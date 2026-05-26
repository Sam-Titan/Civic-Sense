from fastapi import APIRouter, Depends, HTTPException
from core.firebase import db
from core.security import get_session
from models.user import UserRegister
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
async def register_user(data: UserRegister, session=Depends(get_session)):
    phone_number = session["phone_number"]
    role = session["role"]

    # Prevent duplicate registration
    existing = db.collection("users")\
        .where("phone_number", "==", phone_number)\
        .get()

    if len(existing) > 0:
        return {"message": "User already registered"}

    user_id = str(uuid.uuid4())

    db.collection("users").document(user_id).set({
        "user_id": user_id,
        "phone_number": phone_number,
        "name": data.name,
        "address": data.address,
        "locality": data.locality,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    })

    return {"message": "User registered successfully", "role": role}


@router.get("/me")
async def get_me(session=Depends(get_session)):
    phone_number = session["phone_number"]

    users = db.collection("users")\
        .where("phone_number", "==", phone_number)\
        .get()

    if not users:
        return {"message": "User not found"}

    return users[0].to_dict()