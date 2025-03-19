import json
import os
import re
import base64
import time
from pathlib import Path
from urllib.parse import urlparse
import requests
from typing import Dict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from .heal import Heal
from .config import operations_meta_data, get_metadata
from .webdriver_utils import retry_click, conditions_met, lambda_hooks
from datetime import datetime

def get_download_folder():
    """Returns the system's Downloads folder path and ensures it exists."""
    if os.name == "nt":  # Windows
        downloads_path = Path(os.path.join(os.environ["USERPROFILE"], "Downloads"))
    else:  # macOS and Linux
        downloads_path = Path(os.path.expanduser("~/Downloads"))

    # Ensure the folder exists
    downloads_path.mkdir(parents=True, exist_ok=True)

    return downloads_path

def download_files(media_list):
    """Downloads files from the given list to the system's Downloads folder."""
    download_folder = get_download_folder()
    
    for media in media_list:
        file_url = f"https://{media['media_url']}"
        file_name = media['name']
        file_path = download_folder / file_name
        
        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            print(f"Downloaded: {file_name} -> {file_path}")
        except requests.RequestException as e:
            print(f"Failed to download {file_name}: {e}")

def get_downloads_file_path(file_name):
    """Returns the full path to a file in the system's Downloads folder."""
    if file_name is None:
        raise ValueError("file_name cannot be None")
    
    if os.name == "nt":  # Windows
        downloads_path = Path(os.path.join(os.environ["USERPROFILE"], "Downloads"))
    else:  # macOS and Linux
        downloads_path = Path(os.path.expanduser("~/Downloads"))

    return str(downloads_path / file_name)

def get_prev_operation_wait_time(operation_index: str) -> float:
    """Get the wait time between previous operation end and current operation start."""
    wait_time = 0
    try:
        metadata = get_metadata()
        prev_op_index = str(int(operation_index) - 1)
        prev_op_end_time = metadata.get(prev_op_index, {}).get('operation_end', '')
        curr_op_start_time = metadata[operation_index].get('operation_start', '')
        
        if prev_op_end_time and curr_op_start_time:
            # Define the datetime format
            format = "%Y-%m-%d %H:%M:%S.%f"
            
            # Convert strings to datetime objects
            datetime1 = datetime.strptime(prev_op_end_time, format)
            datetime2 = datetime.strptime(curr_op_start_time, format)
            
            # Calculate the difference in seconds
            wait_time = (datetime2 - datetime1).total_seconds()
    except Exception as e:
        print(f"Error getting prev operation wait time: {e}")
    
    return wait_time

def get_operation_wait_time(operation_index: str, default_wait_time: float = 10, max_additional_wait_time: float = 120) -> float:
    """Calculate total wait time for an operation including explicit wait and additional wait based on previous operation."""
    wait_time: float = 0
    try:
        metadata = get_metadata()
        op_data = metadata.get(operation_index, {})
        explicit_wait = float(op_data.get('explicit_wait', 0))
        wait_time = explicit_wait
        
        # Get additional wait time depending on prev operation end time
        additional_wait = default_wait_time
        prev_op_wait_time = get_prev_operation_wait_time(operation_index)
        if prev_op_wait_time > additional_wait:
            additional_wait = prev_op_wait_time
            
        # Limit additional wait time
        additional_wait = min(additional_wait, max_additional_wait_time)
        wait_time += additional_wait
    except Exception as e:
        print(f"Error getting wait time: {e}")
        wait_time += default_wait_time
    
    return wait_time

def access_value(mapping, path):
    """Access a nested value in a mapping using a dot-notation path."""
    try:
        keys = path.split('.')
        value = mapping
        for key in keys:
            while '[' in key and ']' in key:
                base_key, index = key.split('[', 1)
                index = int(index.split(']')[0])
                value = value[base_key] if base_key else value
                value = value[index]
                key = key[key.index(']') + 1:]
            if key:
                value = value[key]

        return str(value)
    except (KeyError, IndexError, ValueError, TypeError):
        return path
    
def get_variable_value(value: str, variables: dict) -> str:
    """Replace variable placeholders in a string with their values."""
    matches = re.findall(r'\{\{(.*?)\}\}', value)
    new_value = value
    if matches:
        for match in matches:
            new_value = new_value.replace("{{"+match+"}}", access_value(variables, match))
    return new_value

