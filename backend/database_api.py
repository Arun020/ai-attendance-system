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

# Ensure folder exists (Render fix)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# -----------------------------
# CONNECTION
# -----------------------------
def connect_db():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# -----------------------------
# INIT DATABASE (CRITICAL FIX)
# -----------------------------
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE (FIX FOR YOUR ERROR)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            period_id INTEGER,
            attendance_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# AUTO-RUN ON IMPORT (IMPORTANT FIX)
# -----------------------------
init_db()


# -----------------------------
# SAFE EXECUTE
# -----------------------------
def safe_execute(query, params=(), retries=5):
    for _ in range(retries):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                time.sleep(0.3)
                continue
            raise e

    return False


# -----------------------------
# GET ATTENDANCE
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
# INSERT ATTENDANCE
# -----------------------------
def insert_attendance(name, date, time):
    safe_execute(
        "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
        (name, date, time)
    )


# -----------------------------
# GET STUDENT ID
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
# MARK ATTENDANCE
# -----------------------------
def mark_academic_attendance(
    student_id,
    subject_id,
    period_id,
    attendance_date,
    status
):
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