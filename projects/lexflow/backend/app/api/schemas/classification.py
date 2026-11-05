from datetime import datetime

from backend.app.models.enums import (
    ClassificationSource,
    RequestCategory,
    RequestPriority,
)
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    category: RequestCategory = Field(..., description="Categoria sugerida")
    team: str = Field(..., description="Equipe sugerida responsável")
    priority: RequestPriority = Field(..., description="Prioridade sugerida")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Nível de confiança heurístico ou estimado"
    )
    reason: str = Field(..., description="Justificativa sucinta da classificação")
    source: ClassificationSource = Field(
        ..., description="Origem da classificação (rules, llm, human)"
    )


class ClassificationResponse(BaseModel):
    request_id: str
    result: ClassificationResult
    fallback_used: bool = False
    warning: str | None = None


class ReviewPayload(BaseModel):
    category: RequestCategory = Field(
        ..., description="Categoria revisada pelo analista"
    )
    team: str = Field(
        ..., min_length=2, max_length=100, description="Equipe confirmada"
    )
    priority: RequestPriority = Field(
        ..., description="Prioridade confirmada pelo analista"
    )
    review_reason: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Justificativa da alteração ou validação humana",
        examples=["Ajustado para TI pois envolve liberação de acesso."],
    )
    reviewer_name: str | None = Field(
        None, max_length=100, description="Nome fictício do analista revisor"
    )


class ClassificationFailureResponse(BaseModel):
    id: str
    request_id: str
    provider: str
    source: str
    error_type: str | None = None
    duration_ms: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
