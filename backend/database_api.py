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
# INIT DB (FORCED SAFE)
# -----------------------------
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE (FIX YOUR ERROR)
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
# 🔥 CRITICAL FIX (AUTO RUN)
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
