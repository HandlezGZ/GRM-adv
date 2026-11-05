from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    PromptVersionCreate,
    PromptVersionResponse,
)

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.post("", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_version(payload: PromptVersionCreate, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    existing = repo.get_prompt_by_name_and_version(payload.name, payload.version)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt version {payload.name}:{payload.version} already exists",
        )
    return repo.create_prompt_version(payload)


@router.get("", response_model=list[PromptVersionResponse])
def list_prompt_versions(db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    return repo.list_prompt_versions()


@router.get("/{prompt_id}", response_model=PromptVersionResponse)
def get_prompt_version(prompt_id: str, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    prompt = repo.get_prompt_version(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return prompt
