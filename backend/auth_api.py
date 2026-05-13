from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
import os

from utils.security_utils import hash_password, verify_password
from backend.auth_jwt import create_token

router = APIRouter()

# -----------------------------
# DATABASE PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")


# -----------------------------
# REQUEST MODELS
# -----------------------------
class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


# -----------------------------
# REGISTER USER
# -----------------------------
@router.post("/register")
def register_user(data: RegisterRequest):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (data.email,))
    if cursor.fetchone():
        conn.close()
        return {"message": "Email already exists"}

    # Hash password
    hashed_password = hash_password(data.password)

    # Insert user
    cursor.execute("""
        INSERT INTO users (full_name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        data.full_name,
        data.email,
        hashed_password,
        data.role
    ))

    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}


# -----------------------------
# LOGIN USER (JWT ENABLED)
# -----------------------------
@router.post("/login")
def login_user(data: LoginRequest):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✔ EMAIL-BASED LOGIN (matches DB schema)
    cursor.execute("""
        SELECT id, full_name, email, password, role
        FROM users
        WHERE email = ?
    """, (data.email,))

    user = cursor.fetchone()
    conn.close()

    # If user not found
    if not user:
        return {"message": "Invalid user"}

    user_id, full_name, email, hashed_password, role = user

    # Verify password
    if not verify_password(data.password, hashed_password):
        return {"message": "Invalid password"}

    # Create JWT token
    token = create_token({
        "sub": email,
        "role": role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role
    }