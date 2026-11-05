from datetime import datetime

from backend.app.models.enums import EventActor, RequestStatus
from pydantic import BaseModel, Field


class StatusUpdatePayload(BaseModel):
    new_status: RequestStatus = Field(..., description="Novo status desejado")
    reason: str | None = Field(
        None, max_length=255, description="Motivo da alteração de status"
    )
    actor: EventActor = Field(
        default=EventActor.DEMO_USER,
        description="Ator responsável pela mudança",
    )


class EventResponse(BaseModel):
    id: str
    request_id: str
    event_type: str
    actor: str
    summary: str
    metadata_json: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
