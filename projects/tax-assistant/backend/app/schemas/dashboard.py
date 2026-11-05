from pydantic import BaseModel, Field


class DashboardMetricsResponse(BaseModel):
    total_documents: int = 0
    total_tax_amount: float = 0.0
    total_pages_analyzed: int = 0
    documents_by_type: dict[str, int] = Field(default_factory=dict)
    taxes_distribution: dict[str, int] = Field(default_factory=dict)
    average_confidence_score: float = 0.0
