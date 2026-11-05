import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class TaxDocument(Base):
    __tablename__ = "tax_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    document_type = Column(String(50), default="OUTRO", nullable=False)
    sha256_hash = Column(String(64), unique=True, index=True, nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    total_pages = Column(Integer, default=1, nullable=False)
    raw_text = Column(Text, nullable=False)
    status = Column(String(30), default="UPLOADED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    extractions = relationship("TaxExtraction", back_populates="document", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="document", cascade="all, delete-orphan")
