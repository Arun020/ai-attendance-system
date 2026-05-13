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
def require_teacher_or_admin(authorization: str):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]

    payload = verify_token(token)

    role = payload.get("role")

    if role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher/Admin access required")

    return payload


# =========================================================
# SAFE DB CONNECTION
# =========================================================
def get_conn():
    return sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)


# =========================================================
# 📅 TEACHER PERIODS (SECURED)
# =========================================================
@router.get("/teacher-periods/{teacher_id}")
def get_teacher_periods(
    teacher_id: int,
    authorization: str = Header(None)
):

    require_teacher_or_admin(authorization)

    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                periods.id,
                subjects.subject_name,
                classes.class_name,
                periods.day_name,
                periods.start_time,
                periods.end_time
            FROM periods
            INNER JOIN subjects ON periods.subject_id = subjects.id
            INNER JOIN classes ON periods.class_id = classes.id
            WHERE periods.teacher_id = ?
        """, (teacher_id,))

        rows = cursor.fetchall()
        conn.close()

        periods = []

        for r in rows:
            periods.append({
                "period_id": r[0],
                "subject_name": r[1],
                "class_name": r[2],
                "day_name": r[3],
                "start_time": r[4],
                "end_time": r[5]
            })

        return {"teacher_periods": periods}

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# 👨‍🎓 CLASS STUDENTS (SECURED)
# =========================================================
@router.get("/class-students/{class_id}")
def get_class_students(
    class_id: int,
    authorization: str = Header(None)
):

    require_teacher_or_admin(authorization)

    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                students.id,
                users.full_name,
                students.roll_number
            FROM students
            INNER JOIN users ON students.user_id = users.id
            WHERE students.class_id = ?
        """, (class_id,))

        rows = cursor.fetchall()
        conn.close()

        students = []

        for r in rows:
            students.append({
                "student_id": r[0],
                "student_name": r[1],
                "roll_number": r[2]
            })

        return {"students": students}

    except Exception as e:
        return {"error": str(e)}