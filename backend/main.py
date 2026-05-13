from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

from backend.auth_api import router as auth_router
from backend.admin_api import router as admin_router
from backend.teacher_api import router as teacher_router
from backend.attendance_api import router as attendance_router

from backend.database_api import init_db

app = FastAPI(
    title="AI Attendance API",
    version="1.0.0"
)


# OPTIONAL (safe double init)
@app.on_event("startup")
def startup():
    init_db()


security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(teacher_router)
app.include_router(attendance_router)


@app.get("/")
def home():
    return {"message": "AI Attendance API Running", "status": "healthy"}