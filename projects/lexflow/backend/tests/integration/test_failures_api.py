def test_api_list_classification_failures(client):
    res = client.get("/api/v1/classification/failures")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
