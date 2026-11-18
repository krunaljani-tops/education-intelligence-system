import re
import os
import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment, AIRecommendation
)
from backend.app.schemas import ChatRequest, ChatResponse
from backend.app.agents.tools import EducationDatabaseTools
from backend.app.config import settings

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

def call_gemini_if_available(prompt: str) -> str:
    """Enhance response with Gemini API if key is set; otherwise return None to use deterministic engine."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        res = requests.post(url, json=payload, timeout=6)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
    return None

@router.post("/ask", response_model=ChatResponse)
def ask_education_assistant(chat_in: ChatRequest, db: Session = Depends(get_db)):
    tools = EducationDatabaseTools(db)
    q = chat_in.query.lower().strip()

    evidence_query = None
    calculated_data = {}
    followups = [
        "Which course has the highest enrollment?",
        "What is the total collected fee revenue?",
        "How many students have dropped their course?",
        "What is the average classroom attendance?"
    ]

    # Pattern matching & intent execution against actual DB
    if any(k in q for k in ["how many student", "total student", "number of student"]):
        total_students = db.query(func.count(Student.student_id)).scalar() or 0
        evidence_query = "SELECT COUNT(student_id) FROM students;"
        calculated_data = {"total_students": total_students}
        answer = f"According to the database, there are exactly **{total_students:,}** registered students in the dataset (coverage: May 1, 2026 to October 31, 2026)."

    elif "highest enrollment" in q or "most popular course" in q:
        top_course = (
            db.query(Enrollment.course, func.count(Enrollment.enrollment_id))
            .group_by(Enrollment.course)
            .order_by(func.count(Enrollment.enrollment_id).desc())
            .first()
        )
        evidence_query = "SELECT course, COUNT(enrollment_id) FROM enrollments GROUP BY course ORDER BY count DESC LIMIT 1;"
        calculated_data = {"top_course": top_course[0], "enrollments": top_course[1]}
        answer = f"The course with the highest enrollment is **'{top_course[0]}'** with **{top_course[1]:,}** registered enrollments."

    elif "lowest enrollment" in q or "least popular course" in q:
        low_course = (
            db.query(Enrollment.course, func.count(Enrollment.enrollment_id))
            .group_by(Enrollment.course)
            .order_by(func.count(Enrollment.enrollment_id).asc())
            .first()
        )
        evidence_query = "SELECT course, COUNT(enrollment_id) FROM enrollments GROUP BY course ORDER BY count ASC LIMIT 1;"
        calculated_data = {"lowest_course": low_course[0], "enrollments": low_course[1]}
        answer = f"The course with the lowest enrollment is **'{low_course[0]}'** with **{low_course[1]:,}** registered enrollments."

    elif "drop" in q or "dropped" in q:
        dropped_count = db.query(func.count(Enrollment.enrollment_id)).filter(Enrollment.enrollment_status == "Dropped").scalar() or 0
        total_enr = db.query(func.count(Enrollment.enrollment_id)).scalar() or 0
        drop_rate = round(dropped_count / total_enr * 100, 2) if total_enr > 0 else 0
        evidence_query = "SELECT COUNT(enrollment_id) FROM enrollments WHERE enrollment_status = 'Dropped';"
        calculated_data = {"dropped_enrollments": dropped_count, "total_enrollments": total_enr, "drop_rate_pct": drop_rate}
        answer = f"A total of **{dropped_count:,}** students have dropped their enrollment out of {total_enr:,} historical enrollments, representing an attrition rate of **{drop_rate}%**."

    elif "below 75" in q or "low attendance" in q:
        # Find students with attendance < 75%
        student_att = (
            db.query(
                Attendance.student_id,
                func.count(Attendance.attendance_id).label("total"),
                func.sum(func.case((Attendance.attendance_status == 'Present', 1), else_=0)).label("present")
            )
            .group_by(Attendance.student_id)
            .having((func.sum(func.case((Attendance.attendance_status == 'Present', 1), else_=0)) * 100.0 / func.count(Attendance.attendance_id)) < 75.0)
            .all()
        )
        count_low = len(student_att)
        evidence_query = "SELECT student_id, COUNT(*) as total, SUM(CASE WHEN attendance_status = 'Present' THEN 1 ELSE 0 END) as present FROM attendance GROUP BY student_id HAVING (present * 100.0 / total) < 75;"
        sample_ids = [s[0] for s in student_att[:5]]
        calculated_data = {"low_attendance_students_count": count_low, "sample_students": sample_ids}
        answer = f"There are **{count_low}** students with an overall attendance below 75%. Sample student IDs requiring support: {', '.join(sample_ids)}."

    elif "batch" in q and ("lowest attendance" in q or "worst attendance" in q):
        batch_stats = (
            db.query(
                Attendance.batch_id,
                func.count(Attendance.attendance_id).label("total"),
                func.sum(func.case((Attendance.attendance_status == 'Present', 1), else_=0)).label("present")
            )
            .group_by(Attendance.batch_id)
            .order_by((func.sum(func.case((Attendance.attendance_status == 'Present', 1), else_=0)) * 100.0 / func.count(Attendance.attendance_id)).asc())
            .first()
        )
        rate = round((batch_stats[2] / batch_stats[1] * 100), 2)
        evidence_query = "SELECT batch_id, (SUM(present) * 100.0 / COUNT(*)) FROM attendance GROUP BY batch_id ORDER BY 2 ASC LIMIT 1;"
        calculated_data = {"batch_id": batch_stats[0], "attendance_rate_pct": rate}
        answer = f"Batch **'{batch_stats[0]}'** recorded the lowest attendance rate at **{rate}%** ({batch_stats[2]} present out of {batch_stats[1]} logged sessions)."

    elif "average assessment" in q or "average score" in q:
        avg_score = db.query(func.avg(Assessment.score)).scalar() or 0.0
        evidence_query = "SELECT AVG(score) FROM assessments;"
        calculated_data = {"average_score": round(float(avg_score), 2)}
        answer = f"The institutional average assessment score across all 1,800 examinations is **{round(float(avg_score), 2)}%**."

    elif "highest assessment" in q or "highest score" in q:
        course_perf = (
            db.query(Assessment.course, func.avg(Assessment.score))
            .group_by(Assessment.course)
            .order_by(func.avg(Assessment.score).desc())
            .first()
        )
        evidence_query = "SELECT course, AVG(score) FROM assessments GROUP BY course ORDER BY 2 DESC LIMIT 1;"
        calculated_data = {"course": course_perf[0], "avg_score": round(float(course_perf[1]), 2)}
        answer = f"The program with the highest assessment performance is **'{course_perf[0]}'** with an average score of **{round(float(course_perf[1]), 2)}%**."

    elif "missing" in q and "assessment" in q:
        missing_count = db.query(func.count(Assessment.assessment_id)).filter(Assessment.submission_status == "Missing").scalar() or 0
        evidence_query = "SELECT COUNT(*) FROM assessments WHERE submission_status = 'Missing';"
        calculated_data = {"missing_assessments": missing_count}
        answer = f"There are exactly **{missing_count:,}** missing assessment submissions recorded in the examination logs."

    elif "collected fee" in q or "total fee" in q or "revenue" in q:
        paid_res = db.query(func.sum(FeePayment.amount), func.count(FeePayment.payment_id)).filter(FeePayment.payment_status == "Paid").first()
        paid_amt = round(float(paid_res[0] or 0), 2)
        evidence_query = "SELECT SUM(amount) FROM fee_payments WHERE payment_status = 'Paid';"
        calculated_data = {"total_paid_revenue": paid_amt, "transactions": paid_res[1]}
        answer = f"The total collected fee revenue is **₹{paid_amt:,.2f}** from **{paid_res[1]:,}** successful 'Paid' transactions. (Note: Only 'Paid' status is recognized as revenue under institute rules)."

    elif "pending" in q:
        pending_res = db.query(func.sum(FeePayment.amount), func.count(FeePayment.payment_id)).filter(FeePayment.payment_status == "Pending").first()
        pending_amt = round(float(pending_res[0] or 0), 2)
        evidence_query = "SELECT SUM(amount) FROM fee_payments WHERE payment_status = 'Pending';"
        calculated_data = {"total_pending_amount": pending_amt, "transactions": pending_res[1]}
        answer = f"The total pending payment volume is **₹{pending_amt:,.2f}** across **{pending_res[1]:,}** transactions."

    elif "payment method" in q:
        top_method = (
            db.query(FeePayment.payment_method, func.count(FeePayment.payment_id))
            .group_by(FeePayment.payment_method)
            .order_by(func.count(FeePayment.payment_id).desc())
            .first()
        )
        evidence_query = "SELECT payment_method, COUNT(*) FROM fee_payments GROUP BY payment_method ORDER BY 2 DESC LIMIT 1;"
        calculated_data = {"most_frequent_method": top_method[0], "count": top_method[1]}
        answer = f"The most frequently used payment method is **'{top_method[0]}'** with **{top_method[1]:,}** recorded transactions."

    elif "recommendation" in q or "academic improvement" in q or "operational problem" in q:
        recs = db.query(AIRecommendation).order_by(AIRecommendation.id.asc()).limit(5).all()
        if recs:
            rec_texts = [f"{i+1}. **[{r.category}]**: {r.recommended_action} (Priority: {r.priority})" for i, r in enumerate(recs)]
            answer = "Here are the top strategic recommendations generated by the multi-agent system:\n\n" + "\n\n".join(rec_texts)
            calculated_data = {"recommendations_count": len(recs)}
        else:
            answer = "No strategic recommendations have been generated yet. Please run the AI Multi-Agent analysis first from the 'Agent Monitor' page."

    else:
        # Generic Query: Compute general health and try LLM answer
        total_stu = db.query(func.count(Student.student_id)).scalar() or 0
        total_enr = db.query(func.count(Enrollment.enrollment_id)).scalar() or 0
        paid_amt = db.query(func.sum(FeePayment.amount)).filter(FeePayment.payment_status == "Paid").scalar() or 0.0

        context_info = f"Dataset Metrics: 1,200 students, 1,600 enrollments, 2,500 attendance records, 1,800 assessments, ₹{paid_amt:,.2f} collected fees."
        llm_prompt = f"User asked: '{chat_in.query}'. Use this exact data context: {context_info}. Answer accurately and concisely without inventing fictional data."
        llm_reply = call_gemini_if_available(llm_prompt)

        if llm_reply:
            answer = llm_reply
        else:
            answer = (
                f"I analyzed your request against the PostgreSQL database. Currently, the system manages {total_stu:,} students and {total_enr:,} enrollments with ₹{paid_amt:,.2f} in collected fees. "
                f"If you're asking about courses, attendance, assessments, or fees, please feel free to ask specific metrics like 'Which course has the highest enrollment?' or 'How much fee is pending?'"
            )

    return {
        "answer": answer,
        "evidence_query": evidence_query,
        "calculated_data": calculated_data,
        "suggested_followups": followups
    }
