from fastapi import APIRouter, Depends, HTTPException
from core.firebase import db
from core.security import require_admin
from models.complaint import ComplaintAcknowledge, ComplaintRemark
from models.whitelist import WhitelistAdd
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- Complaint Management ---

@router.get("/complaints")
async def get_all_complaints(session=Depends(require_admin)):
    complaints = db.collection("complaints")\
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


@router.patch("/complaints/{complaint_id}/acknowledge")
async def acknowledge_complaint(
    complaint_id: str,
    data: ComplaintAcknowledge,
    session=Depends(require_admin)
):
    doc_ref = db.collection("complaints").document(complaint_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if doc.to_dict()["status"] != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending complaints can be acknowledged"
        )

    doc_ref.update({
        "status": "Acknowledged",
        "acknowledged_at": datetime.now(timezone.utc),
        "eta": data.eta
    })

    return {"message": "Complaint acknowledged"}


@router.patch("/complaints/{complaint_id}/remarks")
async def add_remarks(
    complaint_id: str,
    data: ComplaintRemark,
    session=Depends(require_admin)
):
    doc_ref = db.collection("complaints").document(complaint_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if doc.to_dict()["status"] == "Resolved":
        raise HTTPException(
            status_code=400,
            detail="Cannot add remarks to a resolved complaint"
        )

    doc_ref.update({
        "remarks": data.remarks
    })

    return {"message": "Remarks added successfully"}


# --- Whitelist Management ---

@router.get("/whitelist")
async def get_whitelist(session=Depends(require_admin)):
    entries = db.collection("whitelist").get()
    return [e.to_dict() for e in entries]


@router.post("/whitelist")
async def add_to_whitelist(data: WhitelistAdd, session=Depends(require_admin)):
    doc_ref = db.collection("whitelist").document(data.phone_number)
    doc = doc_ref.get()

    if doc.exists and doc.to_dict().get("is_active"):
        raise HTTPException(
            status_code=400,
            detail="Phone number already whitelisted and active"
        )

    # If exists but deactivated, reactivate it
    if doc.exists and not doc.to_dict().get("is_active"):
        doc_ref.update({
            "is_active": True,
            "added_by": data.added_by,
            "added_at": datetime.now(timezone.utc)
        })
        return {"message": "Phone number reactivated"}

    # New entry
    doc_ref.set({
        "phone_number": data.phone_number,
        "added_by": data.added_by,
        "added_at": datetime.now(timezone.utc),
        "is_active": True
    })

    return {"message": "Phone number added to whitelist"}


@router.delete("/whitelist/{phone_number}")
async def remove_from_whitelist(
    phone_number: str,
    session=Depends(require_admin)
):
    doc_ref = db.collection("whitelist").document(phone_number)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Phone number not found in whitelist"
        )

    if not doc.to_dict().get("is_active"):
        raise HTTPException(
            status_code=400,
            detail="Phone number is already deactivated"
        )

    doc_ref.update({
        "is_active": False
    })

    return {"message": "Phone number deactivated"}