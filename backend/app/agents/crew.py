"""
Education Multi-Agent Crew Runner
=================================
Executes the CrewAI Multi-Agent Pipeline with 6 collaborative domain agents,
independent non-circular auditing, and database persistence.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.crewai_architecture import CrewAIEducationPipeline

class EducationMultiAgentCrew:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = CrewAIEducationPipeline(db)

    def execute_workflow(self, title: str = "Quarterly Education Intelligence Run") -> Dict[str, Any]:
        """Executes the full 6-agent CrewAI collaborative pipeline."""
        return self.pipeline.run(title=title)
