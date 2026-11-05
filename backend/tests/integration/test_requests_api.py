from backend.app.models.enums import RequestCategory, RequestPriority, RequestStatus


def test_create_valid_request(client):
    payload = {
        "title": "Acesso a ferramenta de pesquisa",
        "description": "Necessito de login na ferramenta de pesquisa jurídica.",
        "category": RequestCategory.ACCESS_AND_SYSTEMS.value,
        "priority": RequestPriority.HIGH.value,
        "department": "Contencioso",
        "requester_name": "Mariana Demo",
    }
    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["status"] == RequestStatus.NEW.value
    assert data["priority"] == RequestPriority.HIGH.value
    assert data["department"] == "Contencioso"


def test_create_request_validation_error_short_title(client):
    payload = {
        "title": "Oi",  # Less than 5 characters
        "description": "Descrição com tamanho aceitável para teste de validação.",
    }
    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 422


def test_create_request_validation_error_short_description(client):
    payload = {
        "title": "Título Válido",
        "description": "Curta",  # Less than 10 characters
    }
    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 422


def test_list_requests_and_filters(client):
    # Create request
    client.post(
        "/api/v1/requests",
        json={
            "title": "Extração de dados para auditoria",
            "description": "Relatório analítico em planilha para auditoria interna.",
            "category": RequestCategory.DATA_AND_REPORTS.value,
        },
    )

    # List all
    res = client.get("/api/v1/requests")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    titles = [item["title"] for item in body["items"]]
    assert "Extração de dados para auditoria" in titles

    # Search filter
    res_search = client.get("/api/v1/requests?search=auditoria")
    assert res_search.status_code == 200
    search_body = res_search.json()
    assert len(search_body["items"]) >= 1


def test_get_request_details(client):
    create_res = client.post(
        "/api/v1/requests",
        json={
            "title": "Configuração de novo certificado digital",
            "description": "Necessidade de configuração do token A1 na máquina.",
        },
    )
    req_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/requests/{req_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == req_id


def test_get_nonexistent_request(client):
    res = client.get("/api/v1/requests/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
