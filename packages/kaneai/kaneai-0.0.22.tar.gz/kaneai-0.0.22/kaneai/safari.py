from selenium import webdriver
import sys

safari_script_path = sys.argv[5] if len(sys.argv) > 5 else "/Users/ltuser/foreman/ltuser/lt_utility.js"

with open(safari_script_path, "r") as f:
    injection = f.read()

def inject_script(driver: webdriver.Safari):
    try:
        driver.execute_script(injection)
    except Exception as e:
        print(f"[Safari Exception]: {str(e)}")
        pass
