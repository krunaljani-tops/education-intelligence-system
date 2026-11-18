import json
from datetime import datetime
from typing import Dict, Any
from backend.app.agents.tools import EducationDatabaseTools

class StudentDataAnalystAgent:
    name: str = "Student Data Analyst Agent"
    role: str = "Analyzes student profiles, demographic spread, age brackets, admission velocity, and diversity patterns."

    def __init__(self, tools: EducationDatabaseTools):
        self.tools = tools

    def run(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        metrics = self.tools.get_student_metrics()

        total = metrics["total_students"]
        genders = metrics["gender_distribution"]
        cities = metrics["city_distribution"]
        edu = metrics["education_distribution"]
        ages = metrics["age_stats"]
        monthly = metrics["monthly_admissions"]

        top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:3]
        top_cities_str = ", ".join([f"{c[0]} ({c[1]} students, {round(c[1]/total*100, 1)}%)" for c in top_cities])

        findings_summary = (
            f"The institution maintains {total:,} unique registered student profiles admitted between May 2026 and October 2026. "
            f"Demographic analysis indicates strong geographic concentration in {top_cities_str}. "
            f"The gender distribution reflects Female: {genders.get('Female', 0)} ({round(genders.get('Female', 0)/total*100, 1)}%), "
            f"Male: {genders.get('Male', 0)} ({round(genders.get('Male', 0)/total*100, 1)}%), and Other: {genders.get('Other', 0)} ({round(genders.get('Other', 0)/total*100, 1)}%). "
            f"The student cohort spans ages {ages['min']} to {ages['max']} years (average: {ages['avg']} years), "
            f"with the 21-25 bracket representing the largest segment ({ages['brackets']['21-25']} students). "
            f"Educational backgrounds encompass Diploma ({edu.get('Diploma', 0)}), Graduate ({edu.get('Graduate', 0)}), "
            f"Undergraduate ({edu.get('Undergraduate', 0)}), and Professional ({edu.get('Professional', 0)})."
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
