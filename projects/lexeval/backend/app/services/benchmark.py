from typing import Optional

from sqlalchemy.orm import Session

from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    PromptComparisonResponse,
    TestCaseComparison,
)


class PromptBenchmarkService:
    """Service to analyze regressions, gains, and performance deltas between two evaluation runs."""

    def __init__(self, db: Session):
        self.repo = EvalRepository(db)

    def compare_runs(self, run_a_id: str, run_b_id: str) -> Optional[PromptComparisonResponse]:
        run_a = self.repo.get_eval_run(run_a_id)
        run_b = self.repo.get_eval_run(run_b_id)

        if not run_a or not run_b:
            return None

        # Build map of test_case_id -> result for run A and run B
        results_a = {r.test_case_id: r for r in run_a.results}
        results_b = {r.test_case_id: r for r in run_b.results}

        all_case_ids = list(set(results_a.keys()).union(set(results_b.keys())))

        comparisons: list[TestCaseComparison] = []
        gains = 0
        regressions = 0
        ties = 0

        for case_id in all_case_ids:
            res_a = results_a.get(case_id)
            res_b = results_b.get(case_id)

            passed_a = res_a.passed if res_a else False
            passed_b = res_b.passed if res_b else False

            faith_a = res_a.faithfulness_score if res_a else 0.0
            faith_b = res_b.faithfulness_score if res_b else 0.0
            delta_faith = round(faith_b - faith_a, 4)

            # Title
            title = "Unknown Case"
            if res_a and res_a.test_case:
                title = res_a.test_case.title
            elif res_b and res_b.test_case:
                title = res_b.test_case.title
            else:
                tc = self.repo.get_test_case(case_id)
                if tc:
                    title = tc.title

            # Status classification
            if not passed_a and passed_b:
                status = "GAIN"
                notes = f"Fixed failure: Run A failed ({res_a.failure_reason if res_a else 'Missing'}), Run B passed."
                gains += 1
            elif passed_a and not passed_b:
                status = "REGRESSION"
                notes = f"New failure introduced: Run B failed with {res_b.failure_reason if res_b else 'Missing'}."
                regressions += 1
            elif delta_faith >= 0.15:
                status = "GAIN"
                notes = f"Faithfulness improved by +{delta_faith * 100:.1f}%."
                gains += 1
            elif delta_faith <= -0.15:
                status = "REGRESSION"
                notes = f"Faithfulness degraded by {delta_faith * 100:.1f}%."
                regressions += 1
            else:
                status = "TIE"
                notes = "Consistent performance across both runs."
                ties += 1

            comparisons.append(
                TestCaseComparison(
                    test_case_id=case_id,
                    title=title,
                    run_a_passed=passed_a,
                    run_b_passed=passed_b,
                    run_a_faithfulness=faith_a,
                    run_b_faithfulness=faith_b,
                    status=status,
                    delta_faithfulness=delta_faith,
                    notes=notes,
                )
            )

        pass_rate_delta = round(run_b.pass_rate - run_a.pass_rate, 4)
        faith_delta = round(run_b.avg_faithfulness - run_a.avg_faithfulness, 4)
        rel_delta = round(run_b.avg_relevance - run_a.avg_relevance, 4)

        if regressions == 0 and (gains > 0 or pass_rate_delta > 0):
            verdict = "POSITIVE_PROGRESSION"
        elif regressions > gains or pass_rate_delta < 0:
            verdict = "CRITICAL_REGRESSION"
        elif gains > regressions:
            verdict = "MODERATE_IMPROVEMENT"
        else:
            verdict = "NEUTRAL_EQUIVALENT"

        return PromptComparisonResponse(
            run_a_id=run_a.id,
            run_b_id=run_b.id,
            run_a_model=run_a.model_name,
            run_b_model=run_b.model_name,
            run_a_pass_rate=run_a.pass_rate,
            run_b_pass_rate=run_b.pass_rate,
            pass_rate_delta=pass_rate_delta,
            faithfulness_delta=faith_delta,
            relevance_delta=rel_delta,
            total_cases=len(comparisons),
            gains_count=gains,
            regressions_count=regressions,
            ties_count=ties,
            verdict=verdict,
            comparisons=comparisons,
        )
