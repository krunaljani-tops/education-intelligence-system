import json
from datetime import datetime
from typing import Dict, Any
from backend.app.agents.tools import EducationDatabaseTools

class AcademicOperationsAgent:
    name: str = "Academic Performance & Operations Agent"
    role: str = "Monitors classroom attendance, lateness trends, assessment performance, grade curves, and assignment compliance."

    def __init__(self, tools: EducationDatabaseTools):
        self.tools = tools

    def run(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        metrics = self.tools.get_academic_and_operations_metrics()

        att = metrics["attendance"]
        total_att = att["total_records"]
        present = att["present_records"]
        late = att["late_records"]
        absent = att["absent_records"]
        att_pct = att["attendance_percentage"]

        asm = metrics["assessments"]
        total_asm = asm["total_records"]
        avg_score = asm["average_score"]
        grades = asm["grade_distribution"]
        submissions = asm["submission_status_distribution"]
        course_perf = asm["course_performance"]

        top_perf = course_perf[0] if course_perf else {"course": "N/A", "avg_score": 0}
        lowest_perf = course_perf[-1] if course_perf else {"course": "N/A", "avg_score": 0}

        findings_summary = (
            f"Classroom operational metrics over {total_att:,} attendance sessions establish an overall attendance rate of {att_pct}% "
            f"derived strictly from {present:,} 'Present' sessions. In accordance with operational policy, "
            f"lateness is audited discretely: {late:,} sessions ({round(late/total_att*100, 1)}%) were marked 'Late', while {absent:,} sessions ({round(absent/total_att*100, 1)}%) were 'Absent'. "
            f"Academic evaluation across {total_asm:,} examinations registers an institutional average score of {avg_score}%. "
            f"Grade distribution breakdown reflects Grade A: {grades.get('A', 0)} ({round(grades.get('A', 0)/total_asm*100, 1)}%), "
            f"Grade B: {grades.get('B', 0)} ({round(grades.get('B', 0)/total_asm*100, 1)}%), "
            f"Grade C: {grades.get('C', 0)} ({round(grades.get('C', 0)/total_asm*100, 1)}%), and "
            f"Grade D: {grades.get('D', 0)} ({round(grades.get('D', 0)/total_asm*100, 1)}%). "
            f"Submission compliance monitoring flags {submissions.get('Missing', 0):,} Missing and {submissions.get('Late', 0):,} Late submissions. "
            f"Course assessment rankings highlight '{top_perf['course']}' with highest average ({top_perf['avg_score']}%) "
            f"and '{lowest_perf['course']}' requiring academic intervention ({lowest_perf['avg_score']}%)."
        )

        completion_time = datetime.utcnow()

        return {
            "agent_name": self.name,
            "agent_role": self.role,
            "status": "COMPLETED",
            "start_time": start_time,
            "completion_time": completion_time,
            "summary": findings_summary,
            "data": metrics
        }
