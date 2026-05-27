import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import json

load_dotenv()

IS_PRODUCTION = os.getenv("ENV") == "production"

if IS_PRODUCTION:
    cred_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()