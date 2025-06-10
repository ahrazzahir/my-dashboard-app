import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
BLOB_CONTAINER_NAME = "dashboard-assets"
LOCAL_IMAGE_PATH = "company_logo.png"  # Make sure this file exists in the same directory
BLOB_NAME = os.path.basename(LOCAL_IMAGE_PATH)

def upload_logo_to_blob():
    try:
        # Get connection string from environment variable
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable not set.")

        print("Attempting to connect to Azure Blob Storage...")
        blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(connection_string)

        # Create a BlobContainerClient
        container_client: ContainerClient = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

        # Create the container if it doesn't exist
        try:
            print(f"Creating container '{BLOB_CONTAINER_NAME}' if it does not exist...")
            container_client.create_container()
            print(f"Container '{BLOB_CONTAINER_NAME}' created successfully.")
        except ResourceExistsError:
            print(f"Container '{BLOB_CONTAINER_NAME}' already exists. Skipping creation.")
        except Exception as e:
            print(f"An unexpected error occurred while creating container: {e}")
            return

        # Upload the image
        blob_client: BlobClient = container_client.get_blob_client(BLOB_NAME)

        if not os.path.exists(LOCAL_IMAGE_PATH):
            raise FileNotFoundError(f"Local image file not found at: {LOCAL_IMAGE_PATH}")

        print(f"Uploading '{LOCAL_IMAGE_PATH}' as '{BLOB_NAME}' to container '{BLOB_CONTAINER_NAME}'...")
        with open(LOCAL_IMAGE_PATH, "rb") as data:
            blob_client.upload_blob(data, overwrite=True) # overwrite=True allows re-uploading
        print(f"Successfully uploaded '{BLOB_NAME}' to '{BLOB_CONTAINER_NAME}'.")


    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Error: {fnfe}")
    except ResourceNotFoundError:
        print("Error: Storage account or container not found. Check connection string and names.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    upload_logo_to_blob()