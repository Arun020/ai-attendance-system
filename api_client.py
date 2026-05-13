import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# GET TOKEN FROM ARGUMENTS (SUBPROCESS SAFE)
# =========================================================
def get_token():

    # token is passed as last argument in subprocess
    if len(sys.argv) >= 5:
        return sys.argv[4]

    return None


# =========================================================
# POST REQUEST
# =========================================================
def post(url, data):

    token = get_token()

    if not token:
        raise Exception("No JWT token received in api_client")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        BASE_URL + url,
        json=data,
        headers=headers
    )

    return response


# =========================================================
# GET REQUEST
# =========================================================
def get(url):

    token = get_token()

    if not token:
        raise Exception("No JWT token received in api_client")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        BASE_URL + url,
        headers=headers
    )

    return response