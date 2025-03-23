import logging
from http.client import HTTPResponse
from io import BytesIO
from typing import Dict

import subsurface
from azure.storage.blob import BlobClient


def push_unstructured_data(unstructured_data: 'subsurface.UnstructuredData', sas: str) -> bool:
    """
    Upload unstructured data to Azure Blob Storage.
    
    Args:
        unstructured_data: The unstructured data to be uploaded
        sas: The Shared Access Signature (SAS) URL for the blob storage
        
    Returns:
        bool: True if upload was successful
        
    Raises:
        ValueError: If there's an error during upload
    """
    logger = logging.getLogger(__name__)


    try:
        # Convert data to binary
        binary_data = unstructured_data.to_binary()

        # Initialize blob client and create data stream
        blob_client = BlobClient.from_blob_url(sas)
        data_stream = BytesIO(binary_data)

        # Upload data to blob storage
        upload_result:dict = blob_client.upload_blob(
            data_stream,
            blob_type="BlockBlob",
            overwrite=True
        )

        logger.info(f"Successfully uploaded blob: {upload_result}")
        return True

    except Exception as e:
        error_message = f"Error uploading data to blob storage: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message) from e
