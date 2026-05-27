from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import auth, users, complaints, admin
import os

load_dotenv()

app = FastAPI(
    title="CivicCollect API",
    description="Community garbage collection complaint management system",
    version="1.0.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "https://your-app-name.onrender.com"  # add after deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(admin.router)

@app.get("/health")
async def root():
    return {"message": "CivicCollect API is running"}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")