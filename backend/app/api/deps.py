from backend.app.db.session import get_db
from backend.app.repositories.request_repo import RequestRepository
from backend.app.services.classification.manager import ClassificationManager
from backend.app.services.workflow import WorkflowService
from fastapi import Depends
from sqlalchemy.orm import Session


def get_request_repo(db: Session = Depends(get_db)) -> RequestRepository:
    return RequestRepository(db)


def get_workflow_service(
    repo: RequestRepository = Depends(get_request_repo),
) -> WorkflowService:
    return WorkflowService(repo)


def get_classification_manager(
    repo: RequestRepository = Depends(get_request_repo),
) -> ClassificationManager:
    return ClassificationManager(repo)
