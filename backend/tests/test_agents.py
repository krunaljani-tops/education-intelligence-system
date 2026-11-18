def test_multi_agent_execution(client, admin_token):
    res = client.post(
        "/api/agents/analyze?title=Test%20Execution%20Run",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "analysis_id" in data
    assert data["status"] == "COMPLETED"
    assert data["verification_status"] == "APPROVED"
    assert len(data["agent_results"]) == 6
    assert len(data["recommendations"]) >= 3

def test_analysis_logs_and_verification(client):
    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    runs = history_res.json()
    assert len(runs) > 0
    latest_id = runs[0]["id"]

    logs_res = client.get(f"/api/agents/logs/{latest_id}")
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) == 6
    agent_names = [l["agent_name"] for l in logs]
    assert "Student Data Analyst Agent" in agent_names
    assert "Admission & Course Analytics Agent" in agent_names
    assert "Finance Agent" in agent_names
    assert "Academic Performance & Operations Agent" in agent_names
    assert "Education Strategy Agent" in agent_names
    assert "Verification Agent" in agent_names
