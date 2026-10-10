from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_reports_local_mode():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["name"] == "ORBIT"
    setup = client.post("/api/auth/setup", json={"username":"orbit-founder-test","password":"test-password-that-is-long-123"})
    assert setup.status_code in (200, 409)


def test_developer_requires_explicit_approval():
    response = client.post("/api/developer/jobs", json={"goal": "create a test project"})
    assert response.status_code == 403


def test_ceo_delegation_requires_explicit_approval():
    response = client.post("/api/ceo/execute", json={"goal": "create a test project"})
    assert response.status_code == 403


def test_terminal_requires_explicit_approval():
    response = client.post("/api/command/execute", json={"command": "python --version"})
    assert response.status_code == 403
