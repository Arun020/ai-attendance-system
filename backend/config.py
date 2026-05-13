import os

# -----------------------------
# BASE PROJECT PATH
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------
# DATABASE PATH
# -----------------------------
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

# -----------------------------
# ENVIRONMENT SETUP
# -----------------------------
ENV = "production"   # ✅ changed from development to production

# -----------------------------
# API CONFIG (CLOUD READY FIX)
# -----------------------------
API_HOST = "https://ai-attendance-system-edyg.onrender.com"
API_PORT = 8000

# OPTIONAL: full base URL (recommended for your project)
API_BASE_URL = f"{API_HOST}"

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = "ai_attendance_secret_key"