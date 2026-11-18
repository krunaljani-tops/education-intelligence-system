def test_recommendation_approval_workflow(client, manager_token):
    # Fetch recommendations
    recs_res = client.get("/api/recommendations")
    assert recs_res.status_code == 200
    recs = recs_res.json()
    assert len(recs) > 0

    first_rec = recs[0]
    rec_id = first_rec["id"]

    # Approve recommendation as Manager
    approve_res = client.post(
        f"/api/recommendations/{rec_id}/approve",
        json={"comments": "Approved for Q3 execution."},
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # Verify history was recorded
    hist_res = client.get("/api/recommendations/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert any(h["recommendation_id"] == rec_id and h["action"] == "APPROVED" for h in history)

def test_recommendation_rejection_workflow(client, manager_token):
    recs_res = client.get("/api/recommendations")
    assert recs_res.status_code == 200
    recs = recs_res.json()
    if len(recs) > 1:
        target_rec = recs[1]
        rec_id = target_rec["id"]

        reject_res = client.post(
            f"/api/recommendations/{rec_id}/reject",
            json={"comments": "Budget constraints; defer to next fiscal cycle."},
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert reject_res.status_code == 200
        assert reject_res.json()["status"] == "REJECTED"