def perform_assertion(operand1, operator, operand2, operation_index, intent, driver):
    """Perform assertion with hard assertion support and variable handling."""
    metadata = get_metadata()
    operation_metadata = metadata.get(str(operation_index), {})
    hard_assertion = operation_metadata.get('hard_assertion', False)
    print(f"Performing assertion: '{hard_assertion}'")
    
    # Handle variable substitution from sub_instruction_obj
    sub_instruction_obj = operation_metadata.get('sub_instruction_obj', {})
    if isinstance(sub_instruction_obj, str):
        sub_instruction_obj = json.loads(sub_instruction_obj)
    
    is_string_to_float = operation_metadata.get('string_to_float', False)
    variables = metadata.get('variables', {})
    
    if isinstance(sub_instruction_obj, dict) and 'json' not in operator:
        if 'variable' in sub_instruction_obj:
            if 'operand1' in sub_instruction_obj['variable']:
                new_value = get_variable_value(sub_instruction_obj['variable']['operand1'], variables)
                if is_string_to_float:
                    operand1 = string_to_float(new_value)
                else:
                    operand1 = new_value
            if 'operand2' in sub_instruction_obj['variable']:
                new_value = get_variable_value(sub_instruction_obj['variable']['operand2'], variables)
                if is_string_to_float:
                    operand2 = string_to_float(new_value)
                else:
                    operand2 = new_value

    is_replace = operation_metadata.get('is_replace', False)
    if is_replace:
        operand2 = operation_metadata.get('expected_value')

    # Handle JSON-specific operators first.
    json_ops = {
        "json_key_exists",
        "json_keys_count",
        "json_array_length",
        "json_array_contains",
        "json_value_equals"
    }
    if operator in json_ops:
        if operator == "json_key_exists":
            return operand2 in operand1.keys()
        elif operator == "json_keys_count":
            return len(operand1.keys()) == int(operand2)
        elif operator == "json_array_length":
            return len(operand1) == int(operand2)
        elif operator == "json_array_contains":
            # Match original behavior: return True if found, else None.
            return True if operand2 in operand1 else None
        elif operator == "json_value_equals":
            return operand1 == operand2

    # Map standard operators to their corresponding assertion checks.
    assertion_map = {
        "==": lambda a, b: (a == b, f"Expected {a} to equal {b}"),
        "!=": lambda a, b: (a != b, f"Expected {a} to not equal {b}"),
        "true": lambda a, b: (bool(a) is True, f"Expected true, got {a}"),
        "false": lambda a, b: (bool(a) is False, f"Expected false, got {a}"),
        "is_null": lambda a, b: (a is None, "Expected operand to be None"),
        "not_null": lambda a, b: (a is not None, "Expected operand to be not None"),
        "contains": lambda a, b: (b in a, f"Expected {b} to be in {a}"),
        "not_contains": lambda a, b: (b not in a, f"Expected {b} to not be in {a}"),
        ">": lambda a, b: (a > b, f"Expected {a} to be greater than {b}"),
        "<": lambda a, b: (a < b, f"Expected {a} to be less than {b}"),
        ">=": lambda a, b: (a >= b, f"Expected {a} to be greater than or equal to {b}"),
        "<=": lambda a, b: (a <= b, f"Expected {a} to be less than or equal to {b}"),
        "length_equals": lambda a, b: (len(a) == b, f"Expected length of {a} to be {b}"),
        "type_equals": lambda a, b: (type(a) == b, f"Expected type of {a} to be {b}")
    }

    try:
        # Perform assertion if operator is recognized.
        if operator in assertion_map:
            condition, error_msg = assertion_map[operator](operand1, operand2)
            assert condition, error_msg
        # For unrecognized operators, assume the assertion passes.
        lambda_hooks(driver, f"Assertion passed: '{intent}'")
        return True
    except AssertionError as e:
        lambda_hooks(driver, f"Assertion failed: '{intent}' - {str(e)}")
        print(f"Assertion check failed: '{intent}' - {str(e)}")
        if hard_assertion:
            status = "failed"
            driver.execute_script(f"lambda-status={status}")
            raise e

