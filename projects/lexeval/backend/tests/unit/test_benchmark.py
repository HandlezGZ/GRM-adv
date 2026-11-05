import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import EvalDatasetCreate, EvalTestCaseCreate
from backend.app.services.benchmark import PromptBenchmarkService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_compare_runs_positive_progression(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="Bench-DS", category="TRIBUTARIO"))

    tc1 = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="Case 1",
            input_query="Query 1",
            context_document="Context 1",
            expected_output="Output 1",
        ),
    )
    tc2 = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="Case 2",
            input_query="Query 2",
            context_document="Context 2",
            expected_output="Output 2",
        ),
    )

    # Run A: tc1 passed, tc2 failed
    run_a = repo.create_eval_run(dataset_id=dataset.id, model_name="model-v1")
    repo.create_eval_result(
        run_id=run_a.id,
        test_case_id=tc1.id,
        generated_output="v1 out 1",
        faithfulness_score=0.9,
        relevance_score=0.9,
        schema_score=1.0,
        passed=True,
    )
    repo.create_eval_result(
        run_id=run_a.id,
        test_case_id=tc2.id,
        generated_output="v1 out 2",
        faithfulness_score=0.4,
        relevance_score=0.5,
        schema_score=1.0,
        passed=False,
        failure_reason="HALLUCINATION",
    )
    repo.update_eval_run_metrics(
        run_id=run_a.id,
        total_cases=2,
        passed_cases=1,
        pass_rate=0.5,
        avg_faithfulness=0.65,
        avg_relevance=0.7,
        avg_schema=1.0,
        duration_ms=20.0,
    )

    # Run B: both passed (tc2 is fixed!)
    run_b = repo.create_eval_run(dataset_id=dataset.id, model_name="model-v2")
    repo.create_eval_result(
        run_id=run_b.id,
        test_case_id=tc1.id,
        generated_output="v2 out 1",
        faithfulness_score=0.92,
        relevance_score=0.9,
        schema_score=1.0,
        passed=True,
    )
    repo.create_eval_result(
        run_id=run_b.id,
        test_case_id=tc2.id,
        generated_output="v2 out 2",
        faithfulness_score=0.95,
        relevance_score=0.92,
        schema_score=1.0,
        passed=True,
    )
    repo.update_eval_run_metrics(
        run_id=run_b.id,
        total_cases=2,
        passed_cases=2,
        pass_rate=1.0,
        avg_faithfulness=0.935,
        avg_relevance=0.91,
        avg_schema=1.0,
        duration_ms=22.0,
    )

    service = PromptBenchmarkService(db_session)
    comp = service.compare_runs(run_a.id, run_b.id)

    assert comp is not None
    assert comp.pass_rate_delta == 0.5
    assert comp.gains_count == 1
    assert comp.regressions_count == 0
    assert comp.ties_count == 1
    assert comp.verdict == "POSITIVE_PROGRESSION"


def test_compare_runs_critical_regression(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="Bench-Regress", category="TRIBUTARIO"))

    tc1 = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="Regression Case",
            input_query="Q",
            context_document="C",
            expected_output="O",
        ),
    )

    # Run A: passed
    run_a = repo.create_eval_run(dataset_id=dataset.id, model_name="model-v1")
    repo.create_eval_result(
        run_id=run_a.id,
        test_case_id=tc1.id,
        generated_output="out 1",
        faithfulness_score=0.95,
        relevance_score=0.95,
        schema_score=1.0,
        passed=True,
    )
    repo.update_eval_run_metrics(
        run_id=run_a.id,
        total_cases=1,
        passed_cases=1,
        pass_rate=1.0,
        avg_faithfulness=0.95,
        avg_relevance=0.95,
        avg_schema=1.0,
        duration_ms=10.0,
    )

    # Run B: failed (regression!)
    run_b = repo.create_eval_run(dataset_id=dataset.id, model_name="model-v2")
    repo.create_eval_result(
        run_id=run_b.id,
        test_case_id=tc1.id,
        generated_output="bad out 2",
        faithfulness_score=0.3,
        relevance_score=0.4,
        schema_score=1.0,
        passed=False,
        failure_reason="HALLUCINATED_CITATION",
    )
    repo.update_eval_run_metrics(
        run_id=run_b.id,
        total_cases=1,
        passed_cases=0,
        pass_rate=0.0,
        avg_faithfulness=0.3,
        avg_relevance=0.4,
        avg_schema=1.0,
        duration_ms=12.0,
    )

    service = PromptBenchmarkService(db_session)
    comp = service.compare_runs(run_a.id, run_b.id)

    assert comp is not None
    assert comp.pass_rate_delta == -1.0
    assert comp.regressions_count == 1
    assert comp.gains_count == 0
    assert comp.verdict == "CRITICAL_REGRESSION"
