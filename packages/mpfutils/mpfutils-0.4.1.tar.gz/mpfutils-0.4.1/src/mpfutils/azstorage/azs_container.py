"""
This module provides a simple wrapper for interacting with Azure Blob Storage containers.
It defines the AzsContainerClient class, which allows you to upload and download blobs
using either a connection string or a SAS URL.
"""

from azure.storage.blob import BlobServiceClient, ContainerClient
import logging
import os

logger = logging.getLogger("mpf-utils.azstorage")


class AzsContainerClient:
    """
    A client for interacting with an Azure Blob Storage container.

    This class allows uploading and downloading blobs from an Azure Storage container.
    It can establish the connection using either a connection string (with a specified container)
    or a SAS (Shared Access Signature) URL.
    """

    def __init__(self, container_name: str = None, conn_str: str = None, sas_url: str = None):
        """
        Initialize the AzsContainerClient.

        Parameters:
            container_name (str, optional): The name of the container. This is required when using a connection string.
            conn_str (str, optional): The connection string for the Azure Storage account.
                If not provided, the connection string will be fetched from the environment variable 'MPFU_AZSTORAGE_CONNECTION_STRING'.
            sas_url (str, optional): The SAS URL for the container. If provided, it overrides the connection string.

        Notes:
            - If neither 'conn_str' nor 'sas_url' is provided, the connection string is obtained from the environment.
            - The SAS URL, if provided, takes precedence over the connection string.
        """
        if not conn_str and not sas_url:
            conn_str = os.getenv("MPFU_AZSTORAGE_CONNECTION_STRING")
        
        if not sas_url:
            logger.info("Using connection string to connect to Azure Storage")
            blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            self.container_client = blob_service_client.get_container_client(container_name)
        else:
            # If a sas_url is provided, it overrides the connection string.
            logger.info("Using SAS URL to connect to Azure Storage")
            self.container_client = ContainerClient.from_container_url(sas_url)
        
    def upload_blob(self, blob_name, data, overwrite=True):
        """
        Upload data to a blob within the container.

        Parameters:
            blob_name (str): The name of the blob to be created or overwritten.
            data (bytes or str): The data to upload to the blob.
            overwrite (bool, optional): Whether to overwrite an existing blob with the same name. Defaults to True.

        Returns:
            str: The URL of the uploaded blob.

        """
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(data, overwrite=overwrite)
        return blob_client.url

    def download_blob(self, blob_name):
        """
        Download the content of a blob from the container.

        Parameters:
            container_name (str): The name of the container. 
                Note: This parameter is currently not used since the container is already specified during initialization.
            blob_name (str): The name of the blob to download.

        Returns:
            bytes: The content of the blob.
        """
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        return blob_client.download_blob().readall()

    def list_blobs(self, prefix=None, include=None):
        """
        List blobs in the container.

        Parameters:
            prefix (str, optional): The prefix to filter blobs by name.
            include (list, optional): Additional properties to include in the listing.

        Returns:
            list: A list of blob names in the container.

        """
        blobs = self.container_client.list_blobs(name_starts_with=prefix, include=include)
        return blobs

    def get_blob_url(self, blob_name):
        """
        Get the URL of a blob in the container.

        Parameters:
            blob_name (str): The name of the blob.

        Returns:
            str: The URL of the blob.
        """
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        return blob_client.url

    def delete_blob(self, blob_name):
        """
        Delete a blob from the container.

        Parameters:
            blob_name (str): The name of the blob to delete.

        Returns:
            None
        """
        blob_client = self.container_client.get_blob_client(blob=blob_name)

        blob_client.delete_blob()


        
