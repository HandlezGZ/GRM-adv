from backend.app.models.enums import (
    ClassificationSource,
    EventType,
    RequestCategory,
    RequestPriority,
)


def test_review_request_classification(client):
    # 1. Create request
    create_res = client.post(
        "/api/v1/requests",
        json={
            "title": "Ajuste em planilha de honorários",
            "description": "Necessito de apoio com fórmula e dados fiscais.",
        },
    )
    req_id = create_res.json()["id"]

    # 2. Automatically classify it
    classify_res = client.post(f"/api/v1/requests/{req_id}/classify")
    assert classify_res.status_code == 200

    # 3. Human analyst overrides/reviews
    review_payload = {
        "category": RequestCategory.DATA_AND_REPORTS.value,
        "team": "Dados / Inovação",
        "priority": RequestPriority.HIGH.value,
        "review_reason": "Confirmado como suporte com prioridade alta.",
        "reviewer_name": "Dr. Fernando",
    }
    review_res = client.post(f"/api/v1/requests/{req_id}/review", json=review_payload)
    assert review_res.status_code == 200
    updated = review_res.json()
    assert updated["category"] == RequestCategory.DATA_AND_REPORTS.value
    assert updated["team"] == "Dados / Inovação"
    assert updated["priority"] == RequestPriority.HIGH.value
    assert updated["classification_source"] == ClassificationSource.HUMAN.value
    assert updated["classification_confidence"] == 1.0

    # 4. Verify audit event
    events_res = client.get(f"/api/v1/requests/{req_id}/events")
    events = events_res.json()
    review_events = [
        e for e in events
        if e["event_type"] == EventType.CLASSIFICATION_REVIEWED.value
    ]
    assert len(review_events) == 1
    assert review_events[0]["actor"] == "human"
    assert "Dr. Fernando" in review_events[0]["summary"]
