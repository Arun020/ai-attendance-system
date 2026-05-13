from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
SECRET_KEY = "ai_attendance_secret_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Swagger Authorize support
security = HTTPBearer()


# =========================================================
# CREATE JWT TOKEN
# =========================================================
def create_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =========================================================
# VERIFY TOKEN (CORE FUNCTION)
# =========================================================
def verify_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# =========================================================
# FASTAPI DEPENDENCY (USE IN ALL ROUTES)
# =========================================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):

    token = credentials.credentials
    return verify_token(token)


# =========================================================
# ROLE BASED ACCESS CONTROL (RBAC)
# =========================================================
def require_role(user: dict, allowed_roles: list):

    role = user.get("role")

    if role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied for role: {role}"
        )