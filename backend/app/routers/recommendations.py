from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import AIRecommendation, ApprovalHistory, User
from backend.app.schemas import (
    RecommendationOut, ApprovalDecision, ApprovalHistoryOut
)
from backend.app.auth import get_current_user, require_roles

def is_valid_filter(val: Optional[str]) -> bool:
    if val is None:
        return False
    s = str(val).strip()
    return s != "" and s.lower() not in ("undefined", "null", "none", "all")

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Approval"])

@router.get("", response_model=List[RecommendationOut])
def get_recommendations(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(AIRecommendation)
    if is_valid_filter(status_filter):
        q = q.filter(AIRecommendation.status == status_filter.strip())
    if is_valid_filter(category):
        q = q.filter(AIRecommendation.category == category.strip())
    if is_valid_filter(priority):
        q = q.filter(AIRecommendation.priority == priority.strip())
    return q.order_by(AIRecommendation.id.desc()).all()

@router.post("/{recommendation_id}/approve", response_model=RecommendationOut)
def approve_recommendation(
    recommendation_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Manager"]))
):
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "APPROVED"

    history = ApprovalHistory(
        recommendation_id=rec.id,
        user_id=current_user.id,
        reviewer_name=current_user.full_name or current_user.username,
        action="APPROVED",
        manager_comments=decision.comments or "Approved by management."
    )
    db.add(history)
    db.commit()
    db.refresh(rec)
    return rec

@router.post("/{recommendation_id}/reject", response_model=RecommendationOut)
def reject_recommendation(
    recommendation_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Manager"]))
):
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "REJECTED"

    history = ApprovalHistory(
        recommendation_id=rec.id,
        user_id=current_user.id,
        reviewer_name=current_user.full_name or current_user.username,
        action="REJECTED",
        manager_comments=decision.comments or "Rejected by management review."
    )
    db.add(history)
    db.commit()
    db.refresh(rec)
    return rec

@router.get("/history", response_model=List[ApprovalHistoryOut])
def get_approval_history(db: Session = Depends(get_db)):
    return db.query(ApprovalHistory).order_by(ApprovalHistory.reviewed_at.desc()).all()
