from openai import OpenAI, OpenAIError

from ..llm_client import (
    LLMClient,
    LLMConnectionError,
    LLMOptions,
    LLMResponse,
    TokenUsage,
)


#
class OpenAIClient(LLMClient):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_name(self) -> str:
        return "OpenAI"

    def check_connection(self) -> bool:
        """
        Check if connection to OpenAI API is working.

        Raises:
            LLMConnectionError: If connection check fails
        """
        try:
            # Make a minimal API call to test connection
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )

            # Verify we got a response
            if not response or not response.choices:
                raise LLMConnectionError("No response received from OpenAI API")

            return True

        except OpenAIError as e:
            raise LLMConnectionError(f"Failed to connect to OpenAI API: {str(e)}")
        except Exception as e:
            raise LLMConnectionError(
                f"Unexpected error while connecting to OpenAI API: {str(e)}"
            )

    def generate(self, prompt: str, llm_options: LLMOptions) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=llm_options.get("model", self.get_default_model()),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=llm_options.get("max_tokens", 1000),
                temperature=llm_options.get("temperature", 0.1),
            )
            # Extract token usage information
            usage = response.usage
            res = LLMResponse(
                completion=response.choices[0].message.content,
                tokens=TokenUsage(
                    input_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                ),
                llm_options=llm_options,
            )
        except OpenAIError as e:
            print("LLM Error: ", e)
            raise LLMConnectionError(f"Failed to generate text: {str(e)}")

        return res

    def get_embeddings(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",  # or text-embedding-3-large
            input=text,
            encoding_format="float",
        )
        return response.data[0].embedding

    def calculate_cost(self, tokens: TokenUsage, model_name: str) -> float:
        # Token usage is included in the API response
        prompt_tokens = tokens.input_tokens
        completion_tokens = tokens.completion_tokens

        # per 1M tokens (in USD)
        pricing = {
            "gpt-4o": {"prompt": 2.5, "completion": 10.0},
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.6},
            "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
        }

        if model_name not in pricing:
            print(f"Unknown model: {model_name}")
            raise ValueError(f"Unknown model: {model_name}")

        ONE_MIO = 1000000

        # Calculate cost (converting to price per token)
        prompt_cost = prompt_tokens * (pricing[model_name]["prompt"] / ONE_MIO)
        completion_cost = completion_tokens * (
            pricing[model_name]["completion"] / ONE_MIO
        )
        total_cost = prompt_cost + completion_cost

        return total_cost

    def get_default_model(self) -> str:
        # return "gpt-3.5-turbo"
        # return "gpt-4o-mini"
        return "gpt-4o"
