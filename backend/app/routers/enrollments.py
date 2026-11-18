from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import Enrollment
from backend.app.schemas import EnrollmentOut

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.get("", response_model=List[EnrollmentOut])
def get_enrollments(
    course: Optional[str] = Query(None),
    batch_id: Optional[str] = Query(None),
    enrollment_status: Optional[str] = Query(None),
    delivery_mode: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Enrollment)
    if course:
        q = q.filter(Enrollment.course == course)
    if batch_id:
        q = q.filter(Enrollment.batch_id == batch_id)
    if enrollment_status:
        q = q.filter(Enrollment.enrollment_status == enrollment_status)
    if delivery_mode:
        q = q.filter(Enrollment.delivery_mode == delivery_mode)
    return q.offset(skip).limit(limit).all()

@router.get("/course-analysis")
def get_course_analysis(db: Session = Depends(get_db)):
    courses = (
        db.query(
            Enrollment.course,
            func.count(Enrollment.enrollment_id).label("total_enrollments"),
            func.avg(Enrollment.course_fee).label("avg_fee"),
            func.sum(case((Enrollment.enrollment_status == 'Active', 1), else_=0)),
            func.sum(case((Enrollment.enrollment_status == 'Completed', 1), else_=0)),
            func.sum(case((Enrollment.enrollment_status == 'Dropped', 1), else_=0)),
            func.sum(case((Enrollment.enrollment_status == 'On Hold', 1), else_=0))
        )
        .group_by(Enrollment.course)
        .order_by(func.count(Enrollment.enrollment_id).desc())
        .all()
    )

    results = []
    for c in courses:
        total = c[1]
        results.append({
            "course": c[0],
            "total_enrollments": total,
            "avg_fee": round(float(c[2] or 0), 2),
            "active": int(c[3] or 0),
            "completed": int(c[4] or 0),
            "dropped": int(c[5] or 0),
            "on_hold": int(c[6] or 0),
            "drop_rate": round(int(c[5] or 0) / total * 100, 1) if total > 0 else 0,
            "completion_rate": round(int(c[4] or 0) / total * 100, 1) if total > 0 else 0
        })
    return results
