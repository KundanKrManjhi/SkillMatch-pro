from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from bson import ObjectId
from ..database import db
from ..security import get_current_user, require_admin

router=APIRouter(prefix="/api/support",tags=["Support"])
class TicketIn(BaseModel):
    subject:str=Field(min_length=3,max_length=150)
    message:str=Field(min_length=10,max_length=3000)

@router.post("/tickets",status_code=201)
async def create_ticket(data:TicketIn,user=Depends(get_current_user)):
    ticket={**data.model_dump(),"user_id":user["id"],"user_name":user["name"],"email":user["email"],"status":"Open","created_at":datetime.now(timezone.utc)}
    result=await db.tickets.insert_one(ticket)
    await db.audit.insert_one({"type":"support_ticket","user_id":user["id"],"email":user["email"],"created_at":datetime.now(timezone.utc)})
    return {"id":str(result.inserted_id),**ticket}

@router.get("/my-tickets")
async def my_tickets(user=Depends(get_current_user)):
    docs=await db.tickets.find({"user_id":user["id"]}).sort("created_at",-1).to_list(100)
    for d in docs: d["id"]=str(d.pop("_id"))
    return docs

@router.get("/admin/tickets")
async def all_tickets(admin=Depends(require_admin)):
    docs=await db.tickets.find({}).sort("created_at",-1).to_list(300)
    for d in docs: d["id"]=str(d.pop("_id"))
    return docs

@router.patch("/admin/tickets/{ticket_id}")
async def ticket_status(ticket_id:str,status:str,admin=Depends(require_admin)):
    if status not in ["Open","In Progress","Closed"]: raise HTTPException(400,"Invalid status")
    if not ObjectId.is_valid(ticket_id): raise HTTPException(404,"Ticket not found")
    result=await db.tickets.update_one({"_id":ObjectId(ticket_id)},{"$set":{"status":status,"updated_at":datetime.now(timezone.utc)}})
    if not result.matched_count: raise HTTPException(404,"Ticket not found")
    return {"message":"Ticket updated"}
