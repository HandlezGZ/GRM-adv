from backend.app.models.enums import RequestStatus


def test_api_status_transition_and_events(client):
    # Create request
    create_res = client.post(
        "/api/v1/requests",
        json={
            "title": "Solicitação para teste de API workflow",
            "description": "Validando PATCH de status e listagem de eventos.",
        },
    )
    req_id = create_res.json()["id"]

    # Transition NEW -> TRIAGE
    patch_res = client.patch(
        f"/api/v1/requests/{req_id}/status",
        json={"new_status": RequestStatus.TRIAGE.value, "reason": "Em triagem inicial"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == RequestStatus.TRIAGE.value

    # Query events
    events_res = client.get(f"/api/v1/requests/{req_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 2
    assert any(e["event_type"] == "STATUS_CHANGED" for e in events)


def test_api_invalid_status_transition_returns_400(client):
    create_res = client.post(
        "/api/v1/requests",
        json={
            "title": "Tentativa de transição proibida",
            "description": "Tentando pular de NEW direto para RESOLVED.",
        },
    )
    req_id = create_res.json()["id"]

    # Attempt illegal transition
    patch_res = client.patch(
        f"/api/v1/requests/{req_id}/status",
        json={"new_status": RequestStatus.RESOLVED.value},
    )
    assert patch_res.status_code == 400
    assert "Transição inválida" in patch_res.json()["detail"]