def handle_unresolved_operations(operation_index, driver):
    """Handle unresolved operations using the Vision Agent"""
    metadata = get_metadata()
    op_data = metadata.get(operation_index, {})
    
    if op_data.get('agent') == "Vision Agent":
        WebDriverWait(driver, 30, poll_frequency=3).until(conditions_met)
        healer = Heal(operation_index, driver)
        response = healer.resolve().json()
        response['locator'] = [response.get('xpath')]
        op_data.update(response)
        operations_meta_data.mark_operation_as_processed(op_data)
        
        # Write updated metadata to file
        with open('operations_meta_data.json', 'w') as f:
            json.dump(metadata, f, indent=4)

def string_to_float(input_string):
    """Convert string to float, handling various formats."""
    if input_string is None:
        return 0
    if isinstance(input_string, (float, int)):
        return float(input_string)
    numeric_string = ''.join(filter(lambda x: x.isdigit() or x == '.', str(input_string)))
    return float(numeric_string) if numeric_string else 0

def heal_query(driver: webdriver, operation_index: str, outer_html: str) -> str:
    """Perform textual query healing."""
    response = Heal(operation_index, driver).textual_query(outer_html)
    response_dict = json.loads(response.text)

    if 'regex' in response_dict:
        regex_pattern = response_dict.get('regex')
        lambda_hooks(driver, "Regex Autohealed ")
        print("REGEX FROM AUTOMIND: ", regex_pattern)
        return regex_pattern
    elif 'error' in response_dict or response.status_code == 500:
        print("Error encountered, retrying...")
    else:
        print("Error in Getting Regex")
        
    return ""

def vision_query(driver: webdriver.Chrome, operation_index: str):
    """Perform vision query with proper error handling."""
    result = None
    metadata = get_metadata()
    op_data = metadata.get(operation_index, {})

    try:
        wait_time = get_operation_wait_time(operation_index)
        if wait_time:
            print(f"Waiting '{wait_time} seconds' before performing vision query....")
            time.sleep(wait_time)

        try:
            WebDriverWait(driver, 30, poll_frequency=3).until(conditions_met)

        except Exception as e:
            print(f"Wait for conditions met failed: {e}")
            print("Continuing with the execution...")

        response = Heal(operation_index, driver).vision_query()
        print("Vision Response: ", response.text)
        response = json.loads(response.text)
            
        if "error" in response:
            raise RuntimeError(f"Error in vision query: {response['error']}")

        result = response['vision_query']

        if op_data.get('string_to_float', False):
            result = string_to_float(result)

    except Exception as e:
        time.sleep(op_data.get('retries_delay', 0))
        if not op_data.get('optional_flag', False):
            raise e
        elif op_data.get('optional_flag', False):
            print(f"Failed to execute visual_query after. Error: {e}")
        print(f"Retrying visual_query due to Error: {str(e)[:50]}....")

    return result

def execute_js(user_js_code: str, driver: webdriver.Chrome) -> dict:
    """Execute JavaScript code with error handling."""
    try:
        lines_before_user_code = 2

        # Wrap the user's code to capture the return value and handle errors
        wrapped_js_code = f"(function() {{ try {{ return (function() {{ {user_js_code} }})(); }} catch(e) {{ e.stack = e.stack.replace(/<anonymous>:(\\d+):/g, function(match, lineNumber) {{ lineNumber = parseInt(lineNumber) - {lines_before_user_code}; return '<anonymous>:' + lineNumber + ':'; }}); return {{error: e.stack}}; }} }})();"

        client_response_js = driver.execute_script("return " + wrapped_js_code)

        if isinstance(client_response_js, dict) and 'error' in client_response_js:
            error_stack = client_response_js['error']
            lines = error_stack.split('\n')
            error_message = lines[0].strip()
            error_line = None

            # Extract the line number from the stack trace
            if len(lines) > 1:
                match = re.search(r'<anonymous>:(\d+):', lines[1])
                if match:
                    error_line = int(match.group(1))

            return {
                'value': '',
                'error': error_message,
                'line': error_line
            }
        else:
            # Successful execution
            try:
                json.dumps(client_response_js)
                if client_response_js is None or client_response_js == '':
                    client_response_js = "null"
                return {
                    'value': client_response_js,
                    'error': '',
                    'line': None
                }
            except (TypeError, OverflowError):
                return {
                    'value': str(client_response_js),
                    'error': '',
                    'line': None
                }
    except Exception as e:
        return {
            'value': '',
            'error': str(e),
            'line': None
        }

