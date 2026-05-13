import os
import pandas as pd
import requests

from datetime import datetime

# Base directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# Mark attendance
def mark_attendance(
    name,
    attendance_dir,
    marked_attendance
):

    # Avoid duplicate attendance
    if name in marked_attendance:

        return

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")

    time = now.strftime("%H:%M:%S")

    # Create attendance folder
    os.makedirs(
        attendance_dir,
        exist_ok=True
    )

    # Excel file path
    attendance_file = os.path.join(
        attendance_dir,
        f"{date}.xlsx"
    )

    # New attendance row
    new_data = pd.DataFrame(
        [
            {
                "Name": name,
                "Date": date,
                "Time": time
            }
        ]
    )

    # Append to Excel
    if os.path.exists(attendance_file):

        existing_df = pd.read_excel(
            attendance_file
        )

        df = pd.concat(
            [
                existing_df,
                new_data
            ],
            ignore_index=True
        )

    else:

        df = new_data

    # Save Excel
    df.to_excel(
        attendance_file,
        index=False
    )

    # Send attendance to backend API
    try:

        response = requests.post(
            "http://127.0.0.1:8000/attendance",
            json={
                "name": name,
                "date": date,
                "time": time
            }
        )

        print(
            "API Response:",
            response.json()
        )

    except Exception as e:

        print(
            "API Error:",
            e
        )

    # Mark locally
    marked_attendance.append(name)

    print(
        f"Attendance marked for {name}"
    )