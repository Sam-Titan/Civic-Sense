import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Numbers to whitelist
NUMBERS = [
    "9811616513",
    "9873403777",
    "9818442260",
    "9911142522",
    "9818329807",
    "9312246973",
    "9818414623",
    "9466156666",
    "9811706686",
    "9990290909",
    "9810502963",
    "8287646180",
]

def seed_whitelist():
    success = 0
    skipped = 0

    for number in NUMBERS:
        phone = "+91" + number
        doc_ref = db.collection("whitelist").document(phone)
        doc = doc_ref.get()

        if doc.exists and doc.to_dict().get("is_active"):
            print(f"⏭  Skipped (already active): {phone}")
            skipped += 1
            continue

        doc_ref.set({
            "phone_number": phone,
            "added_by": "seed",
            "added_at": datetime.now(timezone.utc),
            "is_active": True
        })

        print(f"✅ Added: {phone}")
        success += 1

    print(f"\nDone. {success} added, {skipped} skipped.")

if __name__ == "__main__":
    seed_whitelist()