from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, TypeAlias


class LLMClientError(Exception):
    """General exception for LLM client errors."""

    pass


class LLMConnectionError(LLMClientError):
    """Raised when an LLM connection error occurs."""

    pass


LLMOptions: TypeAlias = Dict[str, str]


@dataclass
class TokenUsage:
    def __init__(self, input_tokens: int, completion_tokens: int, total_tokens: int):
        self.input_tokens = input_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


@dataclass
class LLMResponse:
    completion: str
    tokens: TokenUsage
    llm_options: dict


class LLMClient(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the LLM provider."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """
        Check if connection to LLM provider is working.

        Raises:
            LLMConnectionError: If connection check fails
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, llm_opts: LLMOptions) -> LLMResponse:
        """Generate text using the LLM."""
        pass

    @abstractmethod
    def get_embeddings(self, text: str) -> list[float]:
        """Get embeddings for the given text."""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for the LLM."""
        pass

    @abstractmethod
    def calculate_cost(self, tokens: TokenUsage, model_name: str) -> float:
        """Calculate the cost of generating text using the LLM."""
        pass
