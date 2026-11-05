import io

import pytest
from fastapi.testclient import TestClient

from backend.app.core.database import Base, engine
from backend.app.main import app


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_client():
    return TestClient(app)


def test_api_full_document_lifecycle(api_client):
    # 1. Intake document via text
    sample_text = """
    GOVERNO DO ESTADO DE SÃO PAULO
    SECRETARIA DA FAZENDA - SEFAZ/SP
    AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA - AIIM Nº 9.999.888-1

    AUTUADO: INDÚSTRIA METAL PAULISTA LTDA
    CNPJ: 11.222.333/0001-44
    TRIBUTO: ICMS
    VALOR PRINCIPAL: R$ 500.000,00
    MULTA DE OFÍCIO: R$ 250.000,00
    JUROS SELIC: R$ 50.000,00
    VALOR TOTAL: R$ 800.000,00

    DATA DA INTIMAÇÃO: 10/02/2024
    DATA DE VENCIMENTO: 11/03/2024
    Incorreu nas disposições do Art. 61 do RICMS/SP.
    """
    res_intake = api_client.post(
        "/api/v1/documents/text",
        json={
            "filename": "aiim_metal_paulista.txt",
            "text": sample_text,
            "document_type": "AIIM",
        },
    )
    assert res_intake.status_code == 200, res_intake.text
    doc = res_intake.json()
    doc_id = doc["id"]
    assert doc["filename"] == "aiim_metal_paulista.txt"
    assert doc["document_type"] == "AIIM"
    assert len(doc["chunks"]) > 0

    # 2. List documents
    res_list = api_client.get("/api/v1/documents")
    assert res_list.status_code == 200
    docs = res_list.json()
    assert len(docs) >= 1
    assert docs[0]["id"] == doc_id

    # 3. Get document details
    res_get = api_client.get(f"/api/v1/documents/{doc_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == doc_id

    # 4. Trigger / fetch extraction
    res_ext = api_client.post(f"/api/v1/documents/{doc_id}/extract")
    assert res_ext.status_code == 200
    ext = res_ext.json()
    assert ext["contribuinte_cnpj_cpf"] == "11.222.333/0001-44"
    assert ext["valor_total"] == 800000.0
    assert "ICMS" in ext["tributos_identificados"]

    # 5. Get Executive Summary
    res_sum = api_client.get(f"/api/v1/documents/{doc_id}/summary")
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert summary["document_id"] == doc_id
    assert summary["grau_risco"] in ("MEDIO", "ALTO")
    assert "ICMS" in summary["tributos"]
    assert "Resumo Executivo Fiscal" in summary["resumo_texto"]
    assert summary["prazos"]["data_intimacao"] == "10/02/2024"

    # 6. Create Chat Session
    res_session = api_client.post(
        "/api/v1/chat/sessions",
        json={"document_id": doc_id, "title": "Sessão de Análise de Risco"},
    )
    assert res_session.status_code == 200
    session_data = res_session.json()
    session_id = session_data["id"]

    # 7. Query Chat Session (Grounded Question)
    res_q1 = api_client.post(
        f"/api/v1/chat/sessions/{session_id}/query",
        json={"question": "Qual o valor total da autuação e o tributo exigido?"},
    )
    assert res_q1.status_code == 200
    q1_data = res_q1.json()
    assert q1_data["is_grounded"] is True
    assert len(q1_data["citations"]) > 0
    assert q1_data["citations"][0]["page_number"] >= 1
    assert "pág." in q1_data["answer"]

    # 8. Query Chat Session (Ungrounded question - anti-hallucination)
    res_q2 = api_client.post(
        f"/api/v1/chat/sessions/{session_id}/query",
        json={"question": "Qual a taxa de câmbio do euro para iene japonês em Tóquio?"},
    )
    assert res_q2.status_code == 200
    q2_data = res_q2.json()
    assert q2_data["is_grounded"] is False
    assert q2_data["answer"] == "A informação não foi localizada no documento analisado."
    assert len(q2_data["citations"]) == 0

    # 9. Get Session History
    res_history = api_client.get(f"/api/v1/chat/sessions/{session_id}/history")
    assert res_history.status_code == 200
    history = res_history.json()
    assert len(history) == 4  # 2 questions + 2 answers
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    # 10. Dashboard Metrics
    res_metrics = api_client.get("/api/v1/dashboard/metrics")
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()
    assert metrics["total_documents"] >= 1
    assert metrics["total_tax_amount"] >= 800000.0
    assert "AIIM" in metrics["documents_by_type"]


def test_upload_multipart_document(api_client):
    file_content = (
        "AUTO DE INFRAÇÃO E IMPOSIÇÃO DE MULTA\nVALOR TOTAL: R$ 150.000,00\nCNPJ: 22.333.444/0001-55\nICMS"
    ).encode()
    files = {"file": ("auto_teste.txt", io.BytesIO(file_content), "text/plain")}
    res = api_client.post("/api/v1/documents/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["filename"] == "auto_teste.txt"
    assert data["document_type"] == "AIIM"



def test_not_found_handling(api_client):
    res_doc = api_client.get("/api/v1/documents/non-existent-id")
    assert res_doc.status_code == 404

    res_chat = api_client.post(
        "/api/v1/chat/sessions/non-existent-id/query",
        json={"question": "Teste"},
    )
    assert res_chat.status_code == 404
