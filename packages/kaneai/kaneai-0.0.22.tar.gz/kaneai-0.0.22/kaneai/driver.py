from .utils import (
    vision_query,
    execute_js,
    lambda_hooks,
    perform_assertion,
)
from .actions import ui_action, logger
from .config import get_metadata, operations_meta_data


class KaneAIDriver:
    """Wrapper around Selenium WebDriver to provide simplified KaneAI functionality"""

    def __init__(self, driver):
        self._driver = driver
        self._operation_map = {}

    def __getattr__(self, attr):
        """Delegate any unknown attributes to the underlying WebDriver"""
        return getattr(self._driver, attr)

    def execute(self, intent: str):
        """Execute a KaneAI action with logging"""
        logger.info(f"Executing intent: {intent}")

        operation_index = self._find_operation_by_intent(intent)
        logger.info(f"Found operation index: {operation_index}")

        operation = operations_meta_data.get_operation(operation_index)
        if not operation:
            logger.error(f"No operation data found for index: {operation_index}")
            raise ValueError(f"No operation data found for index: {operation_index}")

        logger.info(f"Operation type: {operation.get('operation_type')}")

        # Execute the operation
        lambda_hooks(self._driver, intent)
        return ui_action(driver=self._driver, operation_index=operation_index)

    def query(self, intent: str) -> str:
        """Execute a KaneAI vision query with logging"""
        operation_index = self._find_operation_by_intent(intent)
        lambda_hooks(self._driver, intent)
        return vision_query(driver=self._driver, operation_index=operation_index)

    def assert_equals(self, actual, expected, message=None):
        """Assert that two values are equal"""
        assert actual == expected, message or f"Expected {expected}, but got {actual}"

    def assert_true(self, condition, message=None):
        """Assert that a condition is True"""
        assert condition, message or "Expected condition to be True"

    def assert_false(self, condition, message=None):
        """Assert that a condition is False"""
        assert not condition, message or "Expected condition to be False"

    def assert_visible(self, element_query: str):
        """Assert that an element is visible"""
        result = self.query(element_query)
        assert str(result).lower() == "true", f"Element '{element_query}' is not visible"

    def assert_contains(self, text: str, substring: str):
        """Assert that text contains substring"""
        assert substring in text, f"Expected '{text}' to contain '{substring}'"

    def reset_module_state(self):
        """Reset the processed operations"""
        operations_meta_data.reset_processed_operations()
        logger.info("Reset operation state")

    def _find_operation_by_intent(self, intent: str) -> str:
        """Find operation index from intent string in flattened metadata"""
        metadata = get_metadata()
        logger.info(f"Looking for intent: {intent}")

        if not isinstance(metadata, dict):
            logger.error("Metadata is not a dictionary")
            raise ValueError("Invalid metadata structure")

        # Create a list of operations with their indices and source info
        operations = [
            {
                "index": idx,
                "intent": op.get("operation_intent", ""),
                "type": op.get("operation_type", ""),
                "source": op.get("_source", "main_flow"),
                "module": op.get("_module_id", "")
            }
            for idx, op in metadata.items()
            if isinstance(op, dict) and "operation_intent" in op
        ]

        # Log available operations grouped by source
        sources = {}
        for op in operations:
            if op["source"] not in sources:
                sources[op["source"]] = []
            sources[op["source"]].append({"intent": op["intent"], "type": op["type"]})

        for source, ops in sources.items():
            logger.info(f"Operations in {source}:")
            for op in ops:
                logger.info(f"  - {op['intent']} ({op['type']})")

        # Find matching operation
        normalized_intent = intent.lower().replace('"', "'").strip()
        logger.info(f"Looking for normalized intent: {normalized_intent}")

        for op in operations:
            normalized_metadata_intent = op["intent"].lower().replace('"', "'").strip()
            if normalized_metadata_intent == normalized_intent:
                logger.info(f"Found matching operation: index={op['index']}, type={op['type']}, source={op['source']}")
                if op["module"]:
                    logger.info(f"Operation is from module: {op['module']}")
                return op["index"]

        # Log detailed error if no match found
        logger.error(f"No operation found matching intent: {intent}")
        logger.error("Available operations by source:")
        for source, ops in sources.items():
            logger.error(f"  {source}:")
            for op in ops:
                logger.error(f"    - {op['intent']} ({op['type']})")
        raise ValueError(f"No operation found matching intent: {intent}")