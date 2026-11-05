from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.routes.eval import map_run_to_response
from backend.app.db.session import get_db
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import DashboardMetricsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    raw_metrics = repo.get_dashboard_metrics()

    recent_runs = [map_run_to_response(r) for r in raw_metrics["recent_runs"]]

    return DashboardMetricsResponse(
        total_runs=raw_metrics["total_runs"],
        total_cases_evaluated=raw_metrics["total_cases_evaluated"],
        avg_pass_rate=raw_metrics["avg_pass_rate"],
        avg_faithfulness=raw_metrics["avg_faithfulness"],
        avg_relevance=raw_metrics["avg_relevance"],
        total_failures=raw_metrics["total_failures"],
        failures_by_reason=raw_metrics["failures_by_reason"],
        recent_runs=recent_runs,
    )
