from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    EvalResultResponse,
    EvalRunCreate,
    EvalRunResponse,
    FailureCatalogItem,
    PromptComparisonResponse,
)
from backend.app.services.benchmark import PromptBenchmarkService
from backend.app.services.diagnostics import FailureCatalogService
from backend.app.services.eval_runner import EvalRunnerService

router = APIRouter(prefix="/eval", tags=["Evaluation"])


def map_run_to_response(run) -> EvalRunResponse:
    results_list = []
    if run.results:
        for r in run.results:
            results_list.append(
                EvalResultResponse(
                    id=r.id,
                    run_id=r.run_id,
                    test_case_id=r.test_case_id,
                    test_case_title=r.test_case.title if r.test_case else None,
                    generated_output=r.generated_output,
                    faithfulness_score=r.faithfulness_score,
                    relevance_score=r.relevance_score,
                    schema_score=r.schema_score,
                    passed=r.passed,
                    failure_reason=r.failure_reason,
                    diagnostics=r.diagnostics or {},
                    duration_ms=r.duration_ms,
                    created_at=r.created_at,
                )
            )

    return EvalRunResponse(
        id=run.id,
        dataset_id=run.dataset_id,
        dataset_name=run.dataset.name if run.dataset else None,
        prompt_version_id=run.prompt_version_id,
        prompt_version_name=run.prompt_version.name if run.prompt_version else None,
        model_name=run.model_name,
        status=run.status,
        total_cases=run.total_cases,
        passed_cases=run.passed_cases,
        pass_rate=run.pass_rate,
        avg_faithfulness=run.avg_faithfulness,
        avg_relevance=run.avg_relevance,
        avg_schema=run.avg_schema,
        duration_ms=run.duration_ms,
        created_at=run.created_at,
        results=results_list,
    )


@router.post("/run", response_model=EvalRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_eval_run(payload: EvalRunCreate, db: Session = Depends(get_db)):
    service = EvalRunnerService(db)
    try:
        run = service.execute_run(payload)
        return map_run_to_response(run)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eval run failed: {str(e)}")


@router.get("/runs", response_model=list[EvalRunResponse])
def list_eval_runs(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    runs = repo.list_eval_runs(limit=limit)
    return [map_run_to_response(r) for r in runs]


@router.get("/runs/{run_id}", response_model=EvalRunResponse)
def get_eval_run(run_id: str, db: Session = Depends(get_db)):
    repo = EvalRepository(db)
    run = repo.get_eval_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Eval run not found")
    return map_run_to_response(run)


@router.get("/compare", response_model=PromptComparisonResponse)
def compare_runs(
    run_a_id: str = Query(..., description="ID of baseline run A"),
    run_b_id: str = Query(..., description="ID of candidate run B"),
    db: Session = Depends(get_db),
):
    service = PromptBenchmarkService(db)
    comparison = service.compare_runs(run_a_id, run_b_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="One or both evaluation runs were not found")
    return comparison


@router.get("/failures", response_model=list[FailureCatalogItem])
def list_failures(
    dataset_id: Optional[str] = None,
    run_id: Optional[str] = None,
    reason: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    service = FailureCatalogService(db)
    return service.get_failure_catalog(
        dataset_id=dataset_id,
        run_id=run_id,
        reason=reason,
        limit=limit,
    )
