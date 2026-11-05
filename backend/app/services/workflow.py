from backend.app.db.base import utc_now
from backend.app.models.enums import EventActor, EventType, RequestStatus
from backend.app.models.request import Request
from backend.app.repositories.request_repo import RequestRepository


class InvalidStatusTransitionError(ValueError):
    """Raised when an invalid status transition is attempted."""
    pass


class WorkflowService:
    # Allowed state machine transitions according to RF-05
    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        RequestStatus.NEW.value: {
            RequestStatus.TRIAGE.value,
            RequestStatus.CANCELLED.value,
        },
        RequestStatus.TRIAGE.value: {
            RequestStatus.IN_PROGRESS.value,
            RequestStatus.WAITING.value,
            RequestStatus.CANCELLED.value,
        },
        RequestStatus.IN_PROGRESS.value: {
            RequestStatus.WAITING.value,
            RequestStatus.RESOLVED.value,
            RequestStatus.CANCELLED.value,
        },
        RequestStatus.WAITING.value: {
            RequestStatus.IN_PROGRESS.value,
            RequestStatus.CANCELLED.value,
        },
        RequestStatus.RESOLVED.value: set(),
        RequestStatus.CANCELLED.value: set(),
    }

    def __init__(self, repo: RequestRepository):
        self.repo = repo

    def transition_status(
        self,
        request: Request,
        new_status: str,
        reason: str | None = None,
        actor: str = EventActor.DEMO_USER.value,
    ) -> Request:
        current_status = request.status

        if current_status == new_status:
            return request

        allowed_targets = self.ALLOWED_TRANSITIONS.get(current_status, set())
        if new_status not in allowed_targets:
            targets_str = sorted(list(allowed_targets)) or "nenhuma"
            raise InvalidStatusTransitionError(
                f"Transição inválida de '{current_status}' para '{new_status}'. "
                f"Transições permitidas: {targets_str}."
            )

        old_status = request.status
        request.status = new_status

        # If transitioned to RESOLVED, stamp resolved_at
        if new_status == RequestStatus.RESOLVED.value:
            request.resolved_at = utc_now()
        elif (
            old_status == RequestStatus.RESOLVED.value
            and new_status != RequestStatus.RESOLVED.value
        ):
            request.resolved_at = None

        # Record audit event
        summary = f"Status alterado de {old_status} para {new_status}"
        if reason:
            summary += f": {reason.strip()}"

        self.repo.add_event(
            request_id=request.id,
            event_type=EventType.STATUS_CHANGED.value,
            actor=actor,
            summary=summary,
            metadata={
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
            },
        )

        return self.repo.update(request)
