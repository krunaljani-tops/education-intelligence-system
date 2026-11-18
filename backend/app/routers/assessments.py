from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import Assessment
from backend.app.schemas import AssessmentOut

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=List[AssessmentOut])
def get_assessments(
    course: Optional[str] = Query(None),
    assessment_type: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    submission_status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Assessment)
    if course:
        q = q.filter(Assessment.course == course)
    if assessment_type:
        q = q.filter(Assessment.assessment_type == assessment_type)
    if grade:
        q = q.filter(Assessment.grade == grade)
    if submission_status:
        q = q.filter(Assessment.submission_status == submission_status)
    return q.offset(skip).limit(limit).all()

@router.get("/summary")
def get_assessments_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Assessment.assessment_id)).scalar() or 0
    avg_score = db.query(func.avg(Assessment.score)).scalar() or 0.0

    grades = dict(
        db.query(Assessment.grade, func.count(Assessment.assessment_id))
        .group_by(Assessment.grade).all()
    )

    types = (
        db.query(
            Assessment.assessment_type,
            func.count(Assessment.assessment_id),
            func.avg(Assessment.score)
        )
        .group_by(Assessment.assessment_type)
        .all()
    )

    type_summary = [
        {
            "type": t[0],
            "count": t[1],
            "avg_score": round(float(t[2] or 0), 1)
        }
        for t in types
    ]

    submissions = dict(
        db.query(Assessment.submission_status, func.count(Assessment.assessment_id))
        .group_by(Assessment.submission_status).all()
    )

    return {
        "total_assessments": total,
        "average_score": round(float(avg_score), 2),
        "grades": grades,
        "assessment_types": type_summary,
        "submission_statuses": submissions
    }
