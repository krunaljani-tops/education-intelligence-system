import os

def test_excel_validation(client):
    res = client.get("/api/datasets/validation")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert set(data["sheets_found"]).issuperset({"Students", "Enrollments", "Attendance", "Assessments", "Fee_Payments"})
    assert data["record_counts"]["Students"] == 1200
    assert data["record_counts"]["Enrollments"] == 1600
    assert data["record_counts"]["Attendance"] == 2500
    assert data["record_counts"]["Assessments"] == 1800
    assert data["record_counts"]["Fee_Payments"] == 1200

def test_dataset_preview(client):
    res = client.get("/api/datasets/preview")
    assert res.status_code == 200
    data = res.json()
    assert len(data["previews"]) >= 5
    students_preview = next(p for p in data["previews"] if p["sheet_name"] == "Students")
    assert "student_id" in students_preview["columns"]
    assert len(students_preview["sample_data"]) > 0

def test_import_already_imported(client, admin_token):
    # Calling import when already populated should detect checksum and maintain state
    res = client.post("/api/datasets/import", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["success"] is True
