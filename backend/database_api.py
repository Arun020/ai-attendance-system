import sqlite3
import os
import time

# -----------------------------
# BASE PATH
# -----------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")


# -----------------------------
# SAFE DB CONNECTION
# -----------------------------
def connect_db():

    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False
    )

    # IMPORTANT: prevents locking issues
    conn.execute("PRAGMA journal_mode=WAL;")

    return conn


# -----------------------------
# RETRY SAFE EXECUTION (CRITICAL FIX)
# -----------------------------
def safe_execute(query, params=(), retries=5):

    for attempt in range(retries):

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(query, params)
            conn.commit()
            conn.close()

            return True

        except sqlite3.OperationalError as e:

            if "locked" in str(e).lower():
                time.sleep(0.3)  # wait and retry
                continue

            raise e

    return False


# -----------------------------
# GET ALL ATTENDANCE
# -----------------------------
def get_all_attendance():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return [
        {"id": r[0], "name": r[1], "date": r[2], "time": r[3]}
        for r in rows
    ]


# -----------------------------
# INSERT ATTENDANCE (OLD SYSTEM)
# -----------------------------
def insert_attendance(name, date, time):

    safe_execute(
        "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
        (name, date, time)
    )


# -----------------------------
# GET STUDENT ID BY NAME
# -----------------------------
def get_student_id_by_name(full_name):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT students.id
        FROM students
        INNER JOIN users ON students.user_id = users.id
        WHERE users.full_name = ?
    """, (full_name,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


# -----------------------------
# MARK ACADEMIC ATTENDANCE (FIXED)
# -----------------------------
def mark_academic_attendance(
    student_id,
    subject_id,
    period_id,
    attendance_date,
    status
):

    # prevent duplicate + lock-safe insert
    safe_execute("""
        INSERT INTO academic_attendance (
            student_id,
            subject_id,
            period_id,
            attendance_date,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        subject_id,
        period_id,
        attendance_date,
        status
    ))