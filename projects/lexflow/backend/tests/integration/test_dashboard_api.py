def test_api_dashboard_metrics(client):
    res = client.get("/api/v1/dashboard/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "total_requests" in metrics
    assert "open_requests" in metrics
    assert "resolved_requests" in metrics
    assert "by_category" in metrics
    assert "by_priority" in metrics
    assert "by_status" in metrics
    assert "reviewed_count" in metrics
    assert "ai_failure_count" in metrics
