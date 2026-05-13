from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

from backend.auth_api import router as auth_router
from backend.admin_api import router as admin_router
from backend.teacher_api import router as teacher_router
from backend.attendance_api import router as attendance_router

# -----------------------------
# APP INIT
# -----------------------------
app = FastAPI(
    title="AI Attendance API",
    version="1.0.0"
)

# -----------------------------
# JWT SCHEME
# -----------------------------
security = HTTPBearer()

# -----------------------------
# CORS CONFIG
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTERS (IMPORTANT FIX)
# -----------------------------
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(teacher_router)

# IMPORTANT: give prefix to avoid confusion
app.include_router(attendance_router, prefix="")

# -----------------------------
# OPENAPI FIX
# -----------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Attendance API",
        version="1.0.0",
        description="AI Attendance System with JWT Authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "AI Attendance API Running",
        "status": "healthy"
    }
