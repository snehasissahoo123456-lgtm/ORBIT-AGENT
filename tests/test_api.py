import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from config import settings
from main import app

settings.orbit_database = str(Path(tempfile.mkdtemp()) / "orbit-test.sqlite3")

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_founder_setup(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["name"] == "ORBIT"
    setup = client.post("/api/auth/setup", json={"username":"orbit-founder-test","password":"test-password-that-is-long-123"})
    assert setup.status_code == 200
    assert setup.json()["ok"] is True


def test_developer_requires_explicit_approval(client):
    response = client.post("/api/developer/jobs", json={"goal": "create a test project"})
    assert response.status_code == 403


def test_ceo_delegation_requires_explicit_approval(client):
    response = client.post("/api/ceo/execute", json={"goal": "create a test project"})
    assert response.status_code == 403


def test_terminal_requires_explicit_approval(client):
    response = client.post("/api/command/execute", json={"command": "python --version"})
    assert response.status_code == 403

def test_diagnostics_reports_activation_dependencies(client):
    response = client.get("/api/diagnostics")
    assert response.status_code == 200
    body = response.json()
    assert body["checks"]["api"]["ok"] is True
    assert "ollama" in body["checks"]
    assert body["remote_access"] is False


def test_protected_api_requires_founder_session():
    unauthenticated = TestClient(app)
    response = unauthenticated.get("/api/tasks")
    assert response.status_code == 401
