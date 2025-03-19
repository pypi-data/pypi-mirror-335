"""
This module provides a client wrapper for interacting with OpenAI's services,
supporting both Azure OpenAI and the standard OpenAI API. Depending on the
configuration, the client can be initialized with an Azure endpoint and key,
or with a standard OpenAI API key. The client offers a method to run a prompt
and retrieve the generated response.
"""

from openai import AzureOpenAI, OpenAI
import logging
import os

logger = logging.getLogger("mpf-utils.ai")


class OpenAIClient:
    """
    A client for interacting with OpenAI's API, supporting both Azure OpenAI and the standard OpenAI service.

    Depending on the 'azure' flag, the client is configured to use either Azure's OpenAI endpoint
    and API key or the standard OpenAI API key. When using Azure, the client extracts the deployment
    name and API version from the provided endpoint.
    """

    def __init__(
        self,
        azure: bool = True,
        api_key: str = None,
        azure_endpoint: str = None,
        model: str = None,
        azure_openai_api_version: str = "2024-10-21"
    ):
        """
        Initialize the OpenAIClient.

        Parameters:
            azure (bool): Flag indicating whether to use Azure OpenAI (True) or the standard OpenAI service (False).
            api_key (str, optional): The API key for authentication. For Azure, if not provided, it is fetched from
                the environment variable 'MPFU_AZURE_OPENAI_API_KEY'. For standard OpenAI, it is fetched from
                'MPFU_OPENAI_API_KEY' if not provided.
            azure_endpoint (str, optional): The Azure OpenAI endpoint URL. If not provided, it is fetched from the
                environment variable 'MPFU_AZURE_OPENAI_ENDPOINT'.
            model (str, optional): The model identifier to use when not using Azure. For Azure, the model is derived
                from the deployment information in the endpoint.
            azure_openai_api_version (str, optional): The API version for Azure OpenAI. Defaults to "2024-10-21".

        Notes:
            - When using Azure, the endpoint URL is parsed to extract the deployment name and API version.
            - The Azure configuration takes precedence if the 'azure' flag is set to True.
        """
        self.azure = azure

        if self.azure:
            if not azure_endpoint:
                azure_endpoint = os.getenv("MPFU_AZURE_OPENAI_ENDPOINT")

            if not api_key:
                api_key = os.getenv("MPFU_AZURE_OPENAI_API_KEY")

            # Extract the deployment name from the endpoint (assumes a specific URL structure)
            self.deployment = azure_endpoint.split("/")[-3]
            self.model = self.deployment

            # Extract the API version from the endpoint by splitting on '='
            self.api_version = azure_endpoint.split("=")[-1]

            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=self.api_version,
            )

            logger.info(
                f"Using Azure OpenAI with:\nendpoint {azure_endpoint}\nendpoint model {self.model}\nendpoint api version {self.api_version}"
            )
        else:
            # Using the standard OpenAI service
            if not api_key:
                api_key = os.getenv("MPFU_OPENAI_API_KEY")

            self.model = model
            self.client = OpenAI(api_key=api_key)
            logger.info("Using OpenAI")

    def run_prompt(self, prompt: str, model: str = None) -> str:
        """
        Run a prompt through the OpenAI service and retrieve the generated response.

        Parameters:
            prompt (str): The prompt text to send to the OpenAI service.
            model (str, optional): The model identifier to use. If not provided, the client's default model is used.

        Returns:
            str: The content of the response generated by the AI. Returns None if an error occurs.

        Notes:
            - The method uses the chat completion endpoint, sending the prompt as a user message.
            - In case of an exception, the error is logged and None is returned.
        """
        model = model or self.model
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in AI client: {e}")
            return None
