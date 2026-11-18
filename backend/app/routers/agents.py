from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.database import get_db
from backend.app.models import AnalysisHistory, AgentExecutionLog, User
from backend.app.schemas import AnalysisHistoryOut, AgentExecutionLogOut
from backend.app.auth import require_roles
from backend.app.agents.crew import EducationMultiAgentCrew

router = APIRouter(prefix="/agents", tags=["Multi-Agents"])

@router.post("/analyze")
def trigger_analysis(
    title: str = Query("Comprehensive Education Intelligence Run", description="Execution Title"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Manager"]))
):
    crew = EducationMultiAgentCrew(db)
    result = crew.execute_workflow(title=title)
    return result

@router.get("/status/{analysis_id}", response_model=AnalysisHistoryOut)
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    run = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found")
    return run

@router.get("/logs/{analysis_id}", response_model=List[AgentExecutionLogOut])
def get_analysis_logs(analysis_id: str, db: Session = Depends(get_db)):
    logs = (
        db.query(AgentExecutionLog)
        .filter(AgentExecutionLog.analysis_id == analysis_id)
        .order_by(AgentExecutionLog.start_time.asc())
        .all()
    )
    if not logs:
        # Check if run exists
        run = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Analysis run not found")
    return logs
