import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.session import Base, get_db
from backend.app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def api_client():
    with TestClient(app) as c:
        yield c


def test_full_api_workflow(api_client):
    # 1. Health check
    res_health = api_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Create Dataset
    res_ds = api_client.post(
        "/api/v1/datasets",
        json={
            "name": "Integration Test Dataset",
            "description": "Integration testing for LexEval",
            "category": "TRIBUTARIO",
        },
    )
    assert res_ds.status_code == 201
    dataset_data = res_ds.json()
    dataset_id = dataset_data["id"]
    assert dataset_data["name"] == "Integration Test Dataset"

    # 3. Add Test Cases
    res_tc1 = api_client.post(
        f"/api/v1/datasets/{dataset_id}/cases",
        json={
            "title": "Prescrição Tributária",
            "input_query": "Qual o prazo prescricional?",
            "context_document": "Conforme o art. 174 do CTN, a prescrição ocorre em 5 anos.",
            "expected_output": "O prazo prescricional é de 5 anos nos termos do art. 174 do CTN.",
            "required_keywords": ["5 anos", "art. 174", "CTN"],
            "forbidden_terms": ["10 anos", "20 anos"],
        },
    )
    assert res_tc1.status_code == 201
    tc1_id = res_tc1.json()["id"]

    res_tc2 = api_client.post(
        f"/api/v1/datasets/{dataset_id}/cases",
        json={
            "title": "CSRF Retenção",
            "input_query": "Qual o prazo de recolhimento da CSRF?",
            "context_document": "A CSRF de 4,65% deve ser recolhida até o dia 20 do mês subsequente (Lei 10.833).",
            "expected_output": "Recolhimento até o dia 20 do mês subsequente (Lei 10.833).",
            "required_keywords": ["dia 20", "Lei 10.833"],
            "forbidden_terms": ["dia 10", "dia 15"],
        },
    )
    assert res_tc2.status_code == 201
    tc2_id = res_tc2.json()["id"]

    # List cases
    res_cases = api_client.get(f"/api/v1/datasets/{dataset_id}/cases")
    assert res_cases.status_code == 200
    assert len(res_cases.json()) == 2

    # 4. Create Prompt Versions
    res_pv1 = api_client.post(
        "/api/v1/prompts",
        json={
            "name": "prompt_legal",
            "version": "1.0.0",
            "system_prompt": "Legal assistant",
            "template_text": "Answer: {query}",
            "temperature": 0.2,
        },
    )
    assert res_pv1.status_code == 201
    pv1_id = res_pv1.json()["id"]

    res_pv2 = api_client.post(
        "/api/v1/prompts",
        json={
            "name": "prompt_legal",
            "version": "2.0.0",
            "system_prompt": "Strict legal auditor",
            "template_text": "Strict answer: {query}",
            "temperature": 0.0,
        },
    )
    assert res_pv2.status_code == 201
    pv2_id = res_pv2.json()["id"]

    # 5. Execute Run A (with simulated output where tc2 has hallucinated date)
    res_run_a = api_client.post(
        "/api/v1/eval/run",
        json={
            "dataset_id": dataset_id,
            "prompt_version_id": pv1_id,
            "model_name": "prompt_legal:1.0.0",
            "evaluator_type": "hybrid",
            "custom_outputs": {
                tc1_id: "O prazo prescricional é de 5 anos nos termos do art. 174 do CTN.",
                tc2_id: "A CSRF deve ser recolhida até o dia 10 sem falta.",  # Hallucinated "dia 10" (forbidden)
            },
        },
    )
    assert res_run_a.status_code == 201
    run_a_data = res_run_a.json()
    assert run_a_data["total_cases"] == 2
    assert run_a_data["passed_cases"] == 1
    assert run_a_data["pass_rate"] == 0.5
    run_a_id = run_a_data["id"]

    # 6. Execute Run B (both pass)
    res_run_b = api_client.post(
        "/api/v1/eval/run",
        json={
            "dataset_id": dataset_id,
            "prompt_version_id": pv2_id,
            "model_name": "prompt_legal:2.0.0",
            "evaluator_type": "hybrid",
            "custom_outputs": {
                tc1_id: "O prazo prescricional é de 5 anos nos termos do art. 174 do CTN.",
                tc2_id: "O recolhimento deve ocorrer até o dia 20 do mês subsequente conforme Lei 10.833.",
            },
        },
    )
    assert res_run_b.status_code == 201
    run_b_data = res_run_b.json()
    assert run_b_data["pass_rate"] == 1.0
    run_b_id = run_b_data["id"]

    # 7. Compare Runs A/B
    res_comp = api_client.get(f"/api/v1/eval/compare?run_a_id={run_a_id}&run_b_id={run_b_id}")
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["pass_rate_delta"] == 0.5
    assert comp_data["gains_count"] == 1
    assert comp_data["verdict"] == "POSITIVE_PROGRESSION"

    # 8. Query Failures
    res_fails = api_client.get(f"/api/v1/eval/failures?dataset_id={dataset_id}")
    assert res_fails.status_code == 200
    fails = res_fails.json()
    assert len(fails) == 1
    assert fails[0]["test_case_id"] == tc2_id

    # 9. Dashboard Metrics
    res_metrics = api_client.get("/api/v1/dashboard/metrics")
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()
    assert metrics["total_runs"] >= 2
    assert metrics["total_cases_evaluated"] >= 4
    assert metrics["total_failures"] >= 1
    assert len(metrics["recent_runs"]) >= 2
