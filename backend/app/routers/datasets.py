import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import User, UploadedDataset
from backend.app.schemas import (
    UploadedDatasetOut, DatasetValidationReport
)
from backend.app.config import settings
from backend.app.auth import require_roles
from backend.app.excel_importer import (
    validate_and_preview_excel, import_excel_to_db
)

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetValidationReport)
async def upload_dataset_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["Admin"]))
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel spreadsheets (.xlsx, .xls) are permitted."
        )

    saved_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    report = validate_and_preview_excel(saved_path)
    return report

@router.get("/validation", response_model=DatasetValidationReport)
def get_dataset_validation(
    filename: Optional[str] = Query(None, description="Filename in upload directory or root")
):
    target_path = "02_Education.xlsx"
    if filename:
        upload_path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(upload_path):
            target_path = upload_path
        elif os.path.exists(filename):
            target_path = filename

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Dataset file '{target_path}' not found.")

    return validate_and_preview_excel(target_path)

@router.get("/preview", response_model=DatasetValidationReport)
def get_dataset_preview(filename: Optional[str] = Query(None)):
    return get_dataset_validation(filename)

@router.post("/import")
def import_dataset(
    filename: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    target_path = "02_Education.xlsx"
    if filename:
        upload_path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(upload_path):
            target_path = upload_path
        elif os.path.exists(filename):
            target_path = filename

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File '{target_path}' not found.")

    success, message, counts = import_excel_to_db(target_path, db, uploaded_by=current_user.username)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "counts": counts
    }

@router.get("", response_model=List[UploadedDatasetOut])
def list_uploaded_datasets(db: Session = Depends(get_db)):
    return db.query(UploadedDataset).order_by(UploadedDataset.uploaded_at.desc()).all()
