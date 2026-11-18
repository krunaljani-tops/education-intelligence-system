# AI-Powered Education Business Intelligence & Student Performance System

A production-ready, full-stack multi-agent AI application built for educational training institutes, powered by the actual `02_Education.xlsx` dataset.

[![Test Status](https://img.shields.io/badge/Pytest-18%20Passed%20(100%25)-emerald.svg)](#qa-testing-results)
[![Backend](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/React.js-18.0-61DAFB.svg)](https://react.dev)
[![Multi--Agent](https://img.shields.io/badge/CrewAI%20Architecture-6%20Agents-blueviolet.svg)](#multi-agent-system)
[![Dataset](https://img.shields.io/badge/Dataset-02__Education.xlsx-blue.svg)](#dataset-specifications)
[![Deploy Netlify](https://img.shields.io/badge/Deploy-Netlify-00C7B7.svg)](https://www.netlify.com)
[![Deploy Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com)

---

## 1. System Overview & Technology Stack

- **Frontend:** React.js, Tailwind CSS (v4), Recharts, Axios, Lucide Icons, Vite
- **Backend:** Python 3.11, FastAPI, Pandas, NumPy, Pydantic (v2), SQLAlchemy
- **Multi-Agent AI:** Six Collaborative Agents (CrewAI Architecture) with Gemini API / OpenAI / Offline Deterministic Analytics Engine
- **Database:** PostgreSQL 17 (with automated SQLite fallback for local developer agility)
- **Security & Governance:** JWT Bearer Authentication, Bcrypt password hashing, Role-Based Access Control (`Admin`, `Manager`, `Faculty`)
- **Reporting Engine:** ReportLab Multi-page Executive PDF Report Generator

---

## 2. Dataset Specifications (`02_Education.xlsx`)

The system directly ingests and validates the five operational worksheets from `02_Education.xlsx`:

| Sheet Name | Records | Key Columns | Business Rules & Calculated Metrics |
| :--- | :--- | :--- | :--- |
| **Students** | 1,200 | `student_id`, `student_name`, `age`, `gender`, `city`, `email`, `admission_date`, `education_level` | Demographics, 10 cities, age distribution, education levels |
| **Enrollments** | 1,600 | `enrollment_id`, `student_id`, `course`, `enrollment_date`, `batch_id`, `course_fee`, `enrollment_status`, `delivery_mode` | 8 Programs, 45 Batches, Active (393), Completed (406), Dropped (383), On Hold (418) |
| **Attendance** | 2,500 | `attendance_id`, `student_id`, `batch_id`, `attendance_date`, `session_topic`, `attendance_status`, `session_duration_minutes` | Formula: `(Present / Total) * 100 = 77.76%`. Late (164) tracked discretely from Present (1,944) |
| **Assessments** | 1,800 | `assessment_id`, `student_id`, `course`, `assessment_date`, `assessment_type`, `score`, `max_score`, `grade`, `submission_status` | Score Average: 63.15%. Grade distribution (A, B, C, D). Missing submissions (273) tracked |
| **Fee_Payments** | 1,200 | `payment_id`, `student_id`, `payment_date`, `amount`, `payment_method`, `payment_status`, `installment_no`, `receipt_no` | Strict Rule: Only **Paid** (₹7,637,309.78) counted as revenue. Pending (₹3,862,177.04) and Failed (₹3,660,803.97) tracked separately |
| **README** | 6 | `Field`, `Details` | Classification: Synthetic Demo Data (2026-05-01 to 2026-10-31), Currency: INR (₹) |

---

## 3. Six Collaborative AI Agents

1. **Agent 1: Student Data Analyst Agent**  
   Audits unique student profiles, age brackets, gender diversity, and geographic concentration across 10 cities.
2. **Agent 2: Admission & Course Analytics Agent**  
   Ranks 8 programs by popularity, analyzes delivery modes (Hybrid, Offline, Online), and tracks the 23.9% dropout rate.
3. **Agent 3: Finance Agent**  
   Reconciles ₹7.64M Paid revenue, monitors ₹3.86M pending installments, and identifies ₹3.66M gateway failure liabilities.
4. **Agent 4: Academic Performance & Operations Agent**  
   Monitors classroom presence (77.76%), lateness patterns across 7 session topics, and audits 1,800 assessment scores.
5. **Agent 5: Education Strategy Agent**  
   Synthesizes domain outputs into actionable institutional recommendations with evidence, priority, and expected ROI.
6. **Agent 6: Verification Agent**  
   Cross-references all mathematical metrics directly against database SQL queries, ensuring zero hallucination.

---

## 4. Default Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `AdminPassword123!` | Full control, Excel uploads, trigger multi-agent runs, user management |
| **Manager** | `manager` | `ManagerPassword123!` | Dashboards, view agent findings, approve/reject recommendations |
| **Faculty** | `faculty` | `FacultyPassword123!` | Student profiles, attendance, and assessment analytics |

---

## 5. Exact Windows Installation & Execution Commands

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm
- PostgreSQL 14+ (optional, SQLite fallback built-in)

### Step 1: Clone and Enter Directory
```powershell
cd c:\Users\user\Downloads\education-intelligence-system
```

### Step 2: Backend Setup
```powershell
# Create virtual environment (if not already created)
python -m venv backend/venv

# Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r backend/requirements.txt

# Run backend automated tests
python -m pytest -o pythonpath=. backend/tests -v

# Start FastAPI server on port 8000
python backend/run.py
```
*Backend Swagger Docs will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)*

### Step 3: Frontend Setup (Open a second terminal)
```powershell
cd c:\Users\user\Downloads\education-intelligence-system\frontend

# Install frontend dependencies
npm.cmd install

# Start Vite React development server
npm.cmd run dev
```
*Frontend will be live at: [http://localhost:5173](http://localhost:5173)*

---

## 6. Deployment Instructions (Netlify & Render)

### Deploying Frontend to Netlify
1. Connect your repository to Netlify.
2. Set **Base directory**: `frontend`
3. Set **Build command**: `npm run build`
4. Set **Publish directory**: `frontend/dist`
5. Under **Environment variables**, add:
   - `VITE_API_URL`: Your deployed Render backend URL (e.g., `https://education-bi-backend.onrender.com/api`)
6. The included `frontend/netlify.toml` automatically configures single-page application redirects.

### Deploying Backend to Render
1. Create a new **Web Service** on Render from your GitHub repository.
2. Select **Blueprint** using the included `render.yaml` or manual configuration:
   - **Root directory**: `.`
   - **Environment**: `Python 3`
   - **Build command**: `pip install -r backend/requirements.txt`
   - **Start command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Health check path**: `/api/health`
3. Attach a **Render PostgreSQL** database instance and set:
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>/<database>`
   - `SECRET_KEY`: `<your-random-jwt-secret>`
   - `GEMINI_API_KEY`: `<optional-gemini-key>`

---

## 7. QA Testing Results

The automated Pytest suite validates all critical system functionalities with **100% PASS** rate:
```text
backend/tests/test_agents.py::test_multi_agent_execution PASSED
backend/tests/test_agents.py::test_analysis_logs_and_verification PASSED
backend/tests/test_approvals.py::test_recommendation_approval_workflow PASSED
backend/tests/test_approvals.py::test_recommendation_rejection_workflow PASSED
backend/tests/test_auth.py::test_health_check PASSED
backend/tests/test_auth.py::test_login_success PASSED
backend/tests/test_auth.py::test_login_invalid_password PASSED
backend/tests/test_auth.py::test_get_me PASSED
backend/tests/test_auth.py::test_role_based_access PASSED
backend/tests/test_auth.py::test_register_new_user PASSED
backend/tests/test_calculations.py::test_dashboard_kpis_exact_values PASSED
backend/tests/test_calculations.py::test_attendance_calculation_rules PASSED
backend/tests/test_calculations.py::test_finance_calculation_rules PASSED
backend/tests/test_calculations.py::test_student_performance_and_risk PASSED
backend/tests/test_excel_import.py::test_excel_validation PASSED
backend/tests/test_excel_import.py::test_dataset_preview PASSED
backend/tests/test_excel_import.py::test_import_already_imported PASSED
backend/tests/test_reports.py::test_pdf_report_generation_and_download PASSED

======================= 18 passed in 5.92s ========================
```
See [TEST_EXECUTION_REPORT.md](TEST_EXECUTION_REPORT.md) for detailed test audit logs.
