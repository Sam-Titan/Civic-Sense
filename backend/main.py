from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import auth, users, complaints, admin

load_dotenv()

app = FastAPI(
    title="CivicCollect API",
    description="Community garbage collection complaint management system",
    version="1.0.0"
)

# CORS — allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",        # VS Code Live Server
        "http://localhost:5500",         # Live Server alternative
        "https://your-app.netlify.app"   # Replace after deployment
    ],
    allow_credentials=True,             # Allows cookies to be sent
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "CivicCollect API is running"}