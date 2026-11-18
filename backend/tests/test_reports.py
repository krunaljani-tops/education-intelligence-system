def test_pdf_report_generation_and_download(client, admin_token):
    gen_res = client.post(
        "/api/reports/generate",
        json={"report_title": "Automated Test PDF Report"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert gen_res.status_code == 200
    data = gen_res.json()
    assert data["success"] is True
    report_id = data["report_id"]

    # Test listing reports
    list_res = client.get("/api/reports")
    assert list_res.status_code == 200
    reports = list_res.json()
    assert any(r["id"] == report_id for r in reports)

    # Test download
    dl_res = client.get(f"/api/reports/{report_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000  # valid PDF bytes
