from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    EvalDatasetCreate,
    EvalDatasetResponse,
    EvalTestCaseCreate,
    EvalTestCaseResponse,
)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("", response_model=EvalDatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: EvalDatasetCreate, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    dataset = repo.create_dataset(payload)
    return EvalDatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        category=dataset.category,
        created_at=dataset.created_at,
        test_cases_count=0,
    )


@router.get("", response_model=list[EvalDatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    datasets = repo.list_datasets()
    result = []
    for d in datasets:
        result.append(
            EvalDatasetResponse(
                id=d.id,
                name=d.name,
                description=d.description,
                category=d.category,
                created_at=d.created_at,
                test_cases_count=len(d.test_cases),
            )
        )
    return result


@router.get("/{dataset_id}", response_model=EvalDatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    dataset = repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return EvalDatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        category=dataset.category,
        created_at=dataset.created_at,
        test_cases_count=len(dataset.test_cases),
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    deleted = repo.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return None


@router.get("/{dataset_id}/cases", response_model=list[EvalTestCaseResponse])
def list_dataset_cases(dataset_id: str, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    dataset = repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return repo.list_test_cases(dataset_id)


@router.post("/{dataset_id}/cases", response_model=EvalTestCaseResponse, status_code=status.HTTP_201_CREATED)
def create_test_case(dataset_id: str, payload: EvalTestCaseCreate, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    dataset = repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    case = repo.create_test_case(dataset_id, payload)
    return case
