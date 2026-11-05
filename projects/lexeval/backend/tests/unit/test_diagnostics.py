import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
from backend.app.repositories.eval_repository import EvalRepository
from backend.app.schemas.eval_schemas import EvalDatasetCreate, EvalTestCaseCreate
from backend.app.services.diagnostics import FailureCatalogService


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


def test_failure_catalog_service_queries(db_session):
    repo = EvalRepository(db_session)
    dataset = repo.create_dataset(EvalDatasetCreate(name="Fail-DS", category="TRIBUTARIO"))

    tc = repo.create_test_case(
        dataset.id,
        EvalTestCaseCreate(
            title="Fragile Case A",
            input_query="Q",
            context_document="Context doc text",
            expected_output="Ground truth output",
        ),
    )

    run = repo.create_eval_run(dataset_id=dataset.id, model_name="gpt-4-sample")
    repo.create_eval_result(
        run_id=run.id,
        test_case_id=tc.id,
        generated_output="Invented claim",
        faithfulness_score=0.2,
        relevance_score=0.5,
        schema_score=1.0,
        passed=False,
        failure_reason="HALLUCINATED_CITATION",
        diagnostics={"ungrounded_citations": ["Lei 9999"]},
    )

    service = FailureCatalogService(db_session)
    items = service.get_failure_catalog(dataset_id=dataset.id)
    assert len(items) == 1
    item = items[0]
    assert item.failure_reason == "HALLUCINATED_CITATION"
    assert item.test_case_title == "Fragile Case A"
    assert item.dataset_name == "Fail-DS"
    assert "Context doc" in item.context_snippet

    summary = service.get_failure_summary(dataset_id=dataset.id)
    assert summary["total_failures_cataloged"] == 1
    assert summary["breakdown_by_reason"]["HALLUCINATED_CITATION"] == 1
    assert summary["breakdown_by_model"]["gpt-4-sample"] == 1
    assert len(summary["top_fragile_cases"]) == 1
    assert summary["top_fragile_cases"][0]["title"] == "Fragile Case A"
