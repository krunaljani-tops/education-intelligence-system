import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Education Business Intelligence System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment & Database
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./education_bi.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "education-intelligence-super-secret-jwt-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI / LLM Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # App Settings
    DEMO_DATA_LABEL: str = "DEMO DATA (Synthetic Dataset: May 1, 2026 - Oct 31, 2026)"
    EXCEL_FILE_PATH: str = os.getenv("EXCEL_FILE_PATH", "02_Education.xlsx")
    REPORTS_DIR: str = os.path.join(os.getcwd(), "backend", "generated_reports")
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "backend", "uploads")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
