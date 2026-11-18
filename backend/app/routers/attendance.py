from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import Attendance
from backend.app.schemas import AttendanceOut

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("", response_model=List[AttendanceOut])
def get_attendance(
    batch_id: Optional[str] = Query(None),
    session_topic: Optional[str] = Query(None),
    attendance_status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Attendance)
    if batch_id:
        q = q.filter(Attendance.batch_id == batch_id)
    if session_topic:
        q = q.filter(Attendance.session_topic == session_topic)
    if attendance_status:
        q = q.filter(Attendance.attendance_status == attendance_status)
    return q.offset(skip).limit(limit).all()

@router.get("/summary")
def get_attendance_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Attendance.attendance_id)).scalar() or 0
    present = db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Present").scalar() or 0
    late = db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Late").scalar() or 0
    absent = db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Absent").scalar() or 0

    topic_stats = (
        db.query(
            Attendance.session_topic,
            func.count(Attendance.attendance_id),
            func.sum(case((Attendance.attendance_status == 'Present', 1), else_=0)),
            func.sum(case((Attendance.attendance_status == 'Late', 1), else_=0)),
            func.sum(case((Attendance.attendance_status == 'Absent', 1), else_=0))
        )
        .group_by(Attendance.session_topic)
        .all()
    )

    topics = []
    for t in topic_stats:
        t_total = t[1]
        t_present = int(t[2] or 0)
        topics.append({
            "topic": t[0],
            "total_records": t_total,
            "present": t_present,
            "late": int(t[3] or 0),
            "absent": int(t[4] or 0),
            "attendance_rate": round(t_present / t_total * 100, 1) if t_total > 0 else 0
        })

    return {
        "total_records": total,
        "present_records": present,
        "late_records": late,
        "absent_records": absent,
        "attendance_percentage": round(present / total * 100, 2) if total > 0 else 0.0,
        "topics": sorted(topics, key=lambda x: x["attendance_rate"], reverse=True)
    }
