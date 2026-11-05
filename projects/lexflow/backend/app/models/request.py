from datetime import datetime
from typing import TYPE_CHECKING

from backend.app.db.base import Base, generate_uuid, utc_now
from backend.app.models.enums import RequestPriority, RequestStatus
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from backend.app.models.classification_attempt import ClassificationAttempt
    from backend.app.models.event import RequestEvent


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=RequestPriority.NORMAL.value, index=True
    )
    team: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=RequestStatus.NEW.value, index=True
    )

    department: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    requester_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )

    classification_source: Mapped[str | None] = mapped_column(
        String(30), nullable=True, default=None
    )
    classification_confidence: Mapped[float | None] = mapped_column(
        Float, nullable=True, default=None
    )
    classification_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # Relationships
    events: Mapped[list["RequestEvent"]] = relationship(
        "RequestEvent",
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="RequestEvent.created_at.asc()",
    )
    classification_attempts: Mapped[list["ClassificationAttempt"]] = relationship(
        "ClassificationAttempt",
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="ClassificationAttempt.created_at.desc()",
    )
