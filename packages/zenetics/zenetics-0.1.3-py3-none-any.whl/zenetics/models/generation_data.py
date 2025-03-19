from typing import Dict, List
from pydantic import BaseModel


class TokenUsage(BaseModel):
    """
    Token usage when generating the result of the prompt.
    """

    input_tokens: int
    completion_tokens: int
    total_tokens: int


class Generation(BaseModel):
    """Container for generation output and metadata."""

    output: str
    retrieval_context: List[str] = []
    token_usage: TokenUsage
    metadata: Dict = {}
