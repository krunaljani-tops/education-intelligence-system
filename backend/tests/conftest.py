import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, Base, engine
from backend.app.auth import seed_default_users

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPassword123!"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def manager_token(client):
    res = client.post("/api/auth/login", json={"username": "manager", "password": "ManagerPassword123!"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def faculty_token(client):
    res = client.post("/api/auth/login", json={"username": "faculty", "password": "FacultyPassword123!"})
    assert res.status_code == 200
    return res.json()["access_token"]
