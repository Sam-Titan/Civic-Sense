import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv()

cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()