from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean, 
    ForeignKey, Text, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True, index=True)
    student_name = Column(String(150), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False)
    admission_date = Column(Date, nullable=False, index=True)
    education_level = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    fee_payments = relationship("FeePayment", back_populates="student", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    enrollment_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course = Column(String(100), nullable=False, index=True)
    enrollment_date = Column(Date, nullable=False, index=True)
    batch_id = Column(String(50), nullable=False, index=True)
    course_fee = Column(Float, nullable=False)
    enrollment_status = Column(String(50), nullable=False, index=True)  # Active, Completed, Dropped, On Hold
    delivery_mode = Column(String(50), nullable=False, index=True)      # Hybrid, Offline, Online
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="enrollments")


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(String(50), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    session_topic = Column(String(100), nullable=False, index=True)
    attendance_status = Column(String(50), nullable=False, index=True)  # Present, Absent, Late
    session_duration_minutes = Column(Integer, nullable=False)          # 60, 90, 120
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="attendance_records")


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    course = Column(String(100), nullable=False, index=True)
    assessment_date = Column(Date, nullable=False, index=True)
    assessment_type = Column(String(50), nullable=False, index=True)    # Assignment, Mock Interview, Project, Quiz
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    grade = Column(String(10), nullable=False, index=True)              # A, B, C, D
    submission_status = Column(String(50), nullable=False, index=True)  # Submitted, Late, Missing
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="assessments")


class FeePayment(Base):
    __tablename__ = "fee_payments"

    payment_id = Column(String(50), primary_key=True, index=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False, index=True)    # UPI, Card, Cash, Bank Transfer
    payment_status = Column(String(50), nullable=False, index=True)    # Paid, Pending, Failed
    installment_no = Column(Integer, nullable=False)
    receipt_no = Column(String(50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="fee_payments")


class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(100), nullable=True)
    student_count = Column(Integer, default=0)
    enrollment_count = Column(Integer, default=0)
    attendance_count = Column(Integer, default=0)
    assessment_count = Column(Integer, default=0)
    payment_count = Column(Integer, default=0)
    status = Column(String(50), default="Imported")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), default="Admin")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String(50), primary_key=True, index=True)  # UUID
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="RUNNING")          # RUNNING, COMPLETED, FAILED
    total_agents = Column(Integer, default=6)
    completed_agents = Column(Integer, default=0)
    verification_status = Column(String(50), default="PENDING")  # APPROVED, REJECTED, WARNING
    raw_metrics = Column(JSON, nullable=True)
    executive_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    agent_logs = relationship("AgentExecutionLog", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("AIRecommendation", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="analysis", cascade="all, delete-orphan")


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(50), ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    agent_role = Column(String(150), nullable=False)
    status = Column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED
    start_time = Column(DateTime, default=datetime.utcnow)
    completion_time = Column(DateTime, nullable=True)
    input_context = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    structured_output = Column(JSON, nullable=True)
    verification_status = Column(String(50), default="VERIFIED")

    analysis = relationship("AnalysisHistory", back_populates="agent_logs")


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(50), ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_source = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # Academic, Financial, Operational, Retention, Course
    problem_identified = Column(Text, nullable=False)
    dataset_evidence = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    expected_benefit = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    confidence_level = Column(Float, default=0.90)
    status = Column(String(50), default="PENDING")   # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("AnalysisHistory", back_populates="recommendations")
    approvals = relationship("ApprovalHistory", back_populates="recommendation", cascade="all, delete-orphan")


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("ai_recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reviewer_name = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # APPROVED, REJECTED
    manager_comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("AIRecommendation", back_populates="approvals")
    user = relationship("User", back_populates="approvals")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(50), ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=True, index=True)
    report_title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String(100), default="Admin")

    analysis = relationship("AnalysisHistory", back_populates="reports")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(50), default="Admin")  # Admin, Manager, Faculty
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    approvals = relationship("ApprovalHistory", back_populates="user")
