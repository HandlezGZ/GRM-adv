from backend.app.api.deps import get_request_repo
from backend.app.api.schemas.classification import ClassificationFailureResponse
from backend.app.repositories.request_repo import RequestRepository
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/classification", tags=["Classification"])


@router.get(
    "/failures",
    response_model=list[ClassificationFailureResponse],
    summary="Listar tentativas com falha de classificação da IA",
)
def list_classification_failures(
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    repo: RequestRepository = Depends(get_request_repo),
):
    return repo.list_failures(limit=limit)
