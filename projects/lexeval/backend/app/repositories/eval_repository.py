from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.app.models.eval_models import (
    EvalDataset,
    EvalResult,
    EvalRun,
    EvalTestCase,
    PromptVersion,
)
from backend.app.schemas.eval_schemas import (
    EvalDatasetCreate,
    EvalTestCaseCreate,
    PromptVersionCreate,
)


class EvalRepository:
    def __init__(self, db: Session):
        self.db = db

    # Dataset methods
    def create_dataset(self, data: EvalDatasetCreate) -> EvalDataset:
        dataset = EvalDataset(
            name=data.name,
            description=data.description,
            category=data.category,
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def get_dataset(self, dataset_id: str) -> Optional[EvalDataset]:
        return self.db.query(EvalDataset).filter(EvalDataset.id == dataset_id).first()

    def get_dataset_by_name(self, name: str) -> Optional[EvalDataset]:
        return self.db.query(EvalDataset).filter(EvalDataset.name == name).first()

    def list_datasets(self) -> list[EvalDataset]:
        return self.db.query(EvalDataset).order_by(EvalDataset.created_at.desc()).all()

    def delete_dataset(self, dataset_id: str) -> bool:
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return False
        self.db.delete(dataset)
        self.db.commit()
        return True

    # Test case methods
    def create_test_case(self, dataset_id: str, data: EvalTestCaseCreate) -> EvalTestCase:
        case = EvalTestCase(
            dataset_id=dataset_id,
            title=data.title,
            input_query=data.input_query,
            context_document=data.context_document,
            expected_output=data.expected_output,
            required_keywords=data.required_keywords,
            forbidden_terms=data.forbidden_terms,
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def list_test_cases(self, dataset_id: str) -> list[EvalTestCase]:
        return (
            self.db.query(EvalTestCase)
            .filter(EvalTestCase.dataset_id == dataset_id)
            .order_by(EvalTestCase.created_at.asc())
            .all()
        )

    def get_test_case(self, case_id: str) -> Optional[EvalTestCase]:
        return self.db.query(EvalTestCase).filter(EvalTestCase.id == case_id).first()

    # Prompt version methods
    def create_prompt_version(self, data: PromptVersionCreate) -> PromptVersion:
        prompt = PromptVersion(
            name=data.name,
            version=data.version,
            system_prompt=data.system_prompt,
            template_text=data.template_text,
            temperature=data.temperature,
        )
        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)
        return prompt

    def get_prompt_version(self, prompt_id: str) -> Optional[PromptVersion]:
        return self.db.query(PromptVersion).filter(PromptVersion.id == prompt_id).first()

    def get_prompt_by_name_and_version(self, name: str, version: str) -> Optional[PromptVersion]:
        return (
            self.db.query(PromptVersion)
            .filter(PromptVersion.name == name, PromptVersion.version == version)
            .first()
        )

    def list_prompt_versions(self) -> list[PromptVersion]:
        return self.db.query(PromptVersion).order_by(PromptVersion.created_at.desc()).all()

    # EvalRun methods
    def create_eval_run(
        self,
        dataset_id: str,
        model_name: str,
        prompt_version_id: Optional[str] = None,
        status: str = "RUNNING",
    ) -> EvalRun:
        eval_run = EvalRun(
            dataset_id=dataset_id,
            prompt_version_id=prompt_version_id,
            model_name=model_name,
            status=status,
        )
        self.db.add(eval_run)
        self.db.commit()
        self.db.refresh(eval_run)
        return eval_run

    def update_eval_run_metrics(
        self,
        run_id: str,
        total_cases: int,
        passed_cases: int,
        pass_rate: float,
        avg_faithfulness: float,
        avg_relevance: float,
        avg_schema: float,
        duration_ms: float,
        status: str = "COMPLETED",
    ) -> Optional[EvalRun]:
        run = self.get_eval_run(run_id)
        if not run:
            return None
        run.total_cases = total_cases
        run.passed_cases = passed_cases
        run.pass_rate = pass_rate
        run.avg_faithfulness = avg_faithfulness
        run.avg_relevance = avg_relevance
        run.avg_schema = avg_schema
        run.duration_ms = duration_ms
        run.status = status
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_eval_run(self, run_id: str) -> Optional[EvalRun]:
        return (
            self.db.query(EvalRun)
            .options(joinedload(EvalRun.dataset), joinedload(EvalRun.prompt_version), joinedload(EvalRun.results))
            .filter(EvalRun.id == run_id)
            .first()
        )

    def list_eval_runs(self, limit: int = 50) -> list[EvalRun]:
        return (
            self.db.query(EvalRun)
            .options(joinedload(EvalRun.dataset), joinedload(EvalRun.prompt_version))
            .order_by(EvalRun.created_at.desc())
            .limit(limit)
            .all()
        )

    # EvalResult methods
    def create_eval_result(
        self,
        run_id: str,
        test_case_id: str,
        generated_output: str,
        faithfulness_score: float,
        relevance_score: float,
        schema_score: float,
        passed: bool,
        failure_reason: Optional[str] = None,
        diagnostics: Optional[dict] = None,
        duration_ms: float = 0.0,
    ) -> EvalResult:
        result = EvalResult(
            run_id=run_id,
            test_case_id=test_case_id,
            generated_output=generated_output,
            faithfulness_score=faithfulness_score,
            relevance_score=relevance_score,
            schema_score=schema_score,
            passed=passed,
            failure_reason=failure_reason,
            diagnostics=diagnostics or {},
            duration_ms=duration_ms,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def list_failures(
        self,
        dataset_id: Optional[str] = None,
        run_id: Optional[str] = None,
        reason: Optional[str] = None,
        limit: int = 100,
    ) -> list[EvalResult]:
        query = (
            self.db.query(EvalResult)
            .options(joinedload(EvalResult.test_case), joinedload(EvalResult.eval_run).joinedload(EvalRun.dataset))
            .filter(EvalResult.passed.is_(False))
        )
        if dataset_id:
            query = query.join(EvalTestCase).filter(EvalTestCase.dataset_id == dataset_id)
        if run_id:
            query = query.filter(EvalResult.run_id == run_id)
        if reason:
            query = query.filter(EvalResult.failure_reason == reason)
        return query.order_by(EvalResult.created_at.desc()).limit(limit).all()

    # Dashboard Metrics
    def get_dashboard_metrics(self) -> dict:
        total_runs = self.db.query(func.count(EvalRun.id)).scalar() or 0
        total_cases_evaluated = self.db.query(func.count(EvalResult.id)).scalar() or 0
        avg_pass_rate = self.db.query(func.avg(EvalRun.pass_rate)).scalar() or 0.0
        avg_faithfulness = self.db.query(func.avg(EvalRun.avg_faithfulness)).scalar() or 0.0
        avg_relevance = self.db.query(func.avg(EvalRun.avg_relevance)).scalar() or 0.0

        total_failures = self.db.query(func.count(EvalResult.id)).filter(EvalResult.passed.is_(False)).scalar() or 0

        # Failures by reason
        reason_counts = (
            self.db.query(EvalResult.failure_reason, func.count(EvalResult.id))
            .filter(EvalResult.passed.is_(False))
            .group_by(EvalResult.failure_reason)
            .all()
        )
        failures_by_reason = {
            (reason or "UNSPECIFIED"): count for reason, count in reason_counts
        }

        recent_runs = self.list_eval_runs(limit=10)

        return {
            "total_runs": total_runs,
            "total_cases_evaluated": total_cases_evaluated,
            "avg_pass_rate": round(float(avg_pass_rate), 4),
            "avg_faithfulness": round(float(avg_faithfulness), 4),
            "avg_relevance": round(float(avg_relevance), 4),
            "total_failures": total_failures,
            "failures_by_reason": failures_by_reason,
            "recent_runs": recent_runs,
        }
