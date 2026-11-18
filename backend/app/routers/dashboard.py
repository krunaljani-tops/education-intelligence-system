from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from typing import Optional, List, Dict, Any

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def is_valid_filter(val: Optional[str]) -> bool:
    if val is None:
        return False
    s = str(val).strip()
    return s != "" and s.lower() not in ("undefined", "null", "none", "all")

@router.get("/overview")
def get_dashboard_overview(
    course: Optional[str] = Query(None),
    batch_id: Optional[str] = Query(None),
    enrollment_status: Optional[str] = Query(None),
    delivery_mode: Optional[str] = Query(None),
    month: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Base Query Filters for Enrollments
    enr_q = db.query(Enrollment)
    if is_valid_filter(course):
        enr_q = enr_q.filter(Enrollment.course == course.strip())
    if is_valid_filter(batch_id):
        enr_q = enr_q.filter(Enrollment.batch_id == batch_id.strip())
    if is_valid_filter(enrollment_status):
        enr_q = enr_q.filter(Enrollment.enrollment_status == enrollment_status.strip())
    if is_valid_filter(delivery_mode):
        enr_q = enr_q.filter(Enrollment.delivery_mode == delivery_mode.strip())
    
    total_enrollments = enr_q.count()
    active_enrollments = enr_q.filter(Enrollment.enrollment_status == "Active").count()
    completed_enrollments = enr_q.filter(Enrollment.enrollment_status == "Completed").count()
    dropped_enrollments = enr_q.filter(Enrollment.enrollment_status == "Dropped").count()
    on_hold_enrollments = enr_q.filter(Enrollment.enrollment_status == "On Hold").count()

    # Total students in system
    total_students = db.query(func.count(Student.student_id)).scalar() or 0

    # 2. Attendance Query
    att_q = db.query(Attendance)
    if batch_id:
        att_q = att_q.filter(Attendance.batch_id == batch_id)
    total_att = att_q.count()
    present_att = att_q.filter(Attendance.attendance_status == "Present").count()
    late_att = att_q.filter(Attendance.attendance_status == "Late").count()
    absent_att = att_q.filter(Attendance.attendance_status == "Absent").count()
    avg_attendance = round((present_att / total_att * 100), 2) if total_att > 0 else 0.0

    # 3. Assessment Query
    asm_q = db.query(Assessment)
    if course:
        asm_q = asm_q.filter(Assessment.course == course)
    total_asm = asm_q.count()
    avg_score_val = asm_q.with_entities(func.avg(Assessment.score)).scalar()
    avg_score = round(float(avg_score_val or 0.0), 2)

    # 4. Fee Payments Query (Paid = Revenue strictly)
    fee_q = db.query(FeePayment)
    paid_amt = fee_q.filter(FeePayment.payment_status == "Paid").with_entities(func.sum(FeePayment.amount)).scalar() or 0.0
    pending_amt = fee_q.filter(FeePayment.payment_status == "Pending").with_entities(func.sum(FeePayment.amount)).scalar() or 0.0
    failed_amt = fee_q.filter(FeePayment.payment_status == "Failed").with_entities(func.sum(FeePayment.amount)).scalar() or 0.0

    kpis = {
        "total_students": total_students,
        "total_enrollments": total_enrollments,
        "active_enrollments": active_enrollments,
        "completed_enrollments": completed_enrollments,
        "dropped_enrollments": dropped_enrollments,
        "on_hold_enrollments": on_hold_enrollments,
        "average_attendance": avg_attendance,
        "present_count": present_att,
        "late_count": late_att,
        "absent_count": absent_att,
        "average_assessment_score": avg_score,
        "total_fee_collection": round(float(paid_amt), 2),
        "pending_payments": round(float(pending_amt), 2),
        "failed_payments": round(float(failed_amt), 2),
        "demo_data_notice": settings.DEMO_DATA_LABEL
    }

    # 5. Charts Generation
    # Chart 1: Monthly Student Admission Trend
    students = db.query(Student.admission_date).all()
    admissions_month = {}
    for (ad,) in students:
        if ad:
            m = ad.strftime("%Y-%m")
            admissions_month[m] = admissions_month.get(m, 0) + 1
    chart1 = [{"month": k, "admissions": v} for k, v in sorted(admissions_month.items())]

    # Chart 2: Course-wise Enrollment Distribution
    course_dist = (
        enr_q.with_entities(Enrollment.course, func.count(Enrollment.enrollment_id))
        .group_by(Enrollment.course).all()
    )
    chart2 = [{"course": c[0], "enrollments": c[1]} for c in sorted(course_dist, key=lambda x: x[1], reverse=True)]

    # Chart 3: Enrollment Status Distribution
    status_dist = (
        enr_q.with_entities(Enrollment.enrollment_status, func.count(Enrollment.enrollment_id))
        .group_by(Enrollment.enrollment_status).all()
    )
    chart3 = [{"status": s[0], "count": s[1]} for s in status_dist]

    # Chart 4: Delivery Mode Distribution
    mode_dist = (
        enr_q.with_entities(Enrollment.delivery_mode, func.count(Enrollment.enrollment_id))
        .group_by(Enrollment.delivery_mode).all()
    )
    chart4 = [{"mode": m[0], "count": m[1]} for m in mode_dist]

    # Chart 5: Monthly Attendance Trend
    att_dates = att_q.with_entities(Attendance.attendance_date, Attendance.attendance_status).all()
    att_months = {}
    for ad, st in att_dates:
        if ad:
            m = ad.strftime("%Y-%m")
            if m not in att_months:
                att_months[m] = {"total": 0, "present": 0, "late": 0, "absent": 0}
            att_months[m]["total"] += 1
            if st == "Present":
                att_months[m]["present"] += 1
            elif st == "Late":
                att_months[m]["late"] += 1
            elif st == "Absent":
                att_months[m]["absent"] += 1
    chart5 = [
        {
            "month": k,
            "present": v["present"],
            "late": v["late"],
            "absent": v["absent"],
            "percentage": round(v["present"] / v["total"] * 100, 1) if v["total"] > 0 else 0
        }
        for k, v in sorted(att_months.items())
    ]

    # Chart 6: Batch-wise Attendance Comparison (top 10 batches by volume)
    batch_stats = (
        att_q.with_entities(
            Attendance.batch_id,
            func.count(Attendance.attendance_id),
            func.sum(case((Attendance.attendance_status == "Present", 1), else_=0))
        )
        .group_by(Attendance.batch_id)
        .order_by(Attendance.batch_id)
        .limit(15)
        .all()
    )
    chart6 = [
        {
            "batch": b[0],
            "total": b[1],
            "present": b[2],
            "percentage": round(b[2] / b[1] * 100, 1) if b[1] > 0 else 0
        }
        for b in batch_stats
    ]

    # Chart 7: Attendance Status Distribution
    chart7 = [
        {"name": "Present", "count": present_att},
        {"name": "Late", "count": late_att},
        {"name": "Absent", "count": absent_att}
    ]

    # Chart 8: Course-wise Assessment Performance
    course_asm = (
        asm_q.with_entities(
            Assessment.course,
            func.avg(Assessment.score),
            func.count(Assessment.assessment_id)
        )
        .group_by(Assessment.course)
        .order_by(func.avg(Assessment.score).desc())
        .all()
    )
    chart8 = [{"course": c[0], "avg_score": round(float(c[1] or 0), 1), "assessments": c[2]} for c in course_asm]

    # Chart 9: Grade Distribution
    grade_dist = (
        asm_q.with_entities(Assessment.grade, func.count(Assessment.assessment_id))
        .group_by(Assessment.grade).order_by(Assessment.grade).all()
    )
    chart9 = [{"grade": g[0], "count": g[1]} for g in grade_dist]

    # Chart 10: Assessment Submission Status
    sub_dist = (
        asm_q.with_entities(Assessment.submission_status, func.count(Assessment.assessment_id))
        .group_by(Assessment.submission_status).all()
    )
    chart10 = [{"status": s[0], "count": s[1]} for s in sub_dist]

    # Chart 11: Monthly Fee Collection (Paid revenue)
    payments = db.query(FeePayment.payment_date, FeePayment.amount, FeePayment.payment_status).all()
    monthly_fees = {}
    for pd_date, amt, p_stat in payments:
        if pd_date and p_stat == "Paid":
            m = pd_date.strftime("%Y-%m")
            monthly_fees[m] = monthly_fees.get(m, 0.0) + float(amt)
    chart11 = [{"month": k, "collected_amount": round(v, 2)} for k, v in sorted(monthly_fees.items())]

    # Chart 12: Payment Status Distribution
    pay_status = (
        db.query(FeePayment.payment_status, func.count(FeePayment.payment_id), func.sum(FeePayment.amount))
        .group_by(FeePayment.payment_status).all()
    )
    chart12 = [{"status": p[0], "count": p[1], "amount": round(float(p[2] or 0), 2)} for p in pay_status]

    # Chart 13: Payment Method Analysis
    method_dist = (
        db.query(FeePayment.payment_method, func.count(FeePayment.payment_id), func.sum(case((FeePayment.payment_status == "Paid", FeePayment.amount), else_=0)))
        .group_by(FeePayment.payment_method).all()
    )
    chart13 = [{"method": m[0], "transactions": m[1], "paid_amount": round(float(m[2] or 0), 2)} for m in method_dist]

    # Chart 14: Student City-wise Distribution
    city_dist = (
        db.query(Student.city, func.count(Student.student_id))
        .group_by(Student.city).order_by(func.count(Student.student_id).desc()).all()
    )
    chart14 = [{"city": c[0], "count": c[1]} for c in city_dist]

    return {
        "kpis": kpis,
        "charts": {
            "admissions_trend": chart1,
            "course_enrollments": chart2,
            "enrollment_statuses": chart3,
            "delivery_modes": chart4,
            "attendance_trend": chart5,
            "batch_attendance": chart6,
            "attendance_status": chart7,
            "course_assessment_performance": chart8,
            "grade_distribution": chart9,
            "assessment_submissions": chart10,
            "fee_collection_trend": chart11,
            "payment_status_distribution": chart12,
            "payment_methods": chart13,
            "city_distribution": chart14
        }
    }
