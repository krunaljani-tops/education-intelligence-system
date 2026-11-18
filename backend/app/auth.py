import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pw_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}. Your role is '{current_user.role}'."
            )
        return current_user
    return role_checker

def seed_default_users(db: Session):
    """Seed initial demo users: Admin, Manager, Faculty if none exist."""
    users_data = [
        {"username": "admin", "email": "admin@edu-intelligence.ai", "full_name": "Senior Administrator", "role": "Admin", "password": "AdminPassword123!"},
        {"username": "manager", "email": "manager@edu-intelligence.ai", "full_name": "Operations Manager", "role": "Manager", "password": "ManagerPassword123!"},
        {"username": "faculty", "email": "faculty@edu-intelligence.ai", "full_name": "Academic Faculty Lead", "role": "Faculty", "password": "FacultyPassword123!"},
    ]
    for u in users_data:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            new_user = User(
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                role=u["role"],
                hashed_password=get_password_hash(u["password"]),
                is_active=True
            )
            db.add(new_user)
    db.commit()
