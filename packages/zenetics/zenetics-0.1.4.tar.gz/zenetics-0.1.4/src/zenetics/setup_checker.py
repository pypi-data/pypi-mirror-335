from zenetics.api.zenetics_api_client import ZeneticsAPIClient
from zenetics.llm.providers.openai import OpenAIClient


class SetupChecker:
    """
    This class is responsible for checking the connection to all required services.
    """

    def __init__(
        self, zenetics_api_client: ZeneticsAPIClient, openai_client: OpenAIClient
    ) -> None:
        self.zenetics_api_client = zenetics_api_client
        self.llm_client = openai_client

    def check_zenetics_api_connection(self) -> bool:
        """
        Check the connection to the Zenetics API.
        """
        return self.zenetics_api_client.check_connection()

    def check_llm_connection(self) -> bool:
        """
        Check the connection to the selected LLM Provider API.
        """
        return self.llm_client.check_connection()
