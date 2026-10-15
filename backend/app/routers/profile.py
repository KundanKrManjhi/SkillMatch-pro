from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from ..database import db
from ..schemas import ProfileIn
from ..security import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("")
async def get_profile(user=Depends(get_current_user)):
    return user

@router.put("")
async def update_profile(data: ProfileIn, user=Depends(get_current_user)):
    update = data.model_dump()
    update["updated_at"] = datetime.now(timezone.utc)
    await db.users.update_one({"_id": __import__("bson").ObjectId(user["id"])}, {"$set": update})
    await db.audit.insert_one({"type": "profile_update", "user_id": user["id"], "email": user["email"], "created_at": datetime.now(timezone.utc)})
    return {**user, **update}
