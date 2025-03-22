from enum import Enum
from typing import Any, Dict
from pydantic import Field

from zenetics.models.base import BaseSchema


class EvaluationResultState(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestCaseReference(BaseSchema):
    """Reference to a specific test case version"""

    test_case_id: int
    version: int
    name: str


class RunStats(BaseSchema):
    duration: float


class RunTokenUsage(BaseSchema):
    input_tokens: int
    completion_tokens: int
    cost: float


#
# Evaluator Result
#
class EvaluationResultDetails(BaseSchema):
    state: EvaluationResultState
    score: float = Field(..., ge=0, le=1)
    reason: str
    logs: str


class EvaluatorResult(BaseSchema):
    id: int
    name: str
    test_case_ref: TestCaseReference
    threshold: float
    config: Dict[str, Any]
    result: EvaluationResultDetails
    token_usage: RunTokenUsage
    stats: RunStats


#
# TestCase Result
#
class TestCaseResult(BaseSchema):
    name: str
    test_case_ref: TestCaseReference
    actual_output: str
    retrieval_context: list[str]
    status: EvaluationResultState
    token_usage: RunTokenUsage
    stats: RunStats
    evaluations: list[EvaluatorResult]


#
# TestSuite Result
#
class TestSuiteResult(BaseSchema):
    id: int
    name: str
    status: EvaluationResultState
    test_cases: list[TestCaseResult]
    token_usage: RunTokenUsage
    stats: RunStats


#
# TestRun
#
class TestRun(BaseSchema):
    name: str
    token_usage: RunTokenUsage
    stats: RunStats
    test_suites: list[TestSuiteResult]
