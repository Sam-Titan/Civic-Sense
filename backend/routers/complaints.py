from fastapi import APIRouter, Depends, HTTPException
from core.firebase import db
from core.security import get_session
from models.complaint import ComplaintCreate
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("")
async def file_complaint(data: ComplaintCreate, session=Depends(get_session)):
    phone_number = session["phone_number"]

    # Fetch user profile for address and locality
    users = db.collection("users")\
        .where("phone_number", "==", phone_number)\
        .get()

    if not users:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Please complete registration first."
        )

    user_data = users[0].to_dict()

    # Block if open complaint already exists
    open_complaints = db.collection("complaints")\
        .where("phone_number", "==", phone_number)\
        .where("status", "in", ["Pending", "Acknowledged"])\
        .get()

    if len(open_complaints) > 0:
        raise HTTPException(
            status_code=400,
            detail="You already have an open complaint. Please wait for it to be resolved."
        )

    complaint_id = str(uuid.uuid4())

    db.collection("complaints").document(complaint_id).set({
        "complaint_id": complaint_id,
        "phone_number": phone_number,
        "address": user_data["address"],
        "locality": user_data["locality"],
        "description": data.description,
        "status": "Pending",
        "created_at": datetime.now(timezone.utc),
        "acknowledged_at": None,
        "resolved_at": None,
        "eta": None,
        "remarks": None
    })

    return {
        "message": "Complaint filed successfully",
        "complaint_id": complaint_id
    }


@router.get("/me")
async def get_my_complaints(session=Depends(get_session)):
    phone_number = session["phone_number"]

    complaints = db.collection("complaints")\
        .where("phone_number", "==", phone_number)\
        .order_by("created_at", direction="DESCENDING")\
        .get()

    result = []
    for c in complaints:
        data = c.to_dict()
        # Convert Firestore timestamps to readable strings
        for field in ["created_at", "acknowledged_at", "resolved_at", "eta"]:
            if data.get(field) and hasattr(data[field], "_seconds"):
                data[field] = datetime.fromtimestamp(
                    data[field]._seconds,
                    tz=timezone.utc
                ).isoformat()
        result.append(data)

    return result


@router.patch("/{complaint_id}/resolve")
async def resolve_complaint(complaint_id: str, session=Depends(get_session)):
    phone_number = session["phone_number"]

    doc_ref = db.collection("complaints").document(complaint_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    data = doc.to_dict()

    # Ensure complaint belongs to this user
    if data["phone_number"] != phone_number:
        raise HTTPException(status_code=403, detail="Not your complaint")

    # Only acknowledged complaints can be resolved
    if data["status"] != "Acknowledged":
        raise HTTPException(
            status_code=400,
            detail="Only acknowledged complaints can be resolved"
        )

    doc_ref.update({
        "status": "Resolved",
        "resolved_at": datetime.now(timezone.utc)
    })

    return {"message": "Complaint marked as resolved"}