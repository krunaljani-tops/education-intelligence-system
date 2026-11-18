from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment
)
from backend.app.schemas import (
    StudentOut, StudentPerformanceOut, EnrollmentOut, FeePaymentOut
)

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[StudentOut])
def get_students(
    city: Optional[str] = Query(None),
    education_level: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    q = db.query(Student)
    if city:
        q = q.filter(Student.city == city)
    if education_level:
        q = q.filter(Student.education_level == education_level)
    if gender:
        q = q.filter(Student.gender == gender)
    if search:
        search_filter = f"%{search}%"
        q = q.filter((Student.student_name.ilike(search_filter)) | (Student.student_id.ilike(search_filter)))

    return q.offset(skip).limit(limit).all()

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return student

@router.get("/{student_id}/performance", response_model=StudentPerformanceOut)
def get_student_performance(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")

    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    attendance_records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    assessments = db.query(Assessment).filter(Assessment.student_id == student_id).all()
    payments = db.query(FeePayment).filter(FeePayment.student_id == student_id).all()

    # Attendance calculation
    att_count = len(attendance_records)
    present_count = sum(1 for a in attendance_records if a.attendance_status == "Present")
    late_count = sum(1 for a in attendance_records if a.attendance_status == "Late")
    absent_count = sum(1 for a in attendance_records if a.attendance_status == "Absent")
    att_pct = round((present_count / att_count * 100), 1) if att_count > 0 else 0.0

    # Attendance Risk Category (Transparent rule-based heuristic)
    if att_count == 0:
        att_risk = "No Attendance Records Logged"
    elif att_pct < 60.0:
        att_risk = "High Attendance Risk (<60%)"
    elif att_pct <= 75.0:
        att_risk = "Medium Attendance Risk (60-75%)"
    else:
        att_risk = "Normal Attendance Category (>75%)"

    # Assessment calculation
    asm_count = len(assessments)
    valid_scores = [a.score for a in assessments if a.submission_status in ["Submitted", "Late"]]
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0
    missing_count = sum(1 for a in assessments if a.submission_status == "Missing")
    late_sub_count = sum(1 for a in assessments if a.submission_status == "Late")

    grades_dist = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in assessments:
        if a.grade in grades_dist:
            grades_dist[a.grade] += 1

    # Academic Risk Category
    if asm_count == 0:
        acad_risk = "No Assessment Records Logged"
    elif avg_score < 50.0:
        acad_risk = "High Academic Risk (<50%)"
    elif avg_score < 70.0:
        acad_risk = "Medium Academic Risk (50-69%)"
    else:
        acad_risk = "Normal Academic Category (>=70%)"

    # Overall Risk Category
    risk_reasons = []
    if att_count > 0 and att_pct < 60.0:
        risk_reasons.append(f"Low Attendance ({att_pct}%)")
    if asm_count > 0 and avg_score < 50.0:
        risk_reasons.append(f"Low Average Score ({avg_score}%)")
    if missing_count > 1:
        risk_reasons.append(f"{missing_count} Missing Assessments")
    
    # Check dropped enrollment
    has_dropped = any(e.enrollment_status == "Dropped" for e in enrollments)
    if has_dropped:
        risk_reasons.append("Has Dropped Enrollment")

    if (att_count > 0 and att_pct < 60.0) or (asm_count > 0 and avg_score < 50.0) or has_dropped:
        overall_risk = "High Risk"
    elif (att_count > 0 and att_pct <= 75.0) or (asm_count > 0 and avg_score < 70.0) or missing_count > 0:
        overall_risk = "Medium Risk"
    else:
        overall_risk = "Low Risk"

    # Payments summary
    paid_total = sum(p.amount for p in payments if p.payment_status == "Paid")
    pending_total = sum(p.amount for p in payments if p.payment_status == "Pending")
    failed_total = sum(p.amount for p in payments if p.payment_status == "Failed")

    return {
        "student": student,
        "enrollments": enrollments,
        "attendance_count": att_count,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
        "attendance_percentage": att_pct,
        "attendance_risk_level": att_risk,
        "assessments_count": asm_count,
        "average_score": avg_score,
        "missing_assessments": missing_count,
        "late_submissions": late_sub_count,
        "grades_distribution": grades_dist,
        "academic_risk_level": acad_risk,
        "overall_risk_category": overall_risk,
        "risk_reasons": risk_reasons,
        "total_fee_paid": round(paid_total, 2),
        "total_fee_pending": round(pending_total, 2),
        "total_fee_failed": round(failed_total, 2),
        "payments": payments
    }
