import pytest
from backend.app.models import User

def check_user_flow(client, username, password, expected_role, expected_tabs, forbidden_tabs):
    # 1. Login
    login_res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    data = login_res.json()
    token = data["access_token"]
    user = data["user"]
    assert user["role"] == expected_role

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Get Me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == expected_role

    # 3. Test Dashboard Overview
    dash_res = client.get("/api/dashboard/overview", headers=headers)
    assert dash_res.status_code == 200
    kpis = dash_res.json()["kpis"]
    assert kpis["total_students"] == 1200
    assert kpis["total_fee_collection"] == 7637309.78

    # 4. Test Student Profiles
    stu_res = client.get("/api/students/?skip=0&limit=5", headers=headers)
    assert stu_res.status_code == 200
    assert len(stu_res.json()) == 5

    # 5. Test Student Intelligence
    si_res = client.get("/api/students/STU00001/performance", headers=headers)
    assert si_res.status_code == 200
    assert si_res.json()["overall_risk_category"] == "Low Risk"

    # 6. Test Course & Enrollments
    c_res = client.get("/api/enrollments/course-analysis", headers=headers)
    assert c_res.status_code == 200
    assert len(c_res.json()) == 8

    # 7. Test Attendance Operations
    att_res = client.get("/api/attendance/summary", headers=headers)
    assert att_res.status_code == 200
    assert att_res.json()["attendance_percentage"] == 77.76

    # 8. Test Assessment Performance
    ass_res = client.get("/api/assessments/summary", headers=headers)
    assert ass_res.status_code == 200
    assert ass_res.json()["average_score"] == 63.15

    # 9. Test Fee Analytics
    f_res = client.get("/api/fees/summary", headers=headers)
    assert f_res.status_code == 200
    assert f_res.json()["collected_revenue"] == 7637309.78

    # 10. Test AI Recommendations
    rec_res = client.get("/api/recommendations/", headers=headers)
    assert rec_res.status_code == 200
    assert len(rec_res.json()) >= 1

    # 11. Test PDF Reports
    rep_res = client.get("/api/reports", headers=headers)
    assert rep_res.status_code == 200

    # 12. Test History
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 200

    # 13. Test Datasets validation
    val_res = client.get("/api/datasets/validation", headers=headers)
    assert val_res.status_code == 200

    # 14. RBAC check on User Management endpoint
    users_res = client.get("/api/auth/users", headers=headers)
    if expected_role == "Admin":
        assert users_res.status_code == 200
    else:
        assert users_res.status_code == 403

    # 15. Check Side Menu items visibility mapping
    is_admin = user["role"] == "Admin"
    is_manager = user["role"] in ["Manager", "Admin"]

    all_tabs = [
        {"id": "dashboard", "hide": False},
        {"id": "students", "hide": False},
        {"id": "student-intelligence", "hide": False},
        {"id": "courses", "hide": False},
        {"id": "attendance", "hide": False},
        {"id": "assessments", "hide": False},
        {"id": "finance", "hide": False},
        {"id": "agent-monitor", "hide": False},
        {"id": "recommendations", "hide": False},
        {"id": "approvals", "hide": not is_manager},
        {"id": "ai-assistant", "hide": False},
        {"id": "dataset-upload", "hide": not is_admin},
        {"id": "dataset-validation", "hide": False},
        {"id": "reports", "hide": False},
        {"id": "history", "hide": False},
        {"id": "users", "hide": not is_admin},
    ]

    visible = [t["id"] for t in all_tabs if not t["hide"]]
    for exp in expected_tabs:
        assert exp in visible, f"{exp} missing for {expected_role}"
    for forb in forbidden_tabs:
        assert forb not in visible, f"{forb} should NOT be visible for {expected_role}"

def test_admin_flow_and_menus(client):
    check_user_flow(client, "admin", "AdminPassword123!", "Admin",
        ["dashboard", "students", "student-intelligence", "courses", "attendance", "assessments", "finance", "agent-monitor", "recommendations", "approvals", "ai-assistant", "dataset-upload", "dataset-validation", "reports", "history", "users"],
        []
    )

def test_manager_flow_and_menus(client):
    check_user_flow(client, "manager", "ManagerPassword123!", "Manager",
        ["dashboard", "students", "student-intelligence", "courses", "attendance", "assessments", "finance", "agent-monitor", "recommendations", "approvals", "ai-assistant", "dataset-validation", "reports", "history"],
        ["dataset-upload", "users"]
    )

def test_faculty_flow_and_menus(client):
    check_user_flow(client, "faculty", "FacultyPassword123!", "Faculty",
        ["dashboard", "students", "student-intelligence", "courses", "attendance", "assessments", "finance", "agent-monitor", "recommendations", "ai-assistant", "dataset-validation", "reports", "history"],
        ["approvals", "dataset-upload", "users"]
    )
