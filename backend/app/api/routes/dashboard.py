from backend.app.api.deps import get_request_repo
from backend.app.api.schemas.dashboard import DashboardMetrics
from backend.app.repositories.request_repo import RequestRepository
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Obter indicadores e métricas consolidadas para o dashboard",
)
def get_metrics(
    repo: RequestRepository = Depends(get_request_repo),
):
    data = repo.get_dashboard_metrics()
    return DashboardMetrics(**data)
