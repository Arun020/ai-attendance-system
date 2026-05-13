import hashlib


# Hash password
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# Verify password
def verify_password(
    plain_password,
    hashed_password
):

    return (
        hash_password(plain_password)
        == hashed_password
    )