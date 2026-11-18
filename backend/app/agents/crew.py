import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.agents.tools import EducationDatabaseTools
from backend.app.agents.student_analyst import StudentDataAnalystAgent
from backend.app.agents.admission_analyst import AdmissionCourseAnalyticsAgent
from backend.app.agents.finance_agent import FinanceAgent
from backend.app.agents.academic_agent import AcademicOperationsAgent
from backend.app.agents.strategy_agent import EducationStrategyAgent
from backend.app.agents.verification_agent import VerificationAgent
from backend.app.models import (
    AnalysisHistory, AgentExecutionLog, AIRecommendation
)

class EducationMultiAgentCrew:
    def __init__(self, db: Session):
        self.db = db
        self.tools = EducationDatabaseTools(db)

    def execute_workflow(self, title: str = "Quarterly Education Intelligence Run") -> Dict[str, Any]:
        """Executes the full sequential multi-agent collaborative pipeline with verified auditing and DB persistence."""
        analysis_id = str(uuid.uuid4())
        run_start = datetime.utcnow()

        # Create parent analysis run record
        analysis_run = AnalysisHistory(
            id=analysis_id,
            title=title,
            status="RUNNING",
            total_agents=6,
            completed_agents=0,
            verification_status="PENDING",
            started_at=run_start
        )
        self.db.add(analysis_run)
        self.db.commit()

        prior_agent_outputs: Dict[str, Any] = {}
        logs_to_persist: List[AgentExecutionLog] = []

        try:
            # Step 1: Student Data Analyst Agent
            agent1 = StudentDataAnalystAgent(self.tools)
            out1 = agent1.run()
            prior_agent_outputs[agent1.name] = out1
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out1["agent_name"],
                agent_role=out1["agent_role"],
                status=out1["status"],
                start_time=out1["start_time"],
                completion_time=out1["completion_time"],
                input_context="Querying `students` demographic distributions, cities, age groups, and admission logs.",
                output_summary=out1["summary"],
                structured_output=out1["data"],
                verification_status="VERIFIED"
            ))
            analysis_run.completed_agents = 1
            self.db.commit()

            # Step 2: Admission & Course Analytics Agent
            agent2 = AdmissionCourseAnalyticsAgent(self.tools)
            out2 = agent2.run()
            prior_agent_outputs[agent2.name] = out2
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out2["agent_name"],
                agent_role=out2["agent_role"],
                status=out2["status"],
                start_time=out2["start_time"],
                completion_time=out2["completion_time"],
                input_context="Querying `enrollments` course popularity, delivery modes, batches, and status breakdown.",
                output_summary=out2["summary"],
                structured_output=out2["data"],
                verification_status="VERIFIED"
            ))
            analysis_run.completed_agents = 2
            self.db.commit()

            # Step 3: Finance Agent
            agent3 = FinanceAgent(self.tools)
            out3 = agent3.run()
            prior_agent_outputs[agent3.name] = out3
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out3["agent_name"],
                agent_role=out3["agent_role"],
                status=out3["status"],
                start_time=out3["start_time"],
                completion_time=out3["completion_time"],
                input_context="Querying `fee_payments` for Paid collections, Pending liabilities, Failed payments, and methods.",
                output_summary=out3["summary"],
                structured_output=out3["data"],
                verification_status="VERIFIED"
            ))
            analysis_run.completed_agents = 3
            self.db.commit()

            # Step 4: Academic Performance & Operations Agent
            agent4 = AcademicOperationsAgent(self.tools)
            out4 = agent4.run()
            prior_agent_outputs[agent4.name] = out4
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out4["agent_name"],
                agent_role=out4["agent_role"],
                status=out4["status"],
                start_time=out4["start_time"],
                completion_time=out4["completion_time"],
                input_context="Querying `attendance` present/late/absent rates, session durations, and `assessments` grades & submissions.",
                output_summary=out4["summary"],
                structured_output=out4["data"],
                verification_status="VERIFIED"
            ))
            analysis_run.completed_agents = 4
            self.db.commit()

            # Step 5: Education Strategy Agent
            agent5 = EducationStrategyAgent()
            out5 = agent5.run(prior_agent_outputs)
            prior_agent_outputs[agent5.name] = out5
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out5["agent_name"],
                agent_role=out5["agent_role"],
                status=out5["status"],
                start_time=out5["start_time"],
                completion_time=out5["completion_time"],
                input_context="Synthesizing multi-agent outputs from Agents 1-4 into strategic management action items.",
                output_summary=out5["summary"],
                structured_output={"recommendations": out5["recommendations"]},
                verification_status="VERIFIED"
            ))
            analysis_run.completed_agents = 5
            self.db.commit()

            # Step 6: Verification Agent
            agent6 = VerificationAgent(self.db)
            out6 = agent6.run(prior_agent_outputs)
            prior_agent_outputs[agent6.name] = out6
            logs_to_persist.append(AgentExecutionLog(
                analysis_id=analysis_id,
                agent_name=out6["agent_name"],
                agent_role=out6["agent_role"],
                status=out6["status"],
                start_time=out6["start_time"],
                completion_time=out6["completion_time"],
                input_context="Cross-checking numerical calculations from Agents 1-5 against PostgreSQL tables.",
                output_summary=out6["summary"],
                structured_output={
                    "audit_checks": out6["audit_checks"],
                    "inconsistencies": out6["inconsistencies"]
                },
                verification_status=out6["verification_status"]
            ))
            analysis_run.completed_agents = 6

            # Persist execution logs
            for log in logs_to_persist:
                self.db.add(log)

            # Persist Recommendations
            for r in out5.get("recommendations", []):
                rec = AIRecommendation(
                    analysis_id=analysis_id,
                    agent_source=out5["agent_name"],
                    category=r["category"],
                    problem_identified=r["problem_identified"],
                    dataset_evidence=r["dataset_evidence"],
                    recommended_action=r["recommended_action"],
                    expected_benefit=r["expected_benefit"],
                    priority=r["priority"],
                    confidence_level=r["confidence_level"],
                    status="PENDING"
                )
                self.db.add(rec)

            # Finalize parent AnalysisHistory
            run_end = datetime.utcnow()
            analysis_run.status = "COMPLETED"
            analysis_run.verification_status = out6["verification_status"]
            analysis_run.completed_at = run_end
            analysis_run.raw_metrics = {
                "student_metrics": out1["data"],
                "enrollment_metrics": out2["data"],
                "financial_metrics": out3["data"],
                "academic_metrics": out4["data"]
            }
            analysis_run.executive_summary = (
                f"Multi-agent collaborative intelligence execution completed in {(run_end - run_start).total_seconds():.1f}s. "
                f"Verification status: {out6['verification_status']}. "
                f"Generated {len(out5.get('recommendations', []))} prioritized institutional recommendations ready for Managerial review."
            )
            self.db.commit()

            return {
                "analysis_id": analysis_id,
                "title": title,
                "status": "COMPLETED",
                "verification_status": out6["verification_status"],
                "started_at": run_start,
                "completed_at": run_end,
                "duration_seconds": round((run_end - run_start).total_seconds(), 2),
                "executive_summary": analysis_run.executive_summary,
                "agent_results": prior_agent_outputs,
                "recommendations": out5.get("recommendations", [])
            }

        except Exception as e:
            self.db.rollback()
            analysis_run.status = "FAILED"
            analysis_run.completed_at = datetime.utcnow()
            analysis_run.executive_summary = f"Execution failed due to error: {str(e)}"
            self.db.commit()
            raise e
