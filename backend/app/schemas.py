from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ----------------- Auth & Users -----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "Faculty"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ----------------- Students -----------------
class StudentBase(BaseModel):
    student_id: str
    student_name: str
    age: int
    gender: str
    city: str
    email: str
    admission_date: date
    education_level: str

class StudentOut(StudentBase):
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# ----------------- Enrollments -----------------
class EnrollmentBase(BaseModel):
    enrollment_id: str
    student_id: str
    course: str
    enrollment_date: date
    batch_id: str
    course_fee: float
    enrollment_status: str
    delivery_mode: str

class EnrollmentOut(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Attendance -----------------
class AttendanceBase(BaseModel):
    attendance_id: str
    student_id: str
    batch_id: str
    attendance_date: date
    session_topic: str
    attendance_status: str
    session_duration_minutes: int

class AttendanceOut(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Assessments -----------------
class AssessmentBase(BaseModel):
    assessment_id: str
    student_id: str
    course: str
    assessment_date: date
    assessment_type: str
    score: float
    max_score: float = 100.0
    grade: str
    submission_status: str

class AssessmentOut(AssessmentBase):
    score_percentage: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

# ----------------- Fee Payments -----------------
class FeePaymentBase(BaseModel):
    payment_id: str
    student_id: str
    payment_date: date
    amount: float
    payment_method: str
    payment_status: str
    installment_no: int
    receipt_no: str

class FeePaymentOut(FeePaymentBase):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Student Intelligence & Performance -----------------
class StudentPerformanceOut(BaseModel):
    student: StudentOut
    enrollments: List[EnrollmentOut]
    attendance_count: int
    present_count: int
    late_count: int
    absent_count: int
    attendance_percentage: float
    attendance_risk_level: str   # High Risk (<60%), Medium Risk (60-75%), Normal (>75%)
    assessments_count: int
    average_score: float
    missing_assessments: int
    late_submissions: int
    grades_distribution: Dict[str, int]
    academic_risk_level: str     # High Risk (<50%), Medium Risk (50-69%), Normal (>=70%)
    overall_risk_category: str   # High Risk, Medium Risk, Low Risk
    risk_reasons: List[str]
    total_fee_paid: float
    total_fee_pending: float
    total_fee_failed: float
    payments: List[FeePaymentOut]

# ----------------- Dashboard & KPIs -----------------
class DashboardKPI(BaseModel):
    total_students: int
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    dropped_enrollments: int
    on_hold_enrollments: int
    average_attendance: float
    present_count: int
    late_count: int
    absent_count: int
    average_assessment_score: float
    total_fee_collection: float
    pending_payments: float
    failed_payments: float
    demo_data_notice: str

class ChartDataPoint(BaseModel):
    name: str
    value: Any
    count: Optional[int] = None
    amount: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

class DashboardOverview(BaseModel):
    kpis: DashboardKPI
    charts: Dict[str, List[Dict[str, Any]]]

# ----------------- AI Recommendations & Approval -----------------
class RecommendationOut(BaseModel):
    id: int
    analysis_id: str
    agent_source: str
    category: str
    problem_identified: str
    dataset_evidence: str
    recommended_action: str
    expected_benefit: str
    priority: str
    confidence_level: float
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApprovalDecision(BaseModel):
    comments: Optional[str] = ""

class ApprovalHistoryOut(BaseModel):
    id: int
    recommendation_id: int
    reviewer_name: str
    action: str
    manager_comments: Optional[str]
    reviewed_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Multi-Agent Orchestration -----------------
class AgentExecutionLogOut(BaseModel):
    id: int
    analysis_id: str
    agent_name: str
    agent_role: str
    status: str
    start_time: datetime
    completion_time: Optional[datetime] = None
    input_context: Optional[str] = None
    output_summary: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    verification_status: str
    model_config = ConfigDict(from_attributes=True)

class AnalysisHistoryOut(BaseModel):
    id: str
    title: str
    status: str
    total_agents: int
    completed_agents: int
    verification_status: str
    raw_metrics: Optional[Dict[str, Any]] = None
    executive_summary: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    agent_logs: Optional[List[AgentExecutionLogOut]] = None
    recommendations: Optional[List[RecommendationOut]] = None
    model_config = ConfigDict(from_attributes=True)

# ----------------- Chatbot -----------------
class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    answer: str
    evidence_query: Optional[str] = None
    calculated_data: Optional[Dict[str, Any]] = None
    suggested_followups: Optional[List[str]] = []

# ----------------- Reports -----------------
class ReportCreate(BaseModel):
    analysis_id: Optional[str] = None
    report_title: Optional[str] = "Comprehensive Education Intelligence Report"

class GeneratedReportOut(BaseModel):
    id: int
    analysis_id: Optional[str]
    report_title: str
    filename: str
    file_size: int
    generated_at: datetime
    generated_by: str
    download_url: str
    model_config = ConfigDict(from_attributes=True)

# ----------------- Dataset Upload & Preview -----------------
class SheetPreview(BaseModel):
    sheet_name: str
    row_count: int
    columns: List[str]
    dtypes: Dict[str, str]
    sample_data: List[Dict[str, Any]]

class DatasetValidationReport(BaseModel):
    is_valid: bool
    filename: str
    sheets_found: List[str]
    missing_sheets: List[str]
    record_counts: Dict[str, int]
    column_checks: Dict[str, bool]
    foreign_key_errors: List[str]
    warnings: List[str]
    errors: List[str]
    previews: List[SheetPreview]

class UploadedDatasetOut(BaseModel):
    id: int
    filename: str
    file_size: int
    student_count: int
    enrollment_count: int
    attendance_count: int
    assessment_count: int
    payment_count: int
    status: str
    uploaded_at: datetime
    uploaded_by: str
    model_config = ConfigDict(from_attributes=True)
