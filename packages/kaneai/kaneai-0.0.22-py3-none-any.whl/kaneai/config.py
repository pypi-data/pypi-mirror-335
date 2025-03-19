import json
import sys
import os
import logging
from datetime import datetime, timezone  # Added timezone import

# Configure logging
logger = logging.getLogger(__name__)

class OperationsMetaData:
    """
    Manages operations metadata using the Singleton pattern.
    Provides methods to load, access, and search operation metadata.
    """
    _instance = None

    def __init__(self):
        """Private constructor to prevent direct instantiation"""
        if OperationsMetaData._instance:
            raise RuntimeError("OperationsMetaData is a singleton. Use getInstance() instead.")
        
        # Initialize instance variables
        self._metadata = {}  # Original metadata with module structure
        self._flattened_metadata = {"main_flow": {}}  # Flattened version with all operations in main_flow
        self._processed_indices = set()  # Track processed operations
        self._active_node = "main_flow"
        
        # Load initial metadata
        self._load_initial_metadata()
        
        OperationsMetaData._instance = self

    def _flatten_metadata(self):
        """Create flattened version of metadata with all operations in main_flow ordered by global_operation_index"""
        all_ops = []
        
        # Collect all operations
        for node_key, node_data in self._metadata.items():
            if isinstance(node_data, dict):
                for op_idx, op in node_data.items():
                    if isinstance(op, dict) and op.get("operation_intent"):
                        all_ops.append(op)
        
        # Sort by global_operation_index
        all_ops.sort(key=lambda x: x.get("global_operation_index", float('inf')))
        
        # Create flattened metadata
        self._flattened_metadata = {"main_flow": {}}
        for idx, op in enumerate(all_ops):
            self._flattened_metadata["main_flow"][str(idx)] = op

    @staticmethod
    def getInstance():
        """Gets the singleton instance of OperationsMetaData"""
        if not OperationsMetaData._instance:
            OperationsMetaData._instance = OperationsMetaData()
        return OperationsMetaData._instance

    def _load_initial_metadata(self):
        """Load initial metadata from file"""
        test_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_path = os.path.join(test_dir, "operations_meta_data.json")
        
        # Override file path if provided in args
        if len(sys.argv) > 6:
            file_path = sys.argv[6]
            if not file_path.endswith('.json'):
                file_path = f'{file_path}.json'
        
        # Handle HYPER environment
        if os.getenv("HYPER") == "true":
            folder_name = os.path.abspath(__file__).split("/")[-2]
            file_path = f"extracted_hye_files/{folder_name}/operations_meta_data.json"

        try:
            logger.info(f"Loading metadata from: {file_path}")
            with open(file_path, 'r') as f:
                self._metadata = json.load(f)
            
            # Create flattened version
            self._flatten_metadata()
            
            # Start with main_flow as active node
            self._active_node = "main_flow"
            self._processed_indices.clear()
            
            # Check for files to download
            if self._metadata.get('files', None):
                from .utils import download_files
                download_files(self._metadata['files'])
            
            # Check for chrome_options with file downloads
            if self._metadata.get('chrome_options', []):
                chrome_options = self._metadata['chrome_options']
                files_data = []
                for option in chrome_options:
                    if option.get('type', "") == "file":
                        files_data.append({"name": option.get('value', ""), "media_url": option.get('file_url', "")})
                if files_data:
                    from .utils import download_files
                    download_files(files_data)
            
            logger.info(f"Loaded metadata with nodes: {list(self._metadata.keys())}")
            logger.info(f"Flattened metadata has {len(self._flattened_metadata['main_flow'])} operations")
        except FileNotFoundError:
            # Initialize with empty metadata if file doesn't exist
            logger.info("No metadata file found, initializing with empty metadata")
            self._metadata = {"main_flow": {}}
            self._flattened_metadata = {"main_flow": {}}
            self._active_node = "main_flow"
        except Exception as e:
            logger.error(f"Error loading initial metadata: {e}")
            raise

    def loadMetadata(self, data, node_name):
        """
        Loads metadata into the instance
        Args:
            data: The metadata to load
            node_name: Name of the node (e.g., 'main_flow' or module name)
        """
        if not data:
            raise ValueError("Cannot load null or undefined metadata")

        # Store metadata directly
        self._metadata = data
        self._active_node = node_name
        self._processed_indices.clear()

        # Create flattened version
        self._flatten_metadata()

        logger.info(f"Loaded metadata structure: {list(data.keys())}")
        logger.info(f"Flattened metadata has {len(self._flattened_metadata['main_flow'])} operations")

    def get_active_metadata(self):
        """Get the currently active metadata"""
        # Always return flattened metadata's main_flow
        return self._flattened_metadata["main_flow"]

    def get_operation(self, operation_index):
        """Get operation by index from flattened metadata"""
        return self._flattened_metadata["main_flow"].get(str(operation_index))

    def mark_operation_as_processed(self, operation):
        """
        Marks an operation as processed
        Args:
            operation: The operation to mark as processed
        """
        if operation and 'operation_id' in operation:
            self._processed_indices.add(operation['operation_id'])
            logger.info(f"Operation processed - ID: {operation['operation_id']} "
                       f"{operation.get('operation_intent', '')}")

    def reset_processed_operations(self):
        """Resets the processed operations tracking"""
        self._processed_indices.clear()
        logger.info("Reset processed operations")

# Initialize the singleton instance
operations_meta_data = OperationsMetaData.getInstance()

def get_metadata():
    """Get the active metadata from the singleton instance"""
    metadata = operations_meta_data.get_active_metadata()
    
    if not isinstance(metadata, dict):
        logger.error("Metadata is not a dictionary")
        return {}
        
    logger.info(f"Raw metadata keys: {list(metadata.keys())}")
    logger.info(f"Operations in metadata: {[op.get('operation_intent') for op in metadata.values() if isinstance(op, dict)]}")
    
    return metadata

def reload_metadata_root(switch_root="main_flow"):
    """
    Switch to a different metadata root node
    Args:
        switch_root: Name of the node to switch to
    """
    logger.info(f"Reloading metadata root, switching to: {switch_root}")
    
    # Force reload of metadata
    operations_meta_data._load_initial_metadata()
    logger.info("Metadata reloaded")

    # Verify metadata state
    metadata = get_metadata()
    if isinstance(metadata, dict):
        logger.info(f"Metadata loaded successfully with {len(metadata)} operations")
        logger.info(f"Available operations: {[op.get('operation_intent') for op in metadata.values() if isinstance(op, dict)]}")
    else:
        logger.error("Metadata is not in the expected format")