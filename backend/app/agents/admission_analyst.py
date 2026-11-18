import json
from datetime import datetime
from typing import Dict, Any
from backend.app.agents.tools import EducationDatabaseTools

class AdmissionCourseAnalyticsAgent:
    name: str = "Admission & Course Analytics Agent"
    role: str = "Evaluates course enrollment velocity, program popularity ranking, delivery modes, and completion rates."

    def __init__(self, tools: EducationDatabaseTools):
        self.tools = tools

    def run(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        metrics = self.tools.get_enrollment_metrics()

        total = metrics["total_enrollments"]
        status = metrics["status_distribution"]
        modes = metrics["delivery_mode_distribution"]
        ranking = metrics["course_enrollment_ranking"]
        unique_batches = metrics["unique_batches_count"]

        top_course = ranking[0] if ranking else {"course": "None", "enrollments": 0}
        lowest_course = ranking[-1] if ranking else {"course": "None", "enrollments": 0}

        active = status.get("Active", 0)
        completed = status.get("Completed", 0)
        dropped = status.get("Dropped", 0)
        on_hold = status.get("On Hold", 0)

        drop_rate = round(dropped / total * 100, 2) if total > 0 else 0
        completion_rate = round(completed / total * 100, 2) if total > 0 else 0

        findings_summary = (
            f"Across {unique_batches} active batches, a total of {total:,} course enrollments were recorded. "
            f"Program popularity ranking is led by '{top_course['course']}' ({top_course['enrollments']} enrollments), "
            f"while '{lowest_course['course']}' registered the lowest intake ({lowest_course['enrollments']} enrollments). "
            f"Current enrollment statuses indicate {active:,} Active ({round(active/total*100, 1)}%), "
            f"{completed:,} Completed ({completion_rate}%), {on_hold:,} On Hold ({round(on_hold/total*100, 1)}%), and "
            f"{dropped:,} Dropped enrollments ({drop_rate}% attrition rate). "
            f"Delivery modes show balanced utilization: Hybrid ({modes.get('Hybrid', 0)}), "
            f"Offline ({modes.get('Offline', 0)}), and Online ({modes.get('Online', 0)}). "
            f"Note: Campaign and marketing lead acquisition data are not present in this workbook, so insights are derived exclusively from operational registration logs."
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
