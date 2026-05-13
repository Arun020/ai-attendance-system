from fastapi import APIRouter, Depends, HTTPException
import sqlite3
import os
from fastapi.responses import HTMLResponse

from backend.auth_jwt import get_current_user

router = APIRouter()

# =========================================================
# DATABASE
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =========================================================
# COLLEGE ATTENDANCE
# =========================================================
@router.post("/college-attendance")
def college_attendance(payload: dict, user=Depends(get_current_user)):

    if user.get("role") not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO college_attendance
            (student_id, student_name, subject_name, teacher_name, session_id, attendance_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload["student_id"],
            payload["student_name"],
            payload["subject_name"],
            payload["teacher_name"],
            payload["session_id"],
            payload["attendance_date"],
            payload["status"]
        ))
        conn.commit()

    return {"message": "success"}


# =========================================================
# CORPORATE ATTENDANCE
# =========================================================
@router.post("/corporate-attendance")
def corporate_attendance(payload: dict, user=Depends(get_current_user)):

    if user.get("role") not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO corporate_attendance
            (employee_id, employee_name, session_id, check_in_time, attendance_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload["employee_id"],
            payload["employee_name"],
            payload["session_id"],
            payload.get("check_in_time", ""),
            payload["attendance_date"],
            payload["status"]
        ))
        conn.commit()

    return {"message": "success"}


# =========================================================
# 🎓 COLLEGE DEFAULTER DASHBOARD (EMAILJS)
# =========================================================
@router.get("/college-defaulters", response_class=HTMLResponse)
def college_defaulters():

    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                student_name,
                COUNT(*) as total,
                SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present,
                (SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as percentage,
                email
            FROM college_attendance
            WHERE strftime('%Y-%m', attendance_date)=strftime('%Y-%m','now')
            GROUP BY student_name
            HAVING percentage < 75
        """)

        rows = cur.fetchall()

    html = """
    <html>
    <head>
        <title>College Defaulters</title>
        <style>
            body {font-family:Arial;background:#f4f4f4;}
            table {border-collapse:collapse;width:80%;margin:auto;background:white;}
            th,td{border:1px solid #ddd;padding:10px;text-align:center;}
            th{background:#2c3e50;color:white;}
            h2{text-align:center;}
            .btn{background:red;color:white;padding:6px;border:none;cursor:pointer;}
        </style>

        <!-- EmailJS -->
        <script src="https://cdn.emailjs.com/dist/email.min.js"></script>
        <script>
            emailjs.init("24u84vEHfewOEqff8");

            function sendEmail(name, email){

                if(!email){
                    alert("Email missing for " + name);
                    return;
                }

                emailjs.send("service_yn9h6bq", "template_z3crfj1", {
                    to_name: name,
                    to_email: email,
                    message: "You are marked as a DEFAULTER. Improve attendance immediately."
                })
                .then(function(response){
                    alert("Email Sent Successfully");
                    console.log(response);
                })
                .catch(function(error){
                    alert("Email Failed");
                    console.log(error);
                });
            }
        </script>

    </head>

    <body>
    <h2>🎓 College Defaulter Dashboard</h2>

    <table>
        <tr>
            <th>Name</th>
            <th>Total</th>
            <th>Present</th>
            <th>%</th>
            <th>Action</th>
        </tr>
    """

    for r in rows:
        name = r[0]
        email = r[4] if len(r) > 4 and r[4] else f"{name}@gmail.com"

        html += f"""
        <tr>
            <td>{name}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]:.2f}</td>
            <td>
                <button class='btn'
                onclick="sendEmail('{name}','{email}')">
                    Send Email
                </button>
            </td>
        </tr>
        """

    html += "</table></body></html>"
    return html


# =========================================================
# 🏢 CORPORATE DEFAULTER DASHBOARD (EMAILJS)
# =========================================================
@router.get("/corporate-defaulters", response_class=HTMLResponse)
def corporate_defaulters():

    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                employee_name,
                COUNT(*) as total,
                SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present,
                (SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as percentage,
                email
            FROM corporate_attendance
            WHERE strftime('%Y-%m', attendance_date)=strftime('%Y-%m','now')
            GROUP BY employee_name
            HAVING percentage < 75
        """)

        rows = cur.fetchall()

    html = """
    <html>
    <head>
        <title>Corporate Defaulters</title>
        <style>
            body {font-family:Arial;background:#f4f4f4;}
            table {border-collapse:collapse;width:80%;margin:auto;background:white;}
            th,td{border:1px solid #ddd;padding:10px;text-align:center;}
            th{background:#34495e;color:white;}
            h2{text-align:center;}
            .btn{background:#c0392b;color:white;padding:6px;border:none;cursor:pointer;}
        </style>

        <script src="https://cdn.emailjs.com/dist/email.min.js"></script>
        <script>
            emailjs.init("24u84vEHfewOEqff8");

            function sendEmail(name, email){

                if(!email){
                    alert("Email missing for " + name);
                    return;
                }

                emailjs.send("service_yn9h6bq", "YOUR_TEMPLATE_ID", {
                    to_name: name,
                    to_email: email,
                    message: "You are marked as a DEFAULTER. Improve attendance immediately."
                })
                .then(function(response){
                    alert("Email Sent Successfully");
                    console.log(response);
                })
                .catch(function(error){
                    alert("Email Failed");
                    console.log(error);
                });
            }
        </script>

    </head>

    <body>
    <h2>🏢 Corporate Defaulter Dashboard</h2>

    <table>
        <tr>
            <th>Name</th>
            <th>Total</th>
            <th>Present</th>
            <th>%</th>
            <th>Action</th>
        </tr>
    """

    for r in rows:
        name = r[0]
        email = r[4] if len(r) > 4 and r[4] else f"{name}@company.com"

        html += f"""
        <tr>
            <td>{name}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]:.2f}</td>
            <td>
                <button class='btn'
                onclick="sendEmail('{name}','{email}')">
                    Send Email
                </button>
            </td>
        </tr>
        """

    html += "</table></body></html>"
    return html