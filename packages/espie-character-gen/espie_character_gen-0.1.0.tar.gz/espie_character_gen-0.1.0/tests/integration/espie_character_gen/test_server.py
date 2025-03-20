from fastapi.testclient import TestClient
import pytest
from espie_character_gen.server import fastapi_app


@pytest.fixture
def api_client():
    return TestClient(fastapi_app)


def test_healthz__when_calling__returns_ok(api_client):
    response = api_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"o": "k"}
