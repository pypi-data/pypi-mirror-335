import os
import hashlib
import json
import logging

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, AzureError
logger = logging.getLogger(__name__)

# Retrieve the connection string from the environment variable
AZURE_BLOB_CONNECTION_STRING = os.environ.get("AZURE_BLOB_CONNECTION_STRING")
if not AZURE_BLOB_CONNECTION_STRING:
    raise ValueError("AZURE_BLOB_CONNECTION_STRING environment variable is not set")

# Define the container name for caching outputs
CONTAINER_NAME = "cacheoutputs"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
logging.getLogger("azure").setLevel(logging.CRITICAL)

# Ensure the container exists (if it already exists, an error is caught and ignored)
try:
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    container_client.create_container()
except AzureError as e:
    # The container might already exist so we ignore the exception
    pass


def cache_output(tool_name: str, key: str, value, ttl: int = None) -> bool:
    """
    Cache the output of a function using Azure Blob Storage.

    Parameters:
        tool_name (str): Name of the tool whose output is being cached.
        key (str): The cache key.
        value (Any): The value to be cached.
        ttl (int, optional): The time-to-live (TTL) for the cached value in seconds.

    Returns:
        bool: True if the value was successfully cached, False otherwise.
    """
    # Create a hash of the key for a consistent blob name
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Construct the blob name using a virtual folder for the tool name.
    # For example: "my_tool/abcdef123456.json"
    blob_name = f"{tool_name}/{key_hash}.json"

    # Prepare the cache data
    cache_data = {
        "value": value,
        "ttl": ttl
    }
    data = json.dumps(cache_data)

    try:
        # Get a blob client for the specific blob
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        # Upload the blob content (overwrite if the blob already exists)
        blob_client.upload_blob(data, overwrite=True)
        return True
    except Exception as e:
        logger.error(f"Error uploading blob '{blob_name}': {e}")
        return False


def retrieve_output(tool_name: str, key: str):
    """
    Retrieve the cached output for a given tool and cache key from Azure Blob Storage.

    Parameters:
        tool_name (str): Name of the tool whose output is being retrieved.
        key (str): The cache key.

    Returns:
        Any: The cached value if found, None otherwise.
    """
    # Create a hash of the key to locate the blob
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Construct the blob name using the tool name folder
    blob_name = f"{tool_name}/{key_hash}.json"

    try:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        download_stream = blob_client.download_blob()
        content = download_stream.readall()  # content is in bytes
        cache_data = json.loads(content.decode("utf-8"))
        return cache_data.get("value")
    except ResourceNotFoundError:
        # Blob does not exist
        logger.info(f"Blob '{blob_name}' not found.")
        return None
    except Exception as e:
        logger.error(f"Error retrieving blob '{blob_name}': {e}")
        return None
