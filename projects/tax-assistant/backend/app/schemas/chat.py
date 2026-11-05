from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CitationItem(BaseModel):
    chunk_id: str
    page_number: int
    verbatim_excerpt: str
    relevance_score: float = 1.0


class ChatMessageRead(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: list[CitationItem] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionCreate(BaseModel):
    document_id: str
    title: str = "Consulta Tributária"


class ChatSessionRead(BaseModel):
    id: str
    document_id: str
    title: str
    created_at: datetime
    messages: list[ChatMessageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ChatQueryRequest(BaseModel):
    question: str


class ChatQueryResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    citations: list[CitationItem] = Field(default_factory=list)
    is_grounded: bool = True
