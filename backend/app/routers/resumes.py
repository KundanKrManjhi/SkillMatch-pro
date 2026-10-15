from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
import fitz, re
from ..database import db
from ..security import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["Resume"])
MIN_SIZE = 20 * 1024
MAX_SIZE = 10 * 1024 * 1024
SKILL_WORDS = ["python", "java", "javascript", "typescript", "react", "node.js", "fastapi", "django", "flask", "mongodb", "sql", "mysql", "postgresql", "html", "css", "tailwind", "git", "github", "docker", "aws", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "data structures", "algorithms", "rest api", "express", "c++", "c", "kotlin", "communication", "leadership"]

def analyze_text(text: str):
    lower = text.lower()
    skills = sorted({s for s in SKILL_WORDS if s in lower})
    sections = {"education": bool(re.search(r"education|university|college|b\.tech|bachelor|degree", lower)), "experience": bool(re.search(r"experience|internship|employment|work history", lower)), "projects": "project" in lower, "skills": "skill" in lower, "contact": bool(re.search(r"@|\+?\d[\d ()-]{7,}", text))}
    checks = sum(sections.values())
    score = min(100, round((checks / len(sections)) * 65 + min(len(skills), 7) * 5))
    suggestions = []
    if not sections["contact"]: suggestions.append("Add a professional email and phone number.")
    if not sections["education"]: suggestions.append("Add an Education section with degree, institute and graduation year.")
    if not sections["experience"]: suggestions.append("Add internship or practical experience; quantify your impact where possible.")
    if not sections["projects"]: suggestions.append("Add 2–3 projects with technologies, your contribution and measurable outcomes.")
    if not sections["skills"]: suggestions.append("Add a clear Skills section tailored to the target job.")
    if len(skills) < 5: suggestions.append("Mention relevant technical skills explicitly so screening systems can identify them.")
    suggestions.append("Use concise bullet points and action verbs; do not add skills or experience you do not have.")
    return {"score": score, "skills": skills, "sections": sections, "suggestions": suggestions, "word_count": len(text.split())}

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF resumes are accepted")
    raw = await file.read(MAX_SIZE + 1)
    if len(raw) > MAX_SIZE: raise HTTPException(413, "PDF must be 10 MB or smaller")
    if len(raw) < MIN_SIZE: raise HTTPException(400, "PDF must be at least 20 KB")
    if not raw.startswith(b"%PDF-"): raise HTTPException(400, "The uploaded file is not a valid PDF")
    try:
        doc = fitz.open(stream=raw, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception:
        raise HTTPException(400, "Could not read this PDF. Please upload a valid, non-password-protected PDF.")
    if len(text.strip()) < 30: raise HTTPException(400, "No readable text found. Upload a text-based PDF instead of a scanned image PDF.")
    result = analyze_text(text)
    record = {"user_id": user["id"], "filename": file.filename, "size_bytes": len(raw), "analysis": result, "text_preview": text[:12000], "uploaded_at": datetime.now(timezone.utc)}
    inserted = await db.resumes.insert_one(record)
    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": {"latest_resume_id": str(inserted.inserted_id), "resume_score": result["score"], "skills": result["skills"]}})
    await db.audit.insert_one({"type": "resume_upload", "user_id": user["id"], "email": user["email"], "filename": file.filename, "created_at": datetime.now(timezone.utc)})
    return {"id": str(inserted.inserted_id), "filename": file.filename, "size_bytes": len(raw), **result}

@router.get("/latest")
async def latest_resume(user=Depends(get_current_user)):
    doc = await db.resumes.find_one({"user_id": user["id"]}, sort=[("uploaded_at", -1)])
    if not doc: return {"resume": None}
    return {"id": str(doc["_id"]), "filename": doc["filename"], "size_bytes": doc["size_bytes"], "uploaded_at": doc["uploaded_at"], **doc["analysis"]}
