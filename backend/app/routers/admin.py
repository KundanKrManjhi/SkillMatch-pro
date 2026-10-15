from datetime import datetime, timezone
import re

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from ..database import db
from ..schemas import JobIn, CompanyIn
from ..security import require_admin


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


def clean(document: dict) -> dict:
    """Convert MongoDB ObjectId to a JSON-compatible string."""
    document["id"] = str(document.pop("_id"))
    return document


def escaped_name(name: str) -> str:
    """Safely match a company name using a case-insensitive regex."""
    return "^" + re.escape(name.strip()) + "$"


# --------------------------------------------------
# ADMIN OVERVIEW
# --------------------------------------------------

@router.get("/overview")
async def overview(admin=Depends(require_admin)):
    return {
        "registered_users": await db.users.count_documents(
            {"role": "user"}
        ),
        "active_jobs": await db.jobs.count_documents(
            {"active": {"$ne": False}}
        ),
        "applications": await db.applications.count_documents({}),
        "companies": await db.companies.count_documents({}),
        "resume_uploads": await db.resumes.count_documents({}),
        "form_submissions": await db.audit.count_documents({
            "type": {
                "$in": [
                    "registration",
                    "profile_update",
                    "resume_upload",
                    "application_submit",
                    "support_ticket",
                ]
            }
        }),
        "support_tickets": await db.tickets.count_documents({
            "status": {"$ne": "Closed"}
        }),
    }


# --------------------------------------------------
# USERS
# --------------------------------------------------

@router.get("/users")
async def users(admin=Depends(require_admin)):
    result = []

    cursor = (
        db.users.find({}, {"password_hash": 0})
        .sort("created_at", -1)
        .limit(500)
    )

    async for user in cursor:
        user["id"] = str(user.pop("_id"))
        result.append(user)

    return result


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

@router.get("/applications")
async def applications(admin=Depends(require_admin)):
    result = []

    cursor = (
        db.applications.find({})
        .sort("created_at", -1)
        .limit(500)
    )

    async for document in cursor:
        result.append(clean(document))

    return result


@router.patch("/applications/{app_id}")
async def update_application(
    app_id: str,
    status: str,
    admin=Depends(require_admin),
):
    allowed_statuses = [
        "Submitted",
        "Under Review",
        "Shortlisted",
        "Rejected",
        "Hired",
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(allowed_statuses)}",
        )

    if not ObjectId.is_valid(app_id):
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    result = await db.applications.update_one(
        {"_id": ObjectId(app_id)},
        {
            "$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {"message": "Application status updated"}


# --------------------------------------------------
# COMPANIES
# --------------------------------------------------

@router.get("/companies")
async def companies(admin=Depends(require_admin)):
    documents = await (
        db.companies.find({})
        .sort("created_at", -1)
        .to_list(length=300)
    )

    return [clean(document) for document in documents]


@router.post("/companies", status_code=201)
async def add_company(
    data: CompanyIn,
    admin=Depends(require_admin),
):
    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Company name cannot be empty",
        )

    existing = await db.companies.find_one({
        "name": {
            "$regex": escaped_name(name),
            "$options": "i",
        }
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Company already exists",
        )

    document = {
        **data.model_dump(),
        "name": name,
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.companies.insert_one(document)

    return {
        "id": str(result.inserted_id),
        **document,
    }


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: str,
    admin=Depends(require_admin),
):
    if not ObjectId.is_valid(company_id):
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    result = await db.companies.delete_one({
        "_id": ObjectId(company_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return {"message": "Company deleted"}


# --------------------------------------------------
# JOB LISTINGS
# --------------------------------------------------

@router.post("/jobs", status_code=201)
async def add_job(
    data: JobIn,
    admin=Depends(require_admin),
):
    company_name = data.company.strip()

    if not company_name:
        raise HTTPException(
            status_code=422,
            detail="Company name cannot be empty",
        )

    existing_company = await db.companies.find_one({
        "name": {
            "$regex": escaped_name(company_name),
            "$options": "i",
        }
    })

    if not existing_company:
        await db.companies.insert_one({
            "name": company_name,
            "industry": "Technology",
            "location": data.location,
            "website": "",
            "description": "Added automatically with a job listing",
            "created_at": datetime.now(timezone.utc),
        })

    document = {
        **data.model_dump(),
        "company": company_name,
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.jobs.insert_one(document)

    return {
        "id": str(result.inserted_id),
        **document,
    }


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    admin=Depends(require_admin),
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    result = await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"active": False}},
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {"message": "Job deactivated"}


# --------------------------------------------------
# ADMIN ACTIVITY
# --------------------------------------------------

@router.get("/activity")
async def activity(admin=Depends(require_admin)):
    documents = await (
        db.audit.find({})
        .sort("created_at", -1)
        .to_list(length=250)
    )

    for document in documents:
        document["id"] = str(document.pop("_id"))

    return documents