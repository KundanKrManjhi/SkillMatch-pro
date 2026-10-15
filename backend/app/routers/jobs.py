from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
from bson import ObjectId
from ..database import db
from ..schemas import JobIn
from ..security import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])
def serialize(d):
    d["id"] = str(d.pop("_id")); return d

@router.get("")
async def list_jobs(q: str = "", location: str = "", limit: int = Query(100, ge=1, le=200)):
    query = {"active": {"$ne": False}}
    docs = await db.jobs.find(query).sort("created_at", -1).to_list(limit)
    if q:
        term=q.lower(); docs=[d for d in docs if term in (d.get("title","")+" "+d.get("company","")+" "+" ".join(d.get("skills",[]))).lower()]
    if location: docs=[d for d in docs if location.lower() in d.get("location","").lower()]
    return [serialize(d) for d in docs]

@router.post("/{job_id}/apply")
async def apply(job_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(job_id): raise HTTPException(404,"Job not found")
    job=await db.jobs.find_one({"_id":ObjectId(job_id),"active":{"$ne":False}})
    if not job: raise HTTPException(404,"Job not found")
    if await db.applications.find_one({"job_id":job_id,"user_id":user["id"]}): raise HTTPException(409,"You already applied to this job")
    resume=await db.resumes.find_one({"user_id":user["id"]},sort=[("uploaded_at",-1)])
    app={"job_id":job_id,"job_title":job["title"],"company":job["company"],"user_id":user["id"],"user_name":user["name"],"user_email":user["email"],"resume_score":resume.get("analysis",{}).get("score") if resume else None,"status":"Submitted","created_at":datetime.now(timezone.utc)}
    await db.applications.insert_one(app)
    await db.audit.insert_one({"type":"application_submit","user_id":user["id"],"email":user["email"],"job_id":job_id,"created_at":datetime.now(timezone.utc)})
    return {"message":"Application submitted successfully","status":app["status"]}

@router.get("/my/applications")
async def my_applications(user=Depends(get_current_user)):
    docs=await db.applications.find({"user_id":user["id"]}).sort("created_at",-1).to_list(200)
    return [serialize(d) for d in docs]

@router.get("/my/saved")
async def saved_jobs(user=Depends(get_current_user)):
    docs=await db.saved_jobs.find({"user_id":user["id"]}).to_list(200)
    return [d.get("job_id") for d in docs]

@router.post("/{job_id}/save")
async def save_job(job_id: str,user=Depends(get_current_user)):
    if not ObjectId.is_valid(job_id) or not await db.jobs.find_one({"_id":ObjectId(job_id)}): raise HTTPException(404,"Job not found")
    await db.saved_jobs.update_one({"user_id":user["id"],"job_id":job_id},{"$setOnInsert":{"user_id":user["id"],"job_id":job_id,"created_at":datetime.now(timezone.utc)}},upsert=True)
    return {"message":"Job saved"}
