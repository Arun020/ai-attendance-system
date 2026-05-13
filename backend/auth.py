from fastapi import APIRouter, HTTPException

router = APIRouter()

# -----------------------------
# SIMPLE IN-MEMORY USERS (FOR NOW)
# LATER WE CAN MOVE TO DB
# -----------------------------
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "teacher": {
        "password": "teacher123",
        "role": "teacher"
    },
    "hr": {
        "password": "hr123",
        "role": "hr"
    }
}


# =========================================================
# 🔐 LOGIN API
# =========================================================
@router.post("/login")
def login(payload: dict):

    username = payload.get("username")
    password = payload.get("password")

    if username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid user")

    user = USERS[username]

    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Wrong password")

    return {
        "message": "Login successful",
        "role": user["role"],
        "username": username
    }