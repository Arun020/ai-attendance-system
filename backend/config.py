import os

# -----------------------------
# BASE PROJECT PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------
# DATABASE PATH (CENTRALIZED)
# -----------------------------
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

# -----------------------------
# ENVIRONMENT SETUP
# -----------------------------
ENV = "development"   # change to "production" when deploying

# -----------------------------
# API CONFIG (FOR FUTURE CLOUD DEPLOYMENT)
# -----------------------------
API_HOST = "127.0.0.1"
API_PORT = 8000

# -----------------------------
# SECURITY (PLACEHOLDER FOR NEXT STEP)
# -----------------------------
SECRET_KEY = "ai_attendance_secret_key"