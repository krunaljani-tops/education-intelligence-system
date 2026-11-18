def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "DEMO DATA" in data["classification"]

def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPassword123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Admin"

def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword"})
    assert res.status_code == 401

def test_get_me(client, admin_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "admin"

def test_role_based_access(client, faculty_token):
    # Faculty cannot list users (Admin only)
    res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 403

def test_register_new_user(client):
    import uuid
    uid = str(uuid.uuid4())[:8]
    payload = {
        "username": f"user_{uid}",
        "email": f"user_{uid}@example.com",
        "full_name": f"Test User {uid}",
        "role": "Faculty",
        "password": "Password123!"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    assert res.json()["username"] == payload["username"]
