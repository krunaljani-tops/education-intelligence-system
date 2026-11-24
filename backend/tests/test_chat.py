def test_chat_total_students(client):
    res = client.post("/api/chat/ask", json={"query": "How many total students are in the institute?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "1,200" in data["answer"] or "1200" in data["answer"]
    assert data["evidence_query"] is not None
    assert "students" in data["evidence_query"].lower()

def test_chat_highest_enrollment(client):
    res = client.post("/api/chat/ask", json={"query": "Which course has the highest enrollment?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "{top_course}" not in data["answer"]
    assert "Data Analytics" in data["answer"]
    assert "211" in data["answer"]
    assert data["evidence_query"] is not None

def test_chat_fee_revenue_strict_rule(client):
    res = client.post("/api/chat/ask", json={"query": "What is the total collected fee revenue?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "7,637,309" in data["answer"] or "7637309" in data["answer"] or "76.37" in data["answer"]
    assert "Paid" in data["answer"]
    assert "fee_payments" in data["evidence_query"].lower()

def test_chat_attendance_rate(client):
    res = client.post("/api/chat/ask", json={"query": "What is the classroom attendance rate?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "77.76" in data["answer"]
    assert data["evidence_query"] is not None
