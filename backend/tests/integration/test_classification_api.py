from backend.app.models.enums import RequestCategory, RequestStatus


def test_api_classify_request(client):
    create_res = client.post(
        "/api/v1/requests",
        json={
            "title": "Acesso a ferramenta de pesquisa",
            "description": "Necessito de login na ferramenta para suporte.",
        },
    )
    req_id = create_res.json()["id"]

    # Trigger classification
    classify_res = client.post(f"/api/v1/requests/{req_id}/classify")
    assert classify_res.status_code == 200
    data = classify_res.json()
    assert data["request_id"] == req_id
    assert data["result"]["category"] == RequestCategory.ACCESS_AND_SYSTEMS.value
    assert data["result"]["team"] == "TI / Suporte"
    assert data["result"]["source"] == "rules"
    assert data["result"]["confidence"] >= 0.70

    # Verify request updated
    get_res = client.get(f"/api/v1/requests/{req_id}")
    req = get_res.json()
    assert req["category"] == RequestCategory.ACCESS_AND_SYSTEMS.value
    assert req["team"] == "TI / Suporte"
    assert req["status"] == RequestStatus.TRIAGE.value
