from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from .config import settings
from .database import client, db
from .security import hash_password
from .routers import auth, profile, resumes, jobs, admin, support


# Create the default admin account if it does not exist
async def create_admin():
    email = settings.admin_email.lower().strip()

    existing = await db.users.find_one({"email": email})

    if existing:
        # Do not overwrite an existing account's password or role
        print(f"Admin email already exists in database: {email}")
        return

    admin_user = {
        "name": settings.admin_name,
        "email": email,
        "password_hash": hash_password(settings.admin_password),
        "role": "admin",
        "education": "",
        "experience": "",
        "skills": [],
        "target_role": "",
        "location": "",
        "created_at": datetime.now(timezone.utc),
    }

    await db.users.insert_one(admin_user)

    print(f"Admin account created successfully: {email}")


# Application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await client.admin.command("ping")
        print("MongoDB connection: OK")

        await create_admin()

    except PyMongoError as exc:
        print(f"MongoDB connection error: {exc}")

    except Exception as exc:
        print(f"Application startup error: {exc}")
        raise

    yield

    client.close()


# Create FastAPI application
app = FastAPI(
    title="SkillMatch Pro API",
    version="2.0.0",
    description="Resume scoring and job matching platform",
    lifespan=lifespan,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        settings.frontend_origin,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
routers = [
    auth.router,
    profile.router,
    resumes.router,
    jobs.router,
    admin.router,
    support.router,
]

for router in routers:
    app.include_router(router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "SkillMatch Pro API is running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/api/health")
async def health():
    try:
        await client.admin.command("ping")

        return {
            "status": "ok",
            "database": "connected",
        }

    except PyMongoError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "database": "disconnected",
                "hint": (
                    "Start MongoDB and check "
                    "MONGODB_URL in backend/.env"
                ),
            },
        )