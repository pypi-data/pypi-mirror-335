"""
This module provides a wrapper class for interacting with an Azure CosmosDB container.
It simplifies common operations such as querying, inserting, updating, and deleting items
within a specified CosmosDB container.

The CosmosDBContainer class uses either an endpoint and key or a connection string for
authentication, and provides methods to run queries and perform CRUD operations.
"""

from azure.cosmos import CosmosClient
import logging
import os

logger = logging.getLogger("mpf-utils.cosmosdb")


class CosmosDBContainer:
    """
    A client for interacting with a specific CosmosDB container.

    This class provides methods to run queries, delete, upsert, retrieve a single item,
    or retrieve all items from a container in a CosmosDB database.
    """

    def __init__(self, database_name: str, container_name: str, endpoint: str = None, key: str = None, conn_str: str = None):
        """
        Initialize the CosmosDBContainer.

        Parameters:
            database_name (str): The name of the CosmosDB database.
            container_name (str): The name of the container within the database.
            endpoint (str, optional): The CosmosDB endpoint URL. If not provided, the environment variable 'MPFU_COSMOSDB_ENDPOINT' is used.
            key (str, optional): The primary key for the CosmosDB account. If not provided, the environment variable 'MPFU_COSMOSDB_KEY' is used.
            conn_str (str, optional): A connection string for CosmosDB. If provided, it takes precedence over the endpoint and key.

        Notes:
            - If neither endpoint nor key are provided, the constructor attempts to load them from the environment.
            - The connection string, if provided, will override the endpoint and key.
        """
        if not endpoint:
            endpoint = os.getenv("MPFU_COSMOSDB_ENDPOINT")
        
        if not key:
            key = os.getenv("MPFU_COSMOSDB_KEY")

        if conn_str:
            logger.info("Using connection string to connect to CosmosDB")
            client = CosmosClient.from_connection_string(conn_str)
        else:
            logger.info("Using endpoint and key to connect to CosmosDB")
            client = CosmosClient(endpoint, key)

        database = client.get_database_client(database_name)
        self.container = database.get_container_client(container_name)

    def run_query(self, query: str, parameters: list = None, results_as_list: bool = True):
        """
        Run a query against the CosmosDB container.

        Parameters:
            query (str): The SQL query string to execute.
            parameters (list, optional): A list of parameters to be used with the query.
                Defaults to an empty list if not provided.
            results_as_list (bool, optional): Determines whether the results should be returned as a list.
                If False, an iterable is returned. Defaults to True.

        Returns:
            list or iterator: The query results as a list if results_as_list is True; otherwise, an iterator.
            Returns None if an error occurs during the query.

        Notes:
            - The query is executed with cross-partition querying enabled.
        """
        if not parameters:
            parameters = []

        try:
            items = self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
            if results_as_list:
                return list(items)
            else:
                return items
        except Exception as e:
            logger.error(f"Error in CosmosDBContainer: {e}")
            raise e

    def delete_item(self, item_id: str, partition_key: str = None):
        """
        Delete an item from the CosmosDB container.

        Parameters:
            item_id (str): The unique identifier of the item to delete.
            partition_key (str, optional): The partition key for the item.
                If not provided, the item_id is used as the partition key.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if not partition_key:
            partition_key = item_id
        try:
            self.container.delete_item(item=item_id, partition_key=partition_key)
            return True
        except Exception as e:
            logger.error(f"Error in CosmosDBContainer: {e}")
            raise e


    def upsert_item(self, item: dict):
        """
        Upsert (update or insert) an item in the CosmosDB container.

        Parameters:
            item (dict): A dictionary representing the item to upsert.

        Returns:
            bool: True if the upsert operation was successful, False otherwise.
        """
        try:
            self.container.upsert_item(item)
            return True
        except Exception as e:
            logger.error(f"Error in CosmosDBContainer: {e}")
            raise e

    def get_item(self, item_id: str, partition_key: str = None):
        """
        Retrieve a single item from the CosmosDB container.

        Parameters:
            item_id (str): The unique identifier of the item to retrieve.
            partition_key (str, optional): The partition key for the item.
                If not provided, the item_id is used as the partition key.

        Returns:
            dict: The retrieved item as a dictionary if found.
            Returns None if an error occurs or the item is not found.
        """
        if not partition_key:
            partition_key = item_id
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            return item      
        except Exception as e:
            if "(NotFound)" in str(e):
                logger.info(f"Item with ID {item_id} not found in CosmosDBContainer.")
                return None
            else:
                logger.error(f"Error in CosmosDBContainer: {e}")
                raise e

    def get_all_items(self, max_item_count: int = None, results_as_list: bool = True):
        """
        Retrieve all items from the CosmosDB container.

        Parameters:
            max_item_count (int, optional): The maximum number of items to retrieve.
                Currently, this parameter is not used by the underlying API call.
            results_as_list (bool, optional): Determines whether the results should be returned as a list.
                If False, an iterable is returned. Defaults to True.

        Returns:
            list or iterator: The items in the container as a list if results_as_list is True; otherwise, an iterator.
            Returns None if an error occurs during retrieval.
        """
        try:
            items = self.container.read_all_items()
            if results_as_list:
                return list(items)
            else:
                return items
        except Exception as e:
            logger.error(f"Error in CosmosDBContainer: {e}")
            raise e
            
