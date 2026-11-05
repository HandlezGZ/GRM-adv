from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.tax_document_repository import TaxDocumentRepository
from backend.app.schemas.dashboard import DashboardMetricsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    repo = TaxDocumentRepository(db)
    metrics_dict = repo.get_metrics()
    return DashboardMetricsResponse(**metrics_dict)
