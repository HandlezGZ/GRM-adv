from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaxDocumentBase(BaseModel):
    filename: str
    document_type: str = "OUTRO"


class TaxDocumentCreate(TaxDocumentBase):
    raw_text: str
    file_size_bytes: int = 0
    total_pages: int = 1
    sha256_hash: str


class DocumentChunkRead(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: int
    content: str
    token_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaxDocumentRead(TaxDocumentBase):
    id: str
    sha256_hash: str
    file_size_bytes: int
    total_pages: int
    raw_text: str
    status: str
    created_at: datetime
    chunks: list[DocumentChunkRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaxDocumentSummaryItem(BaseModel):
    id: str
    filename: str
    document_type: str
    sha256_hash: str
    file_size_bytes: int
    total_pages: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
