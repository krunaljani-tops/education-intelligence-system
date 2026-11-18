from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models import AnalysisHistory
from backend.app.schemas import AnalysisHistoryOut

router = APIRouter(prefix="/history", tags=["Analysis History"])

@router.get("", response_model=List[AnalysisHistoryOut])
def list_analysis_history(db: Session = Depends(get_db)):
    return db.query(AnalysisHistory).order_by(AnalysisHistory.started_at.desc()).all()

@router.get("/{analysis_id}", response_model=AnalysisHistoryOut)
def get_analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    run = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found")
    return run
