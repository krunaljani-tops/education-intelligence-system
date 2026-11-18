import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import GeneratedReport, User
from backend.app.schemas import GeneratedReportOut, ReportCreate
from backend.app.auth import require_roles, get_current_user
from backend.app.pdf_generator import build_pdf_report

router = APIRouter(prefix="/reports", tags=["PDF Reports"])

@router.post("/generate")
def generate_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Manager"]))
):
    try:
        file_path, filename, report_id = build_pdf_report(
            db,
            analysis_id=payload.analysis_id,
            generated_by=current_user.full_name or current_user.username
        )
        return {
            "success": True,
            "report_id": report_id,
            "filename": filename,
            "download_url": f"/api/reports/{report_id}/download"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@router.get("", response_model=List[GeneratedReportOut])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(GeneratedReport).order_by(GeneratedReport.generated_at.desc()).all()
    results = []
    for r in reports:
        results.append({
            "id": r.id,
            "analysis_id": r.analysis_id,
            "report_title": r.report_title,
            "filename": r.filename,
            "file_size": r.file_size,
            "generated_at": r.generated_at,
            "generated_by": r.generated_by,
            "download_url": f"/api/reports/{r.id}/download"
        })
    return results

@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="PDF report file not found on disk")

    return FileResponse(
        path=report.file_path,
        filename=report.filename,
        media_type="application/pdf"
    )
