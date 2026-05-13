import os
import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# CLOUD CONFIG
# -----------------------------
API_BASE_URL = "https://ai-attendance-system-edyg.onrender.com"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# -----------------------------
# MARK ATTENDANCE
# -----------------------------
def mark_attendance(name, attendance_dir, marked_attendance):

    # Avoid duplicate attendance
    if name in marked_attendance:
        return

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Create folder
    os.makedirs(attendance_dir, exist_ok=True)

    # Excel file
    attendance_file = os.path.join(attendance_dir, f"{date}.xlsx")

    # New row
    new_data = pd.DataFrame([
        {
            "Name": name,
            "Date": date,
            "Time": time
        }
    ])

    # Append if exists
    if os.path.exists(attendance_file):
        existing_df = pd.read_excel(attendance_file)
        df = pd.concat([existing_df, new_data], ignore_index=True)
    else:
        df = new_data

    # Save Excel
    df.to_excel(attendance_file, index=False)

    # -----------------------------
    # SEND TO BACKEND (FIXED)
    # -----------------------------
    try:
        # Using correct endpoint (based on your system design)
        response = requests.post(
            f"{API_BASE_URL}/college-attendance",
            json={
                "student_name": name,
                "attendance_date": date,
                "status": "Present"
            },
            timeout=10,
            verify=False   # 🔥 FIX for SSL issues
        )

        try:
            print("API Response:", response.json())
        except:
            print("API Response received")

    except Exception as e:
        print("API Error:", e)

    # Mark locally
    marked_attendance.append(name)

    print(f"Attendance marked for {name}")