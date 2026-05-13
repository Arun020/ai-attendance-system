import sqlite3
import os

# Base directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "attendance.db"
)


def connect_db():

    conn = sqlite3.connect(DB_PATH)

    return conn


def create_table():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
        """
    )

    conn.commit()

    conn.close()


def attendance_exists(name, date):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM attendance
        WHERE name = ? AND date = ?
        """,
        (name, date)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def insert_attendance(name, date, time):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO attendance (
            name,
            date,
            time
        )
        VALUES (?, ?, ?)
        """,
        (name, date, time)
    )

    conn.commit()

    conn.close()