def execute_api(driver: webdriver.Chrome, method: str, url: str, headers: dict, body: str, params: dict, timeout: int, verify: bool) -> dict:
    """Execute API request with error handling."""
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return {'status': 400, 'message': 'Invalid URL'}
    if url.startswith(("wss://", "ws://")):
        return {'status': 400, 'message': 'Websockets not supported'}
    if any(value == 'text/event-stream' for value in headers.values()):
        return {'status': 400, 'message': 'SSE not supported'}

    proxies = {"http": "http://127.0.0.1:22000", "https": "http://127.0.0.1:22000"}
    request_methods = {
        "GET": requests.get,
        "POST": requests.post,
        "PUT": requests.put,
        "DELETE": requests.delete,
        "PATCH": requests.patch
    }

    start = time.time()
    try:
        response = request_methods.get(method.upper(), lambda *args, **kwargs: None)(
            url, headers=headers, data=body, params=params, timeout=timeout, proxies=proxies, verify=verify
        )
        if response is None:
            return {'status': 400, 'message': 'Unsupported HTTP method'}
    except requests.RequestException as e:
        return {'status': 400, 'message': f"API request failed: {e}"}
    end = time.time()

    test_api_resp = {
        'status': response.status_code,
        'headers': dict(response.headers),
        'cookies': response.cookies.get_dict(),
        'body': response.content,
        'time': (end - start) * 1000
    }

    for key in list(test_api_resp.keys()):
        try:
            json.dumps(test_api_resp[key])
        except (TypeError, ValueError):
            if isinstance(test_api_resp[key], bytes):
                test_api_resp["response_body"] = [test_api_resp[key].decode('utf-8')]
            test_api_resp[key] = list(test_api_resp[key])
            for i in range(len(test_api_resp[key])):
                try:
                    json.dumps(test_api_resp[key][i])
                except (TypeError, ValueError):
                    test_api_resp[key][i] = str(test_api_resp[key][i])

    return test_api_resp

def replace_secrets(text: str) -> str:
    """Replace secrets using {{secrets.env.VAR}} format."""
    matches = re.findall(r'\{\{(.*?)\}\}', text)
    for match in matches:
        keys = match.split('.')
        if len(keys) == 3 and keys[0] == 'secrets':
            secret_value = os.getenv(keys[2], '')
            text = text.replace(f"{{{{{match}}}}}", secret_value)
    return text

def replace_secrets_in_dict(d: Dict[str, str]) -> Dict[str, str]:
    """Replace secrets in dictionary values."""
    new_dict = {}
    for k, v in d.items():
        replaced_key = replace_secrets(k)
        replaced_value = replace_secrets(v)
        if replaced_key == 'Authorization' and not replaced_value.startswith('Bearer'):
            username = replaced_value.split(':')[0]
            access_key = replaced_value.split(':')[1]
            replaced_value = f"Basic {base64.b64encode(f'{username}:{access_key}'.encode()).decode()}"
        new_dict[replaced_key] = replaced_value
    return new_dict

def replace_variables_in_script(script: str, variables: dict) -> str:
    """Replace variables in JavaScript code."""
    pattern = r'//Variables start.*?//Variables end\n*'
    find_variables = re.findall(pattern, script, re.DOTALL)
    updated_script = script
    if find_variables:
        updated_variables = ""
        for key, value in variables.items():
            if f"const {key} " in find_variables[0]:
                if isinstance(value, str):
                    value = json.dumps(value)
                    updated_variables += f"const {key} = {value};\n"
                else:
                    value = json.dumps(value)
                    updated_variables += f"const {key} = {value};\n"
        updated_script = script.replace(find_variables[0], f"//Variables start\n{updated_variables}//Variables end\n")
    return updated_script
