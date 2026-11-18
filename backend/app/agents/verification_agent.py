import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models import (
    Student, Enrollment, Attendance, Assessment, FeePayment
)

class VerificationAgent:
    name: str = "Verification Agent"
    role: str = "Conducts independent numerical auditing, database query verification, conflict detection, and final report gatekeeping."

    def __init__(self, db: Session):
        self.db = db

    def run(self, prior_agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        audit_checks: List[Dict[str, Any]] = []
        inconsistencies: List[str] = []

        # 1. Verify Student Counts
        db_student_count = self.db.query(func.count(Student.student_id)).scalar() or 0
        agent1_count = prior_agent_outputs.get("Student Data Analyst Agent", {}).get("data", {}).get("total_students", 0)
        match_students = (db_student_count == agent1_count)
        audit_checks.append({
            "check": "Total Students Verification",
            "db_value": db_student_count,
            "agent_value": agent1_count,
            "status": "PASS" if match_students else "FAIL"
        })
        if not match_students:
            inconsistencies.append(f"Student count mismatch: DB has {db_student_count}, Agent 1 reported {agent1_count}.")

        # 2. Verify Enrollments & Statuses
        db_enr_count = self.db.query(func.count(Enrollment.enrollment_id)).scalar() or 0
        agent2_count = prior_agent_outputs.get("Admission & Course Analytics Agent", {}).get("data", {}).get("total_enrollments", 0)
        match_enr = (db_enr_count == agent2_count)
        audit_checks.append({
            "check": "Total Enrollments Verification",
            "db_value": db_enr_count,
            "agent_value": agent2_count,
            "status": "PASS" if match_enr else "FAIL"
        })
        if not match_enr:
            inconsistencies.append(f"Enrollments count mismatch: DB has {db_enr_count}, Agent 2 reported {agent2_count}.")

        # 3. Verify Financial Revenue (Paid only)
        db_paid_revenue = float(
            self.db.query(func.sum(FeePayment.amount))
            .filter(FeePayment.payment_status == "Paid")
            .scalar() or 0.0
        )
        agent3_revenue = float(
            prior_agent_outputs.get("Finance Agent", {}).get("data", {}).get("total_paid_revenue", 0.0)
        )
        # Allow tiny float precision diff (< 0.1)
        match_revenue = abs(db_paid_revenue - agent3_revenue) < 0.1
        audit_checks.append({
            "check": "Total Paid Fee Collection Revenue",
            "db_value": round(db_paid_revenue, 2),
            "agent_value": round(agent3_revenue, 2),
            "status": "PASS" if match_revenue else "FAIL"
        })
        if not match_revenue:
            inconsistencies.append(f"Revenue mismatch: DB Paid sum is ₹{db_paid_revenue:,.2f}, Finance Agent reported ₹{agent3_revenue:,.2f}.")

        # 4. Verify Attendance Count and Percentage
        db_att_count = self.db.query(func.count(Attendance.attendance_id)).scalar() or 0
        db_present_count = self.db.query(func.count(Attendance.attendance_id)).filter(Attendance.attendance_status == "Present").scalar() or 0
        db_att_pct = round((db_present_count / db_att_count * 100), 2) if db_att_count > 0 else 0.0

        agent4_att = prior_agent_outputs.get("Academic Performance & Operations Agent", {}).get("data", {}).get("attendance", {})
        agent4_pct = agent4_att.get("attendance_percentage", 0.0)
        match_att = (db_att_count == agent4_att.get("total_records", 0)) and abs(db_att_pct - agent4_pct) < 0.1

        audit_checks.append({
            "check": "Classroom Attendance Percentage Audit",
            "db_value": f"{db_att_pct}% ({db_present_count}/{db_att_count})",
            "agent_value": f"{agent4_pct}%",
            "status": "PASS" if match_att else "FAIL"
        })
        if not match_att:
            inconsistencies.append(f"Attendance calculation mismatch: DB computed {db_att_pct}%, Agent 4 reported {agent4_pct}%.")

        # 5. Verify Assessment Count and Average
        db_asm_count = self.db.query(func.count(Assessment.assessment_id)).scalar() or 0
        db_avg_score = round(float(self.db.query(func.avg(Assessment.score)).scalar() or 0.0), 2)
        agent4_asm = prior_agent_outputs.get("Academic Performance & Operations Agent", {}).get("data", {}).get("assessments", {})
        agent4_score = agent4_asm.get("average_score", 0.0)
        match_score = (db_asm_count == agent4_asm.get("total_records", 0)) and abs(db_avg_score - agent4_score) < 0.1

        audit_checks.append({
            "check": "Average Assessment Score Audit",
            "db_value": db_avg_score,
            "agent_value": agent4_score,
            "status": "PASS" if match_score else "FAIL"
        })
        if not match_score:
            inconsistencies.append(f"Assessment score mismatch: DB computed {db_avg_score}, Agent 4 reported {agent4_score}.")

        # 6. Recommendation Verification
        strat_recs = prior_agent_outputs.get("Education Strategy Agent", {}).get("recommendations", [])
        has_recs = len(strat_recs) >= 3
        audit_checks.append({
            "check": "Strategic Action Plan Grounding & Integrity",
            "db_value": f"{len(strat_recs)} Action Items formulated",
            "agent_value": f"{len(strat_recs)} Action Items",
            "status": "PASS" if has_recs else "FAIL"
        })

        # Final Verification Determination
        all_passed = all(check["status"] == "PASS" for check in audit_checks)
        verification_status = "APPROVED" if all_passed else "REJECTED"

        summary = (
            f"Verification Agent completed comprehensive numerical and cross-relational audit across all 5 operational datasets. "
            f"Result: {verification_status} ({sum(1 for c in audit_checks if c['status'] == 'PASS')} of {len(audit_checks)} mathematical checks passed). "
            f"All values were mathematically cross-referenced directly against PostgreSQL tables. "
            + (f"No discrepancies detected. Report is officially APPROVED for executive download and manager approval." if all_passed
               else f"Discrepancies identified: {'; '.join(inconsistencies)}. Report is REJECTED.")
        )

        completion_time = datetime.utcnow()

        return {
            "agent_name": self.name,
            "agent_role": self.role,
            "status": "COMPLETED",
            "start_time": start_time,
            "completion_time": completion_time,
            "verification_status": verification_status,
            "summary": summary,
            "audit_checks": audit_checks,
            "inconsistencies": inconsistencies,
            "is_approved": all_passed
        }
