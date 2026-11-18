from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from datetime import datetime
from typing import Dict, Any, List

from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment
)

class EducationDatabaseTools:
    def __init__(self, db: Session):
        self.db = db

    def get_student_metrics(self) -> Dict[str, Any]:
        """Calculates exact student demographics, age distribution, cities, education levels, and monthly admissions."""
        total_students = self.db.query(func.count(Student.student_id)).scalar() or 0
        
        # Gender distribution
        gender_counts = dict(
            self.db.query(Student.gender, func.count(Student.student_id))
            .group_by(Student.gender).all()
        )
        
        # Education level
        education_counts = dict(
            self.db.query(Student.education_level, func.count(Student.student_id))
            .group_by(Student.education_level).all()
        )
        
        # City-wise distribution
        city_counts = dict(
            self.db.query(Student.city, func.count(Student.student_id))
            .group_by(Student.city).order_by(func.count(Student.student_id).desc()).all()
        )
        
        # Age summary
        age_stats = self.db.query(
            func.min(Student.age),
            func.max(Student.age),
            func.avg(Student.age)
        ).first()

        # Age brackets
        age_brackets = {
            "16-20": self.db.query(func.count(Student.student_id)).filter(Student.age <= 20).scalar() or 0,
            "21-25": self.db.query(func.count(Student.student_id)).filter(Student.age.between(21, 25)).scalar() or 0,
            "26-30": self.db.query(func.count(Student.student_id)).filter(Student.age.between(26, 30)).scalar() or 0,
            "31-35": self.db.query(func.count(Student.student_id)).filter(Student.age > 30).scalar() or 0,
        }

        # Monthly admissions
        students = self.db.query(Student.admission_date).all()
        monthly_admissions = {}
        for (adm_date,) in students:
            if adm_date:
                m_key = adm_date.strftime("%Y-%m")
                monthly_admissions[m_key] = monthly_admissions.get(m_key, 0) + 1
        
        return {
            "total_students": total_students,
            "gender_distribution": gender_counts,
            "education_distribution": education_counts,
            "city_distribution": city_counts,
            "age_stats": {
                "min": age_stats[0] if age_stats else 0,
                "max": age_stats[1] if age_stats else 0,
                "avg": round(age_stats[2], 1) if age_stats and age_stats[2] else 0,
                "brackets": age_brackets
            },
            "monthly_admissions": dict(sorted(monthly_admissions.items()))
        }

    def get_enrollment_metrics(self) -> Dict[str, Any]:
        """Calculates course popularity, enrollment status, delivery modes, and fee ranges."""
        total_enrollments = self.db.query(func.count(Enrollment.enrollment_id)).scalar() or 0
        
        # Status distribution
        status_counts = dict(
            self.db.query(Enrollment.enrollment_status, func.count(Enrollment.enrollment_id))
            .group_by(Enrollment.enrollment_status).all()
        )
        
        # Delivery mode
        mode_counts = dict(
            self.db.query(Enrollment.delivery_mode, func.count(Enrollment.enrollment_id))
            .group_by(Enrollment.delivery_mode).all()
        )
        
        # Course-wise breakdown with avg fees
        course_stats = (
            self.db.query(
                Enrollment.course,
                func.count(Enrollment.enrollment_id).label("count"),
                func.avg(Enrollment.course_fee).label("avg_fee"),
                func.sum(Enrollment.course_fee).label("total_fee")
            )
            .group_by(Enrollment.course)
            .order_by(func.count(Enrollment.enrollment_id).desc())
            .all()
        )
        courses_summary = [
            {
                "course": c[0],
                "enrollments": c[1],
                "avg_fee": round(float(c[2] or 0), 2),
                "total_course_fee_listed": round(float(c[3] or 0), 2)
            }
            for c in course_stats
        ]

        # Monthly enrollment trends
        enrs = self.db.query(Enrollment.enrollment_date).all()
        monthly_enrollments = {}
        for (enr_date,) in enrs:
            if enr_date:
                m_key = enr_date.strftime("%Y-%m")
                monthly_enrollments[m_key] = monthly_enrollments.get(m_key, 0) + 1

        # Unique batches
        unique_batches = self.db.query(func.count(distinct(Enrollment.batch_id))).scalar() or 0

        return {
            "total_enrollments": total_enrollments,
            "status_distribution": status_counts,
            "delivery_mode_distribution": mode_counts,
            "course_enrollment_ranking": courses_summary,
            "monthly_enrollment_trend": dict(sorted(monthly_enrollments.items())),
            "unique_batches_count": unique_batches
        }

    def get_financial_metrics(self) -> Dict[str, Any]:
        """Calculates successful fee collections, pending payments, failed amounts, payment methods, and installments."""
        # Strictly count Paid transactions as successfully collected revenue
        paid_res = self.db.query(
            func.count(FeePayment.payment_id),
            func.sum(FeePayment.amount)
        ).filter(FeePayment.payment_status == "Paid").first()
        paid_count = paid_res[0] or 0
        total_paid_revenue = round(float(paid_res[1] or 0.0), 2)

        pending_res = self.db.query(
            func.count(FeePayment.payment_id),
            func.sum(FeePayment.amount)
        ).filter(FeePayment.payment_status == "Pending").first()
        pending_count = pending_res[0] or 0
        total_pending_amount = round(float(pending_res[1] or 0.0), 2)

        failed_res = self.db.query(
            func.count(FeePayment.payment_id),
            func.sum(FeePayment.amount)
        ).filter(FeePayment.payment_status == "Failed").first()
        failed_count = failed_res[0] or 0
        total_failed_amount = round(float(failed_res[1] or 0.0), 2)

        # Payment methods breakdown
        method_stats = (
            self.db.query(
                FeePayment.payment_method,
                func.count(FeePayment.payment_id),
                func.sum(case((FeePayment.payment_status == "Paid", FeePayment.amount), else_=0))
            )
            .group_by(FeePayment.payment_method)
            .all()
        )
        payment_methods = [
            {
                "method": m[0],
                "transaction_count": m[1],
                "paid_amount": round(float(m[2] or 0), 2)
            }
            for m in method_stats
        ]

        # Monthly fee collections
        payments = self.db.query(FeePayment.payment_date, FeePayment.amount, FeePayment.payment_status).all()
        monthly_collections = {}
        for p_date, amt, p_status in payments:
            if p_date and p_status == "Paid":
                m_key = p_date.strftime("%Y-%m")
                monthly_collections[m_key] = monthly_collections.get(m_key, 0.0) + float(amt)

        monthly_collections = {k: round(v, 2) for k, v in sorted(monthly_collections.items())}

        # Installment numbers
        installment_stats = dict(
            self.db.query(FeePayment.installment_no, func.count(FeePayment.payment_id))
            .group_by(FeePayment.installment_no).order_by(FeePayment.installment_no).all()
        )

        return {
            "total_transactions": paid_count + pending_count + failed_count,
            "paid_transactions_count": paid_count,
            "total_paid_revenue": total_paid_revenue,
            "pending_transactions_count": pending_count,
            "total_pending_amount": total_pending_amount,
            "failed_transactions_count": failed_count,
            "total_failed_amount": total_failed_amount,
            "payment_methods": payment_methods,
            "monthly_collections": monthly_collections,
            "installment_distribution": installment_stats
        }

    def get_academic_and_operations_metrics(self) -> Dict[str, Any]:
        """Calculates attendance %, late/absent breakdown, topic-wise attendance, assessment score average, grades, and submissions."""
        # Attendance records
        total_att = self.db.query(func.count(Attendance.attendance_id)).scalar() or 0
        present_count = self.db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Present").scalar() or 0
        late_count = self.db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Late").scalar() or 0
        absent_count = self.db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Absent").scalar() or 0

        attendance_pct = round((present_count / total_att * 100), 2) if total_att > 0 else 0.0

        # Topic-wise attendance
        topic_stats = (
            self.db.query(
                Attendance.session_topic,
                func.count(Attendance.attendance_id).label("total"),
                func.sum(case((Attendance.attendance_status == "Present", 1), else_=0)).label("present"),
                func.sum(case((Attendance.attendance_status == "Absent", 1), else_=0)).label("absent"),
                func.sum(case((Attendance.attendance_status == "Late", 1), else_=0)).label("late")
            )
            .group_by(Attendance.session_topic)
            .all()
        )
        topic_breakdown = [
            {
                "topic": t[0],
                "total_sessions": t[1],
                "present": t[2],
                "absent": t[3],
                "late": t[4],
                "present_rate": round((t[2] / t[1] * 100), 2) if t[1] > 0 else 0
            }
            for t in topic_stats
        ]

        # Assessment metrics
        total_asm = self.db.query(func.count(Assessment.assessment_id)).scalar() or 0
        score_res = self.db.query(func.avg(Assessment.score), func.min(Assessment.score), func.max(Assessment.score)).first()
        avg_score = round(float(score_res[0] or 0), 2) if score_res else 0.0

        # Grade distribution
        grades_dist = dict(
            self.db.query(Assessment.grade, func.count(Assessment.assessment_id))
            .group_by(Assessment.grade).order_by(Assessment.grade).all()
        )

        # Submission status
        sub_status = dict(
            self.db.query(Assessment.submission_status, func.count(Assessment.assessment_id))
            .group_by(Assessment.submission_status).all()
        )

        # Course-wise score
        course_scores = (
            self.db.query(
                Assessment.course,
                func.count(Assessment.assessment_id),
                func.avg(Assessment.score)
            )
            .group_by(Assessment.course)
            .order_by(func.avg(Assessment.score).desc())
            .all()
        )
        course_perf = [
            {
                "course": c[0],
                "assessments_count": c[1],
                "avg_score": round(float(c[2] or 0), 2)
            }
            for c in course_scores
        ]

        return {
            "attendance": {
                "total_records": total_att,
                "present_records": present_count,
                "late_records": late_count,
                "absent_records": absent_count,
                "attendance_percentage": attendance_pct,
                "topic_breakdown": topic_breakdown
            },
            "assessments": {
                "total_records": total_asm,
                "average_score": avg_score,
                "min_score": float(score_res[1] or 0) if score_res else 0,
                "max_score": float(score_res[2] or 0) if score_res else 0,
                "grade_distribution": grades_dist,
                "submission_status_distribution": sub_status,
                "course_performance": course_perf
            }
        }
