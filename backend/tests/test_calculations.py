def test_dashboard_kpis_exact_values(client):
    res = client.get("/api/dashboard/overview")
    assert res.status_code == 200
    kpis = res.json()["kpis"]
    assert kpis["total_students"] == 1200
    assert kpis["total_enrollments"] == 1600
    assert kpis["active_enrollments"] == 393
    assert kpis["completed_enrollments"] == 406
    assert kpis["dropped_enrollments"] == 383
    assert kpis["on_hold_enrollments"] == 418
    assert kpis["average_attendance"] == 77.76
    assert kpis["present_count"] == 1944
    assert kpis["late_count"] == 164
    assert kpis["absent_count"] == 392
    assert kpis["average_assessment_score"] == 63.15
    assert abs(kpis["total_fee_collection"] - 7637309.78) < 0.1
    assert abs(kpis["pending_payments"] - 3862177.04) < 0.1
    assert abs(kpis["failed_payments"] - 3660803.97) < 0.1

def test_attendance_calculation_rules(client):
    res = client.get("/api/attendance/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] == 2500
    assert data["present_records"] == 1944
    assert data["late_records"] == 164
    assert data["absent_records"] == 392
    assert data["attendance_percentage"] == 77.76

def test_finance_calculation_rules(client):
    res = client.get("/api/fees/summary")
    assert res.status_code == 200
    data = res.json()
    assert abs(data["collected_revenue"] - 7637309.78) < 0.1
    assert abs(data["pending_amount"] - 3862177.04) < 0.1
    assert abs(data["failed_amount"] - 3660803.97) < 0.1
    assert data["paid_transactions"] == 597
    assert data["pending_transactions"] == 306
    assert data["failed_transactions"] == 297

def test_student_performance_and_risk(client):
    res = client.get("/api/students/STU00001/performance")
    assert res.status_code == 200
    data = res.json()
    assert data["student"]["student_id"] == "STU00001"
    assert "attendance_percentage" in data
    assert "overall_risk_category" in data
    assert data["overall_risk_category"] in ["High Risk", "Medium Risk", "Low Risk"]
