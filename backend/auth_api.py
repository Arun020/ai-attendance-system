from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
import os

from utils.security_utils import hash_password, verify_password
from backend.auth_jwt import create_token

router = APIRouter()

# DB PATH
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
# REGISTER
# -----------------------------
@router.post("/register")
def register_user(data: RegisterRequest):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (data.email,))
    if cursor.fetchone():
        conn.close()
        return {"message": "Email already exists"}

    hashed_password = hash_password(data.password)

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
# LOGIN
# -----------------------------
@router.post("/login")
def login_user(data: LoginRequest):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, full_name, email, password, role
        FROM users
        WHERE email = ?
    """, (data.email,))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"message": "Invalid user"}

    user_id, full_name, email, hashed_password, role = user

    if not verify_password(data.password, hashed_password):
        return {"message": "Invalid password"}

    token = create_token({
        "sub": email,
        "role": role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role
    }