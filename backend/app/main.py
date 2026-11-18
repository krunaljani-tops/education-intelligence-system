import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.auth import seed_default_users
from backend.app.excel_importer import import_excel_to_db
from backend.app.models import Student, AnalysisHistory
from backend.app.agents.crew import EducationMultiAgentCrew

# Routers
from backend.app.routers.auth import router as auth_router
from backend.app.routers.datasets import router as datasets_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.students import router as students_router
from backend.app.routers.enrollments import router as enrollments_router
from backend.app.routers.attendance import router as attendance_router
from backend.app.routers.assessments import router as assessments_router
from backend.app.routers.finance import router as finance_router
from backend.app.routers.agents import router as agents_router
from backend.app.routers.chat import router as chat_router
from backend.app.routers.recommendations import router as recommendations_router
from backend.app.routers.reports import router as reports_router
from backend.app.routers.history import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables
    print("[Startup] Initializing Database Schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed default users
        print("[Startup] Seeding initial admin/manager/faculty accounts...")
        seed_default_users(db)

        # Check if actual dataset should be loaded
        student_count = db.query(Student).count()
        if student_count == 0 and os.path.exists(settings.EXCEL_FILE_PATH):
            print(f"[Startup] Importing actual dataset from '{settings.EXCEL_FILE_PATH}'...")
            success, msg, counts = import_excel_to_db(settings.EXCEL_FILE_PATH, db, uploaded_by="System Initializer")
            print(f"[Startup] Dataset Ingestion Result: {msg}")

            # Run baseline multi-agent analysis so dashboards and recommendations have live initial data
            existing_runs = db.query(AnalysisHistory).count()
            if existing_runs == 0:
                print("[Startup] Executing baseline 6-Agent Collaborative Intelligence run...")
                crew = EducationMultiAgentCrew(db)
                crew.execute_workflow(title="Baseline Institute Multi-Agent Analysis")
                print("[Startup] Baseline Multi-Agent run completed and verified successfully.")
    except Exception as e:
        print(f"[Startup Warning] Initialization encountered: {e}")
    finally:
        db.close()

    yield
    print("[Shutdown] Cleaning up application resources...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-Stack Multi-Agent AI Application for Education Business Intelligence and Student Performance Analysis.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Reports
if os.path.exists(settings.REPORTS_DIR):
    app.mount("/static/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")

# Register API Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(students_router, prefix=settings.API_PREFIX)
app.include_router(enrollments_router, prefix=settings.API_PREFIX)
app.include_router(attendance_router, prefix=settings.API_PREFIX)
app.include_router(assessments_router, prefix=settings.API_PREFIX)
app.include_router(finance_router, prefix=settings.API_PREFIX)
app.include_router(agents_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(recommendations_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "classification": settings.DEMO_DATA_LABEL
    }
