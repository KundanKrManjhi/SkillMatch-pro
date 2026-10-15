from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends

from ..database import db
from ..schemas import RegisterIn, LoginIn
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


def public_user(user):
    return {
        "id": str(user.get("_id", user.get("id", ""))),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
    }


@router.post("/register", status_code=201)
async def register(data: RegisterIn):
    email = data.email.lower().strip()

    existing_user = await db.users.find_one({"email": email})

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists. Please sign in."
        )

    user = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "role": "user",
        "education": "",
        "experience": "",
        "skills": [],
        "target_role": "",
        "location": "",
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.users.insert_one(user)
    user["_id"] = result.inserted_id

    await db.audit.insert_one({
        "type": "registration",
        "user_id": str(result.inserted_id),
        "email": email,
        "created_at": datetime.now(timezone.utc),
    })

    return {
        "access_token": create_access_token(
            str(result.inserted_id), "user"
        ),
        "token_type": "bearer",
        "user": public_user(user),
    }


@router.post("/login")
async def login(data: LoginIn):
    email = data.email.lower().strip()

    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Account not found. Please register first."
        )

    stored_hash = user.get("password_hash", "")

    if not stored_hash or not verify_password(
        data.password, stored_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password. Check your password or register a new account."
        )

    await db.audit.insert_one({
        "type": "login",
        "user_id": str(user["_id"]),
        "email": user["email"],
        "created_at": datetime.now(timezone.utc),
    })

    role = user.get("role", "user")

    return {
        "access_token": create_access_token(
            str(user["_id"]), role
        ),
        "token_type": "bearer",
        "user": public_user(user),
    }


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    await db.audit.insert_one({
        "type": "logout",
        "user_id": user["id"],
        "email": user["email"],
        "created_at": datetime.now(timezone.utc),
    })

    return {
        "message": "Logged out. Remove the token on the client."
    }