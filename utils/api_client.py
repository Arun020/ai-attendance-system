import requests
from session_store import get_token

API_BASE_URL = "https://ai-attendance-system-edyg.onrender.com"


def post(endpoint, payload, token=None):
    if token is None:
        token = get_token()

    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=payload,
        headers=headers,
        timeout=10,
        verify=False
    )