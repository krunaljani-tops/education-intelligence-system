import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

db_url = settings.DATABASE_URL
# Handle Render PostgreSQL URL prefix compatibility
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(db_url, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f"[Database Warning] Failed to connect to {db_url}: {e}. Falling back to SQLite.")
    fallback_url = "sqlite:///./education_bi.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
