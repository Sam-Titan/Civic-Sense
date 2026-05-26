from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
from core.firebase import db
from core.security import check_whitelist
from core.redis import redis_client
from datetime import datetime, timezone
import os
import uuid
import json

router = APIRouter(prefix="/auth", tags=["Auth"])

RESIDENT_PASSWORD = os.getenv("RESIDENT_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

SESSION_TTL = 60 * 60 * 24  # 24 hours in seconds


class LoginRequest(BaseModel):
    phone_number: str
    password: str
    role: str


@router.post("/login")
async def login(data: LoginRequest, response: Response):
    # Validate role
    if data.role not in ["resident", "rwa_admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check whitelist
    await check_whitelist(data.phone_number)

    # Check password matches role
    expected = ADMIN_PASSWORD if data.role == "rwa_admin" else RESIDENT_PASSWORD
    if data.password != expected:
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Check if user profile exists
    users = db.collection("users")\
        .where("phone_number", "==", data.phone_number)\
        .get()

    is_new_user = len(users) == 0

    # Generate session ID and store in Redis
    session_id = str(uuid.uuid4())
    session_data = json.dumps({
        "phone_number": data.phone_number,
        "role": data.role
    })
    redis_client.setex(f"session:{session_id}", SESSION_TTL, session_data)

    # Set session cookie on browser
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,      # JS cannot read this cookie
        samesite="lax",     # CSRF protection
        max_age=SESSION_TTL
    )

    return {
        "message": "Login successful",
        "role": data.role,
        "is_new_user": is_new_user
    }


@router.post("/logout")
async def logout(response: Response, session_id: str = Cookie(None)):
    # Delete session from Redis
    if session_id:
        redis_client.delete(f"session:{session_id}")

    # Clear cookie from browser
    response.delete_cookie("session_id")

    return {"message": "Logged out successfully"}
