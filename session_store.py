import os
import json

# -----------------------------
# SESSION FILE (PERSISTENCE)
# -----------------------------
SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")

TOKEN = None
ROLE = None


# =========================================================
# SET SESSION AFTER LOGIN
# =========================================================
def set_session(token: str, role: str):
    global TOKEN, ROLE
    TOKEN = token
    ROLE = role

    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({
                "token": token,
                "role": role
            }, f)
    except Exception as e:
        print("Session save error:", e)


# =========================================================
# GET TOKEN (AUTO RESTORE IF NEEDED)
# =========================================================
def get_token():
    global TOKEN

    if TOKEN:
        return TOKEN

    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                TOKEN = data.get("token")
                return TOKEN
        except Exception:
            return None

    return None


# =========================================================
# GET ROLE (AUTO RESTORE IF NEEDED)
# =========================================================
def get_role():
    global ROLE

    if ROLE:
        return ROLE

    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                ROLE = data.get("role")
                return ROLE
        except Exception:
            return None

    return None


# =========================================================
# CHECK LOGIN STATUS
# =========================================================
def is_logged_in():
    return get_token() is not None


# =========================================================
# CLEAR SESSION
# =========================================================
def clear_session():
    global TOKEN, ROLE
    TOKEN = None
    ROLE = None

    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception as e:
            print("Session clear error:", e)