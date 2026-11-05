from typing import Any, Optional

from sqlalchemy.orm import Session

from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import FailureCatalogItem


class FailureCatalogService:
    """Service to audit, categorize, and query AI generation failures and hallucinations."""

    def __init__(self, db: Session):
        self.repo = EvalRepository(db)

    def get_failure_catalog(
        self,
        dataset_id: Optional[str] = None,
        run_id: Optional[str] = None,
        reason: Optional[str] = None,
        limit: int = 100,
    ) -> list[FailureCatalogItem]:
        failed_results = self.repo.list_failures(
            dataset_id=dataset_id,
            run_id=run_id,
            reason=reason,
            limit=limit,
        )

        catalog_items = []
        for res in failed_results:
            test_case = res.test_case
            eval_run = res.eval_run
            dataset_name = (
                eval_run.dataset.name if eval_run and eval_run.dataset else "Unknown Dataset"
            )
            model_name = eval_run.model_name if eval_run else "Unknown Model"

            title = test_case.title if test_case else "Unknown Test Case"
            expected_output = test_case.expected_output if test_case else ""
            context_doc = test_case.context_document if test_case else ""
            context_snippet = context_doc[:250] + "..." if len(context_doc) > 250 else context_doc

            catalog_items.append(
                FailureCatalogItem(
                    id=res.id,
                    run_id=res.run_id,
                    test_case_id=res.test_case_id,
                    test_case_title=title,
                    dataset_name=dataset_name,
                    model_name=model_name,
                    failure_reason=res.failure_reason or "UNSPECIFIED_FAILURE",
                    faithfulness_score=res.faithfulness_score,
                    relevance_score=res.relevance_score,
                    schema_score=res.schema_score,
                    generated_output=res.generated_output,
                    expected_output=expected_output,
                    context_snippet=context_snippet,
                    diagnostics=res.diagnostics or {},
                    created_at=res.created_at,
                )
            )

        return catalog_items

    def get_failure_summary(self, dataset_id: Optional[str] = None) -> dict[str, Any]:
        """Provides analytical breakdown of failures by category and root cause."""
        items = self.get_failure_catalog(dataset_id=dataset_id, limit=500)

        by_reason: dict[str, int] = {}
        by_test_case: dict[str, int] = {}
        by_model: dict[str, int] = {}

        for item in items:
            by_reason[item.failure_reason] = by_reason.get(item.failure_reason, 0) + 1
            by_test_case[item.test_case_title] = by_test_case.get(item.test_case_title, 0) + 1
            by_model[item.model_name] = by_model.get(item.model_name, 0) + 1

        top_fragile_cases = sorted(by_test_case.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_failures_cataloged": len(items),
            "breakdown_by_reason": by_reason,
            "breakdown_by_model": by_model,
            "top_fragile_cases": [{"title": title, "count": cnt} for title, cnt in top_fragile_cases],
        }
