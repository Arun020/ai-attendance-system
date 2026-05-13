print("🔥 ATTENDANCE API LOADED FROM:", __file__)

from fastapi import APIRouter, Depends, HTTPException
import sqlite3
import os
from fastapi.responses import HTMLResponse, StreamingResponse
import io
from openpyxl import Workbook

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
# COLLEGE ATTENDANCE INSERT
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
# CORPORATE ATTENDANCE INSERT
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
# 🎓 COLLEGE UI DASHBOARD (KPI + CHARTS + LINE)
# =========================================================
@router.get("/college-ui", response_class=HTMLResponse)
def college_ui():

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT student_name, subject_name, teacher_name, session_id, attendance_date, status
            FROM college_attendance
        """)
        rows = cur.fetchall()

    teachers = sorted(list(set([r[2] for r in rows])))

    html = """
    <html>
    <head>
        <title>College Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>
            body {font-family: Arial; background:#f4f6f8;}
            .container {max-width:1100px;margin:auto;padding:20px;}
            .card {background:white;padding:15px;margin:10px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
            .kpi {display:flex;justify-content:center;gap:10px;flex-wrap:wrap;}
            table {width:100%;border-collapse:collapse;}
            th,td{border:1px solid #ddd;padding:8px;text-align:center;}
            th{background:#2c3e50;color:white;}
            canvas{max-height:250px;}
            select, button {padding:6px;margin:5px;}
        </style>

        <script>

        function filterTable() {
            let teacher = document.getElementById("teacherFilter").value;
            let status = document.getElementById("statusFilter").value;

            document.querySelectorAll("table tr:not(:first-child)").forEach(r => {

                let t = r.cells[2].innerText;
                let s = r.cells[5].innerText;

                let show = true;

                if (teacher && t !== teacher) show = false;
                if (status && s !== status) show = false;

                r.style.display = show ? "" : "none";
            });
        }

        window.onload = function () {

            setTimeout(() => {

                let total = 0;
                let present = 0;
                let absent = 0;
                let teacherCount = {};

                document.querySelectorAll("table tr").forEach((r, i) => {

                    if (i === 0) return;
                    if (!r.cells || r.cells.length < 6) return;

                    let teacher = r.cells[2].innerText.trim();
                    let status = r.cells[5].innerText.trim();

                    total++;

                    if (status === "Present") present++;
                    else absent++;

                    teacherCount[teacher] = (teacherCount[teacher] || 0) + 1;
                });

                // KPI UPDATE
                document.getElementById("total").innerText = total;
                document.getElementById("present").innerText = present;
                document.getElementById("absent").innerText = absent;

                let percent = total ? ((present / total) * 100).toFixed(1) : 0;
                document.getElementById("percent").innerText = percent + "%";

                // PIE
                new Chart(document.getElementById("pie"), {
                    type: "pie",
                    data: {
                        labels: ["Present", "Absent"],
                        datasets: [{ data: [present, absent] }]
                    }
                });

                // BAR
                new Chart(document.getElementById("bar"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(teacherCount),
                        datasets: [{ data: Object.values(teacherCount) }]
                    }
                });

                // LINE
                fetch("/college-monthly-analytics")
                    .then(res => res.json())
                    .then(data => {

                        new Chart(document.getElementById("line"), {
                            type: "line",
                            data: {
                                labels: data.months,
                                datasets: [{
                                    label: "Monthly Attendance Trend",
                                    data: data.present,
                                    borderColor: "blue",
                                    fill: false,
                                    tension: 0.3
                                }]
                            }
                        });

                    });

            }, 300);

        };

        </script>
    </head>

    <body>

    <div class="container">

        <h2 style="text-align:center;">🎓 College Dashboard</h2>

        <!-- KPI -->
        <div class="kpi">
            <div class="card"><h3 id="total">0</h3><p>Total</p></div>
            <div class="card"><h3 id="present">0</h3><p>Present</p></div>
            <div class="card"><h3 id="absent">0</h3><p>Absent</p></div>
            <div class="card"><h3 id="percent">0%</h3><p>Attendance %</p></div>
        </div>

        <!-- FILTERS -->
        <div style="text-align:center;margin-bottom:10px;">

            <select id="teacherFilter" onchange="filterTable()">
                <option value="">All Teachers</option>
    """

    for t in teachers:
        html += f'<option value="{t}">{t}</option>'

    html += """
            </select>

            <select id="statusFilter" onchange="filterTable()">
                <option value="">All Status</option>
                <option value="Present">Present</option>
                <option value="Absent">Absent</option>
            </select>

            <a href="/college-export-excel">
                <button style="background:green;color:white;border:none;">
                    Export Excel
                </button>
            </a>

        </div>

        <div class="card">
            <canvas id="pie"></canvas>
        </div>

        <div class="card">
            <canvas id="bar"></canvas>
        </div>

        <div class="card">
            <canvas id="line"></canvas>
        </div>

        <table>
            <tr>
                <th>Name</th>
                <th>Subject</th>
                <th>Teacher</th>
                <th>Session</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
        </tr>
        """

    html += """
        </table>

    </div>

    </body>
    </html>
    """

    return HTMLResponse(html)

# =========================================================
# 🏢 CORPORATE UI DASHBOARD
# =========================================================
@router.get("/corporate-ui", response_class=HTMLResponse)
def corporate_ui():

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_name, session_id, check_in_time, attendance_date, status
            FROM corporate_attendance
        """)
        rows = cur.fetchall()

    html = """
    <html>
    <head>
        <title>Corporate Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>
            body {font-family: Arial; background:#f4f6f8;}
            .container {max-width:1100px;margin:auto;padding:20px;}
            .card {background:white;padding:15px;margin:10px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
            .kpi {display:flex;justify-content:center;gap:10px;flex-wrap:wrap;}
            table {width:100%;border-collapse:collapse;}
            th,td{border:1px solid #ddd;padding:8px;text-align:center;}
            th{background:#34495e;color:white;}
            canvas{max-height:250px;}
            select, button {padding:6px;margin:5px;}
        </style>

        <script>

        window.onload = function () {

            setTimeout(() => {

                let total = 0;
                let present = 0;
                let absent = 0;
                let empCount = {};

                document.querySelectorAll("table tr").forEach((r, i) => {

                    if (i === 0) return;
                    if (!r.cells || r.cells.length < 5) return;

                    let emp = r.cells[0].innerText.trim();
                    let status = r.cells[4].innerText.trim();

                    total++;

                    if (status === "Present") present++;
                    else absent++;

                    empCount[emp] = (empCount[emp] || 0) + 1;
                });

                document.getElementById("total").innerText = total;
                document.getElementById("present").innerText = present;
                document.getElementById("absent").innerText = absent;

                let percent = total ? ((present / total) * 100).toFixed(1) : 0;
                document.getElementById("percent").innerText = percent + "%";

                new Chart(document.getElementById("pie"), {
                    type: "pie",
                    data: {
                        labels: ["Present", "Absent"],
                        datasets: [{ data: [present, absent] }]
                    }
                });

                new Chart(document.getElementById("bar"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(empCount),
                        datasets: [{ data: Object.values(empCount) }]
                    }
                });

                fetch("/corporate-monthly-analytics")
                    .then(res => res.json())
                    .then(data => {

                        new Chart(document.getElementById("line"), {
                            type: "line",
                            data: {
                                labels: data.months,
                                datasets: [{
                                    label: "Monthly Attendance Trend",
                                    data: data.present,
                                    borderColor: "green",
                                    fill: false,
                                    tension: 0.3
                                }]
                            }
                        });

                    });

            }, 300);

        };

        </script>
    </head>

    <body>

    <div class="container">

        <h2 style="text-align:center;">🏢 Corporate Dashboard</h2>

        <!-- KPI -->
        <div class="kpi">
            <div class="card"><h3 id="total">0</h3><p>Total</p></div>
            <div class="card"><h3 id="present">0</h3><p>Present</p></div>
            <div class="card"><h3 id="absent">0</h3><p>Absent</p></div>
            <div class="card"><h3 id="percent">0%</h3><p>Attendance %</p></div>
        </div>

        <!-- FILTER SECTION (RESTORED) -->
        <div style="text-align:center;margin-bottom:10px;">

            <select>
                <option>All Employees</option>
            </select>

            <select>
                <option>All Status</option>
                <option>Present</option>
                <option>Absent</option>
            </select>

            <!-- EXPORT BUTTON RESTORED -->
            <a href="/corporate-export-excel">
                <button style="background:green;color:white;border:none;">
                    Export Excel
                </button>
            </a>

        </div>

        <div class="card">
            <canvas id="pie"></canvas>
        </div>

        <div class="card">
            <canvas id="bar"></canvas>
        </div>

        <div class="card">
            <canvas id="line"></canvas>
        </div>

        <table>
            <tr>
                <th>Employee</th>
                <th>Session</th>
                <th>Check-in</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
        </tr>
        """

    html += """
        </table>

    </div>

    </body>
    </html>
    """

    return HTMLResponse(html)


# =========================================================
# 📊 MONTHLY ANALYTICS APIs
# =========================================================
@router.get("/college-monthly-analytics")
def college_monthly():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT strftime('%Y-%m', attendance_date),
                   COUNT(*),
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END)
            FROM college_attendance
            GROUP BY strftime('%Y-%m', attendance_date)
        """)
        rows = cur.fetchall()

    return {
        "months":[r[0] for r in rows],
        "total":[r[1] for r in rows],
        "present":[r[2] for r in rows],
        "absent":[r[3] for r in rows]
    }


@router.get("/corporate-monthly-analytics")
def corporate_monthly():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT strftime('%Y-%m', attendance_date),
                   COUNT(*),
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END)
            FROM corporate_attendance
            GROUP BY strftime('%Y-%m', attendance_date)
        """)
        rows = cur.fetchall()

    return {
        "months":[r[0] for r in rows],
        "total":[r[1] for r in rows],
        "present":[r[2] for r in rows],
        "absent":[r[3] for r in rows]
    }


