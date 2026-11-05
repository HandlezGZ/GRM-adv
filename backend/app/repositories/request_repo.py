import json
from typing import Any

from backend.app.models.classification_attempt import ClassificationAttempt
from backend.app.models.enums import EventActor, EventType, RequestStatus
from backend.app.models.event import RequestEvent
from backend.app.models.request import Request
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class RequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        title: str,
        description: str,
        category: str | None = None,
        priority: str | None = None,
        department: str | None = None,
        requester_name: str | None = None,
        actor: str = EventActor.SYSTEM.value,
    ) -> Request:
        req = Request(
            title=title.strip(),
            description=description.strip(),
            category=category,
            priority=priority or "NORMAL",
            department=department.strip() if department else None,
            requester_name=requester_name.strip() if requester_name else None,
            status=RequestStatus.NEW.value,
        )
        self.db.add(req)
        self.db.flush()

        # Add creation audit event
        self.add_event(
            request_id=req.id,
            event_type=EventType.REQUEST_CREATED.value,
            actor=actor,
            summary=f"Solicitação criada com prioridade {req.priority}",
            metadata={"priority": req.priority, "department": req.department},
        )
        self.db.commit()
        self.db.refresh(req)
        return req

    def get_by_id(self, request_id: str) -> Request | None:
        stmt = select(Request).where(Request.id == request_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_requests(
        self,
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Request]:
        stmt = select(Request).order_by(desc(Request.created_at))

        if status:
            stmt = stmt.where(Request.status == status)
        if category:
            stmt = stmt.where(Request.category == category)
        if priority:
            stmt = stmt.where(Request.priority == priority)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                (Request.title.ilike(pattern)) | (Request.description.ilike(pattern))
            )

        stmt = stmt.limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def update(self, req: Request) -> Request:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def add_event(
        self,
        request_id: str,
        event_type: str,
        actor: str,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> RequestEvent:
        event = RequestEvent(
            request_id=request_id,
            event_type=event_type,
            actor=actor,
            summary=summary,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def get_events(self, request_id: str) -> list[RequestEvent]:
        stmt = (
            select(RequestEvent)
            .where(RequestEvent.request_id == request_id)
            .order_by(RequestEvent.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def record_classification_attempt(
        self,
        request_id: str,
        provider: str,
        source: str,
        success: bool,
        model_name: str | None = None,
        prompt_version: str | None = None,
        error_type: str | None = None,
        duration_ms: float | None = None,
    ) -> ClassificationAttempt:
        attempt = ClassificationAttempt(
            request_id=request_id,
            provider=provider,
            source=source,
            success=success,
            model_name=model_name,
            prompt_version=prompt_version,
            error_type=error_type,
            duration_ms=duration_ms,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def list_failures(self, limit: int = 50) -> list[ClassificationAttempt]:
        stmt = (
            select(ClassificationAttempt)
            .where(ClassificationAttempt.success.is_(False))
            .order_by(desc(ClassificationAttempt.created_at))
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
