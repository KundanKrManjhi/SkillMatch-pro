from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from .config import settings
from .database import db

# PBKDF2 avoids bcrypt's 72-byte password limitation that caused the earlier error.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(password, hashed)
    except (ValueError, TypeError):
        return False

def create_access_token(user_id: str, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": user_id, "role": role, "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    error = HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id or not ObjectId.is_valid(user_id):
            raise error
    except JWTError:
        raise error
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise error
    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return user

async def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
