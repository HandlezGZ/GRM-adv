from datetime import datetime

from backend.app.models.enums import RequestCategory, RequestPriority
from pydantic import BaseModel, Field, field_validator


class RequestCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=5,
        max_length=120,
        description="Título objetivo da solicitação",
        examples=["Acesso a ferramenta de pesquisa jurisprudencial"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descrição detalhada da necessidade operacional",
        examples=["Necessito de login na plataforma jurídica para apoio."],
    )
    category: RequestCategory | None = Field(
        None, description="Categoria opcional informada pelo solicitante"
    )
    priority: RequestPriority = Field(
        default=RequestPriority.NORMAL,
        description="Prioridade da solicitação (padrão: NORMAL)",
    )
    department: str | None = Field(
        None, max_length=100, description="Departamento solicitante"
    )
    requester_name: str | None = Field(
        None,
        max_length=100,
        description="Nome fictício ou identificador do solicitante",
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("O campo não pode ser vazio ou conter apenas espaços.")
            return stripped
        return v


class RequestResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str | None = None
    priority: str
    team: str | None = None
    status: str
    department: str | None = None
    requester_name: str | None = None
    classification_source: str | None = None
    classification_confidence: float | None = None
    classification_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}


class RequestListResponse(BaseModel):
    items: list[RequestResponse]
    total: int