# =========================================================
# 📥 EXCEL EXPORT
# =========================================================
@router.get("/college-export-excel")
def college_export_excel():
    wb = Workbook()
    ws = wb.active

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT student_name, subject_name, teacher_name, session_id, attendance_date, status FROM college_attendance")
        rows = cur.fetchall()

    ws.append(["Student","Subject","Teacher","Session","Date","Status"])
    for r in rows:
        ws.append(r)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/corporate-export-excel")
def corporate_export_excel():
    wb = Workbook()
    ws = wb.active

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT employee_name, session_id, check_in_time, attendance_date, status FROM corporate_attendance")
        rows = cur.fetchall()

    ws.append(["Employee","Session","Check-in","Date","Status"])
    for r in rows:
        ws.append(r)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# =========================================================
# ⚠ DEFAULTER DASHBOARD (ADDED ONLY - NO CHANGES ELSEWHERE)
# =========================================================

@router.get("/college-defaulters", response_class=HTMLResponse)
def college_defaulters():

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT student_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
            FROM college_attendance
            GROUP BY student_name
        """)
        rows = cur.fetchall()

    html = """
    <html>
    <head>
        <title>College Defaulters</title>
        <style>
            body {font-family: Arial; background:#f4f6f8;}
            .container {max-width:900px;margin:auto;padding:20px;}
            table {width:100%;border-collapse:collapse;background:white;}
            th,td {border:1px solid #ddd;padding:10px;text-align:center;}
            th {background:#c0392b;color:white;}
        </style>
    </head>
    <body>
    <div class="container">

    <h2 style="text-align:center;">⚠ College Defaulters</h2>

    <table>
        <tr>
            <th>Student</th>
            <th>Total</th>
            <th>Present</th>
            <th>Attendance %</th>
        </tr>
    """

    for r in rows:
        total = r[1]
        present = r[2]
        percent = round((present / total) * 100, 2) if total else 0

        if percent < 75:
            html += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{total}</td>
                <td>{present}</td>
                <td>{percent}%</td>
            </tr>
            """

    html += """
    </table>

    </div>
    </body>
    </html>
    """

    return HTMLResponse(html)


@router.get("/corporate-defaulters", response_class=HTMLResponse)
def corporate_defaulters():

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present
            FROM corporate_attendance
            GROUP BY employee_name
        """)
        rows = cur.fetchall()

    html = """
    <html>
    <head>
        <title>Corporate Defaulters</title>
        <style>
            body {font-family: Arial; background:#f4f6f8;}
            .container {max-width:900px;margin:auto;padding:20px;}
            table {width:100%;border-collapse:collapse;background:white;}
            th,td {border:1px solid #ddd;padding:10px;text-align:center;}
            th {background:#8e44ad;color:white;}
        </style>
    </head>
    <body>
    <div class="container">

    <h2 style="text-align:center;">⚠ Corporate Defaulters</h2>

    <table>
        <tr>
            <th>Employee</th>
            <th>Total</th>
            <th>Present</th>
            <th>Attendance %</th>
        </tr>
    """

    for r in rows:
        total = r[1]
        present = r[2]
        percent = round((present / total) * 100, 2) if total else 0

        if percent < 75:
            html += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{total}</td>
                <td>{present}</td>
                <td>{percent}%</td>
            </tr>
            """

    html += """
    </table>

    </div>
    </body>
    </html>
    """

    return HTMLResponse(html)
