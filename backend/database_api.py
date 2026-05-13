import sqlite3
import os
import time

# -----------------------------
# PATH FIX (RENDER SAFE)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "attendance.db")

os.makedirs(DB_DIR, exist_ok=True)


# -----------------------------
# CONNECTION
# -----------------------------
def connect_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# -----------------------------
# INIT DB (SAFE + COMPLETE)
# -----------------------------
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # STUDENTS TABLE (🔥 FIX ADDED)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ATTENDANCE TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)

    # ACADEMIC ATTENDANCE TABLE
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

    # COLLEGE ATTENDANCE (used in dashboard)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            subject_name TEXT,
            teacher_name TEXT,
            session_id TEXT,
            attendance_date TEXT,
            status TEXT
        )
    """)

    # CORPORATE ATTENDANCE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corporate_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            session_id TEXT,
            check_in_time TEXT,
            attendance_date TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


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
# INIT ON IMPORT (SAFE)
# -----------------------------
if __name__ != "__main__":
    init_db()