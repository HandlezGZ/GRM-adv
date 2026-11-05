from backend.app.db.session import get_db
from backend.app.repositories.request_repo import RequestRepository
from fastapi import Depends
from sqlalchemy.orm import Session


def get_request_repo(db: Session = Depends(get_db)) -> RequestRepository:
    return RequestRepository(db)
