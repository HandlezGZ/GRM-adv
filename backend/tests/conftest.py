import pytest
from backend.app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
