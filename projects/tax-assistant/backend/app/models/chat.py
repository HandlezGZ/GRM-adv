import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("tax_documents.id"), nullable=False, index=True)
    title = Column(String(150), default="Consulta Tributária", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    document = relationship("TaxDocument", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    citations = Column(JSON, default=list, nullable=False)  # [{chunk_id, page_number, verbatim_excerpt}]
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    session = relationship("ChatSession", back_populates="messages")
