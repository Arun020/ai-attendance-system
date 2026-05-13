from fastapi import APIRouter, Header, HTTPException
import sqlite3
import os

from backend.auth_jwt import verify_token

router = APIRouter()

# -----------------------------
# DB PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")


# =========================================================
# AUTH + ROLE CHECK
# =========================================================
def require_admin(authorization: str):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]

    payload = verify_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return payload


# =========================================================
# SAFE CONNECTION
# =========================================================
def get_conn():
    return sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)


# =========================================================
# 📊 DEFUALTERS API (SECURED)
# =========================================================
@router.get("/defaulters")
def get_defaulters(authorization: str = Header(None)):

    require_admin(authorization)

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            student_id,
            COUNT(*) as total,
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM college_attendance
        GROUP BY student_id
    """)

    rows = cursor.fetchall()
    conn.close()

    defaulters = []

    for student_id, total, present in rows:

        if total == 0:
            continue

        percentage = round((present / total) * 100, 2)

        if percentage < 75:
            defaulters.append({
                "student_id": student_id,
                "attendance_percentage": percentage
            })

    return {"defaulters": defaulters}


# =========================================================
# 📊 ADMIN STATS (SECURED)
# =========================================================
@router.get("/admin-stats")
def admin_stats(authorization: str = Header(None)):

    require_admin(authorization)

    conn = get_conn()
    cursor = conn.cursor()

    # total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # attendance stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM college_attendance
    """)

    total, present = cursor.fetchone()

    conn.close()

    avg_attendance = 0 if total == 0 else round((present / total) * 100, 2)

    return {
        "total_students": total_students,
        "average_attendance": avg_attendance
    }