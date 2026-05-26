from fastapi import HTTPException, Cookie
from core.redis import redis_client
from core.firebase import db
import json

async def get_session(session_id:str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail= "Not logged in")
    
    data = redis_client.get(f"session:{session_id}")

    if not data:
        raise HTTPException(status_code=401, detail= "Session Expired, please log in again")
    return json.loads(data)

async def require_admin(session_id:str = Cookie(None)):
    session = await get_session(session_id)
    if session["role"] != "rwa_admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return session

async def check_whitelist(phone_number: str):
    doc = db.collection("whitelist").document(phone_number).get()

    if not doc.exists:
        raise HTTPException(status_code=403, detail="Phone number not approved by RWA")

    if not doc.to_dict().get("is_active", False):
        raise HTTPException(status_code=403, detail="Account has been deactivated")
