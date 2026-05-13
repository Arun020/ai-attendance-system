import cv2
import face_recognition
import os
import time
import sys
import requests
from datetime import datetime

# -----------------------------
# PATH FIX
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.face_utils import load_trained_model, recognize_face

# -----------------------------
# CLOUD API BASE URL
# -----------------------------
API_BASE_URL = "https://ai-attendance-system-edyg.onrender.com"


# -----------------------------
# INPUT ARGS
# -----------------------------
mode = sys.argv[1] if len(sys.argv) > 1 else "college"
subject = sys.argv[2] if len(sys.argv) > 2 else ""
teacher = sys.argv[3] if len(sys.argv) > 3 else ""
token = sys.argv[4] if len(sys.argv) > 4 else ""

if not token:
    print("❌ ERROR: JWT token missing")
    sys.exit(1)

# -----------------------------
# CONFIG
# -----------------------------
MODEL_PATH = os.path.join(BASE_DIR, "models", "face_encodings.pkl")

session_id = f"{mode.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
session_date = str(datetime.now().date())

print("\nSESSION STARTED:", session_id)

# -----------------------------
# LOAD MODEL
# -----------------------------
print("Loading model...")
known_encodings, known_names = load_trained_model(MODEL_PATH)
print("Model loaded")

# -----------------------------
# CAMERA
# -----------------------------
video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

SESSION_MARKED = set()
last_seen = {}
COOLDOWN = 10


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    ret, frame = video_capture.read()
    if not ret:
        break

    small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        name = recognize_face(known_encodings, known_names, face_encoding)

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        if name == "Unknown":
            continue

        student_id = name
        key = f"{student_id}_{session_id}"
        now = time.time()

        if student_id in last_seen and now - last_seen[student_id] < COOLDOWN:
            continue

        if key not in SESSION_MARKED:

            try:
                if mode == "college":

                    payload = {
                        "student_id": student_id,
                        "student_name": name,
                        "subject_name": subject,
                        "teacher_name": teacher,
                        "session_id": session_id,
                        "attendance_date": session_date,
                        "status": "Present"
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/college-attendance",
                        json=payload,
                        timeout=10,
                        verify=False   # 🔥 FIX ADDED
                    )

                else:

                    payload = {
                        "employee_id": student_id,
                        "employee_name": name,
                        "session_id": session_id,
                        "attendance_date": session_date,
                        "status": "Present"
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/corporate-attendance",
                        json=payload,
                        timeout=10,
                        verify=False   # 🔥 FIX ADDED
                    )

                try:
                    print("Marked:", response.json())
                except:
                    print("Marked successfully")

                SESSION_MARKED.add(key)
                last_seen[student_id] = now

            except Exception as e:
                print("API Error:", str(e))

    cv2.imshow("AI Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video_capture.release()
cv2.destroyAllWindows()