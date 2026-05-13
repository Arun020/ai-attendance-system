import sqlite3
import os

# Base directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Database path
DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "attendance.db"
)

# Connect database
conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# -----------------------------
# COMMON TABLES
# -----------------------------

# Users table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE,

        password TEXT,

        role TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)

# Departments table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS departments (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        department_name TEXT UNIQUE
    )
    """
)

# -----------------------------
# ACADEMIC TABLES
# -----------------------------

# Classes table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS classes (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        class_name TEXT,

        semester INTEGER,

        division TEXT
    )
    """
)

# Students table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS students (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        roll_number TEXT,

        class_id INTEGER,

        department_id INTEGER,

        student_email TEXT,

        student_phone TEXT,

        guardian_email TEXT,

        guardian_phone TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(id),

        FOREIGN KEY(class_id)
        REFERENCES classes(id),

        FOREIGN KEY(department_id)
        REFERENCES departments(id)
    )
    """
)

# Teachers table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS teachers (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        department_id INTEGER,

        teacher_code TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(id),

        FOREIGN KEY(department_id)
        REFERENCES departments(id)
    )
    """
)

# Subjects table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS subjects (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        subject_name TEXT,

        subject_code TEXT,

        teacher_id INTEGER,

        class_id INTEGER,

        FOREIGN KEY(teacher_id)
        REFERENCES teachers(id),

        FOREIGN KEY(class_id)
        REFERENCES classes(id)
    )
    """
)

# Periods table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS periods (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        class_id INTEGER,

        subject_id INTEGER,

        teacher_id INTEGER,

        day_name TEXT,

        start_time TEXT,

        end_time TEXT,

        FOREIGN KEY(class_id)
        REFERENCES classes(id),

        FOREIGN KEY(subject_id)
        REFERENCES subjects(id),

        FOREIGN KEY(teacher_id)
        REFERENCES teachers(id)
    )
    """
)

# Academic attendance table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS academic_attendance (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_id INTEGER,

        subject_id INTEGER,

        period_id INTEGER,

        attendance_date DATE,

        status TEXT,

        FOREIGN KEY(student_id)
        REFERENCES students(id),

        FOREIGN KEY(subject_id)
        REFERENCES subjects(id),

        FOREIGN KEY(period_id)
        REFERENCES periods(id)
    )
    """
)

# Notification logs
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notification_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_id INTEGER,

        subject_id INTEGER,

        notification_type TEXT,

        message TEXT,

        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(student_id)
        REFERENCES students(id),

        FOREIGN KEY(subject_id)
        REFERENCES subjects(id)
    )
    """
)

# -----------------------------
# CORPORATE TABLES
# -----------------------------

# Employees table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS employees (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        employee_code TEXT,

        department_id INTEGER,

        FOREIGN KEY(user_id)
        REFERENCES users(id),

        FOREIGN KEY(department_id)
        REFERENCES departments(id)
    )
    """
)

# Shifts table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS shifts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        shift_name TEXT,

        start_time TEXT,

        end_time TEXT
    )
    """
)

# Corporate attendance table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS corporate_attendance (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        employee_id INTEGER,

        check_in DATETIME,

        check_out DATETIME,

        attendance_date DATE,

        FOREIGN KEY(employee_id)
        REFERENCES employees(id)
    )
    """
)

# Save changes
conn.commit()

conn.close()

print(
    "\nDatabase initialized successfully.\n"
)
