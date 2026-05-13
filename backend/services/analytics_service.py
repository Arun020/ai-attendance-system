import sqlite3

DB_PATH = "database/attendance.db"


# -----------------------------
# GET ATTENDANCE SUMMARY (REAL LOGIC)
# -----------------------------
def get_attendance_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # attendance stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM attendance
    """)

    total, present = cursor.fetchone()

    if total == 0:
        return {
            "total_students": total_students,
            "present_percentage": 0,
            "absent_percentage": 0
        }

    present_pct = round((present / total) * 100, 2)
    absent_pct = round(100 - present_pct, 2)

    conn.close()

    return {
        "total_students": total_students,
        "present_percentage": present_pct,
        "absent_percentage": absent_pct
    }


# -----------------------------
# DEFUALTERS (REAL LOGIC)
# threshold < 75%
# -----------------------------
def get_defaulters(threshold=75):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            student_id,
            COUNT(*) as total,
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        GROUP BY student_id
    """)

    rows = cursor.fetchall()
    conn.close()

    defaulters = []

    for r in rows:
        student_id, total, present = r

        if total == 0:
            continue

        percentage = (present / total) * 100

        if percentage < threshold:
            defaulters.append({
                "student_id": student_id,
                "attendance_percentage": round(percentage, 2)
            })

    return defaulters
