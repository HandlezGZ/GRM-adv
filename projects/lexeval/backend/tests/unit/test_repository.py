import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import (
    EvalDatasetCreate,
    EvalTestCaseCreate,
    PromptVersionCreate,
)


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


def test_create_and_get_dataset(db_session):
    repo = EvalRepository(db_session)
    dataset_in = EvalDatasetCreate(
        name="Test Tax Dataset",
        description="Dataset for testing PIS/COFINS",
        category="TRIBUTARIO",
    )
    dataset = repo.create_dataset(dataset_in)
    assert dataset.id is not None
    assert dataset.name == "Test Tax Dataset"

    fetched = repo.get_dataset(dataset.id)
    assert fetched is not None
    assert fetched.name == "Test Tax Dataset"


def test_create_and_list_test_cases(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="DS-1", category="TRIBUTARIO"))

    case_in = EvalTestCaseCreate(
        title="PIS/COFINS credit eligibility",
        input_query="Can input goods be credited?",
        context_document="Inputs used in manufacturing generate credits under Law 10.833.",
        expected_output="Yes, inputs generate credit.",
        required_keywords=["crédito", "insumos"],
        forbidden_terms=["vedado"],
    )
    case = repo.create_test_case(dataset.id, case_in)
    assert case.id is not None
    assert case.dataset_id == dataset.id
    assert "crédito" in case.required_keywords

    cases = repo.list_test_cases(dataset.id)
    assert len(cases) == 1
    assert cases[0].title == "PIS/COFINS credit eligibility"


def test_create_eval_run_and_results(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="DS-Run", category="TRIBUTARIO"))
    case = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="ICMS-ST",
            input_query="What is ICMS-ST?",
            context_document="Tax substitution applies forward.",
            expected_output="ICMS-ST is tax substitution.",
        ),
    )

    prompt = repo.create_prompt_version(
        PromptVersionCreate(
            name="tax_expert",
            version="1.0.0",
            system_prompt="You are a tax lawyer.",
            template_text="Question: {input}",
        )
    )

    run = repo.create_eval_run(
        dataset_id=dataset.id,
        model_name="rule-evaluator-v1",
        prompt_version_id=prompt.id,
    )
    assert run.id is not None
    assert run.status == "RUNNING"

    result = repo.create_eval_result(
        run_id=run.id,
        test_case_id=case.id,
        generated_output="ICMS-ST is tax substitution forward.",
        faithfulness_score=0.95,
        relevance_score=0.90,
        schema_score=1.0,
        passed=True,
    )
    assert result.id is not None
    assert result.passed is True

    repo.update_eval_run_metrics(
        run_id=run.id,
        total_cases=1,
        passed_cases=1,
        pass_rate=1.0,
        avg_faithfulness=0.95,
        avg_relevance=0.90,
        avg_schema=1.0,
        duration_ms=45.0,
    )

    updated_run = repo.get_eval_run(run.id)
    assert updated_run.pass_rate == 1.0
    assert len(updated_run.results) == 1


def test_failure_catalog_and_metrics(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="DS-Fail", category="TRIBUTARIO"))
    case = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="Retention deadline",
            input_query="What is the deadline?",
            context_document="Deadline is the 20th day.",
            expected_output="20th day of following month.",
        ),
    )
    run = repo.create_eval_run(dataset_id=dataset.id, model_name="rule-evaluator-v1")

    repo.create_eval_result(
        run_id=run.id,
        test_case_id=case.id,
        generated_output="Deadline is 15th day.",
        faithfulness_score=0.4,
        relevance_score=0.5,
        schema_score=1.0,
        passed=False,
        failure_reason="HALLUCINATION",
        diagnostics={"hallucinated_values": ["15th"]},
    )

    failures = repo.list_failures(dataset_id=dataset.id)
    assert len(failures) == 1
    assert failures[0].failure_reason == "HALLUCINATION"

    metrics = repo.get_dashboard_metrics()
    assert metrics["total_runs"] == 1
    assert metrics["total_cases_evaluated"] == 1
    assert metrics["total_failures"] == 1
    assert metrics["failures_by_reason"]["HALLUCINATION"] == 1
