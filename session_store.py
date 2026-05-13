# session_store.py

TOKEN = None
ROLE = None


# =========================================================
# SET SESSION AFTER LOGIN
# =========================================================
def set_session(token: str, role: str):
    global TOKEN, ROLE
    TOKEN = token
    ROLE = role


# =========================================================
# GET TOKEN (USED BY API CLIENT)
# =========================================================
def get_token():
    return TOKEN


# =========================================================
# GET ROLE
# =========================================================
def get_role():
    return ROLE


# =========================================================
# CHECK LOGIN STATUS
# =========================================================
def is_logged_in():
    return TOKEN is not None


# =========================================================
# CLEAR SESSION (IMPORTANT ADDITION)
# =========================================================
def clear_session():
    global TOKEN, ROLE
    TOKEN = None
    ROLE = None