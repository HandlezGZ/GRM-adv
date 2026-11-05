from backend.app.api.deps import (
    get_classification_manager,
    get_request_repo,
    get_workflow_service,
)
from backend.app.api.schemas.classification import (
    ClassificationResponse,
    ReviewPayload,
)
from backend.app.api.schemas.event import EventResponse, StatusUpdatePayload
from backend.app.api.schemas.request import (
    RequestCreate,
    RequestListResponse,
    RequestResponse,
)
from backend.app.models.enums import (
    ClassificationSource,
    EventActor,
    EventType,
    RequestCategory,
    RequestPriority,
    RequestStatus,
)
from backend.app.repositories.request_repo import RequestRepository
from backend.app.services.classification.manager import ClassificationManager
from backend.app.services.workflow import InvalidStatusTransitionError, WorkflowService
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova solicitação",
)
@router.post(
    "/",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_request(
    payload: RequestCreate,
    repo: RequestRepository = Depends(get_request_repo),
):
    req = repo.create(
        title=payload.title,
        description=payload.description,
        category=payload.category.value if payload.category else None,
        priority=payload.priority.value,
        department=payload.department,
        requester_name=payload.requester_name,
        actor=EventActor.DEMO_USER.value,
    )
    return req


@router.get(
    "",
    response_model=RequestListResponse,
    summary="Listar e filtrar solicitações",
)
@router.get(
    "/",
    response_model=RequestListResponse,
    include_in_schema=False,
)
def list_requests(
    status_filter: RequestStatus | None = Query(
        None, alias="status", description="Filtrar por status"
    ),
    category_filter: RequestCategory | None = Query(
        None, alias="category", description="Filtrar por categoria"
    ),
    priority_filter: RequestPriority | None = Query(
        None, alias="priority", description="Filtrar por prioridade"
    ),
    search: str | None = Query(
        None, min_length=2, max_length=50, description="Busca textual"
    ),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    repo: RequestRepository = Depends(get_request_repo),
):
    items = repo.list_requests(
        status=status_filter.value if status_filter else None,
        category=category_filter.value if category_filter else None,
        priority=priority_filter.value if priority_filter else None,
        search=search,
        limit=limit,
        offset=offset,
    )
    return RequestListResponse(items=items, total=len(items))


@router.get(
    "/{request_id}",
    response_model=RequestResponse,
    summary="Obter detalhes de uma solicitação por ID",
)
def get_request_details(
    request_id: str,
    repo: RequestRepository = Depends(get_request_repo),
):
    req = repo.get_by_id(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação com ID '{request_id}' não encontrada.",
        )
    return req


@router.post(
    "/{request_id}/classify",
    response_model=ClassificationResponse,
    summary="Executar classificação automática da solicitação",
)
def classify_request(
    request_id: str,
    repo: RequestRepository = Depends(get_request_repo),
    manager: ClassificationManager = Depends(get_classification_manager),
):
    req = repo.get_by_id(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação com ID '{request_id}' não encontrada.",
        )
    return manager.classify_request(req)


@router.post(
    "/{request_id}/review",
    response_model=RequestResponse,
    summary="Revisar e confirmar classificação humana da solicitação",
)
def review_request_classification(
    request_id: str,
    payload: ReviewPayload,
    repo: RequestRepository = Depends(get_request_repo),
):
    req = repo.get_by_id(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação com ID '{request_id}' não encontrada.",
        )

    old_category = req.category
    old_team = req.team
    old_priority = req.priority

    # Apply human changes
    req.category = payload.category.value
    req.team = payload.team.strip()
    req.priority = payload.priority.value
    req.classification_source = ClassificationSource.HUMAN.value
    req.classification_confidence = 1.0
    req.classification_reason = payload.review_reason.strip()

    # If still NEW, advance to TRIAGE
    if req.status == RequestStatus.NEW.value:
        req.status = RequestStatus.TRIAGE.value

    reviewer = payload.reviewer_name or "Analista de Triagem"
    summary_text = (
        f"Revisão humana por {reviewer}: {req.category} ({req.team}) "
        f"- Prioridade: {req.priority}"
    )

    repo.add_event(
        request_id=req.id,
        event_type=EventType.CLASSIFICATION_REVIEWED.value,
        actor=EventActor.HUMAN.value,
        summary=summary_text,
        metadata={
            "old_category": old_category,
            "new_category": req.category,
            "old_team": old_team,
            "new_team": req.team,
            "old_priority": old_priority,
            "new_priority": req.priority,
            "review_reason": payload.review_reason,
            "reviewer": reviewer,
        },
    )

    return repo.update(req)


@router.patch(
    "/{request_id}/status",
    response_model=RequestResponse,
    summary="Atualizar status do workflow da solicitação",
)
def update_request_status(
    request_id: str,
    payload: StatusUpdatePayload,
    repo: RequestRepository = Depends(get_request_repo),
    workflow: WorkflowService = Depends(get_workflow_service),
):
    req = repo.get_by_id(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação com ID '{request_id}' não encontrada.",
        )

    try:
        updated = workflow.transition_status(
            request=req,
            new_status=payload.new_status.value,
            reason=payload.reason,
            actor=payload.actor.value,
        )
        return updated
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{request_id}/events",
    response_model=list[EventResponse],
    summary="Listar histórico de eventos e auditoria da solicitação",
)
def get_request_events(
    request_id: str,
    repo: RequestRepository = Depends(get_request_repo),
):
    req = repo.get_by_id(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação com ID '{request_id}' não encontrada.",
        )
    return repo.get_events(request_id)
