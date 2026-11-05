from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EvalTestCaseBase(BaseModel):
    title: str = Field(..., max_length=150)
    input_query: str
    context_document: str
    expected_output: str
    required_keywords: list[str] = Field(default_factory=list)
    forbidden_terms: list[str] = Field(default_factory=list)


class EvalTestCaseCreate(EvalTestCaseBase):
    pass


class EvalTestCaseResponse(EvalTestCaseBase):
    id: str
    dataset_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class EvalDatasetBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category: str = Field(default="TRIBUTARIO", max_length=50)


class EvalDatasetCreate(EvalDatasetBase):
    pass


class EvalDatasetResponse(EvalDatasetBase):
    id: str
    created_at: datetime
    test_cases_count: Optional[int] = 0

    class Config:
        from_attributes = True


class PromptVersionBase(BaseModel):
    name: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    system_prompt: str
    template_text: str
    temperature: float = 0.1


class PromptVersionCreate(PromptVersionBase):
    pass


class PromptVersionResponse(PromptVersionBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class EvalResultResponse(BaseModel):
    id: str
    run_id: str
    test_case_id: str
    test_case_title: Optional[str] = None
    generated_output: str
    faithfulness_score: float
    relevance_score: float
    schema_score: float
    passed: bool
    failure_reason: Optional[str] = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


class EvalRunCreate(BaseModel):
    dataset_id: str
    prompt_version_id: Optional[str] = None
    model_name: str = "rule-evaluator-v1"
    evaluator_type: str = "hybrid"  # "deterministic", "heuristic", "hybrid", "llm"
    threshold: float = 0.70
    custom_outputs: Optional[dict[str, str]] = None  # map of test_case_id -> simulated output


class EvalRunResponse(BaseModel):
    id: str
    dataset_id: str
    dataset_name: Optional[str] = None
    prompt_version_id: Optional[str] = None
    prompt_version_name: Optional[str] = None
    model_name: str
    status: str
    total_cases: int
    passed_cases: int
    pass_rate: float
    avg_faithfulness: float
    avg_relevance: float
    avg_schema: float
    duration_ms: float
    created_at: datetime
    results: Optional[list[EvalResultResponse]] = None

    class Config:
        from_attributes = True


class TestCaseComparison(BaseModel):
    test_case_id: str
    title: str
    run_a_passed: bool
    run_b_passed: bool
    run_a_faithfulness: float
    run_b_faithfulness: float
    status: str  # GAIN, REGRESSION, TIE
    delta_faithfulness: float
    notes: str


class PromptComparisonResponse(BaseModel):
    run_a_id: str
    run_b_id: str
    run_a_model: str
    run_b_model: str
    run_a_pass_rate: float
    run_b_pass_rate: float
    pass_rate_delta: float
    faithfulness_delta: float
    relevance_delta: float
    total_cases: int
    gains_count: int
    regressions_count: int
    ties_count: int
    verdict: str
    comparisons: list[TestCaseComparison]


class FailureCatalogItem(BaseModel):
    id: str
    run_id: str
    test_case_id: str
    test_case_title: str
    dataset_name: str
    model_name: str
    failure_reason: str
    faithfulness_score: float
    relevance_score: float
    schema_score: float
    generated_output: str
    expected_output: str
    context_snippet: str
    diagnostics: dict[str, Any]
    created_at: datetime


class DashboardMetricsResponse(BaseModel):
    total_runs: int
    total_cases_evaluated: int
    avg_pass_rate: float
    avg_faithfulness: float
    avg_relevance: float
    total_failures: int
    failures_by_reason: dict[str, int]
    recent_runs: list[EvalRunResponse]
