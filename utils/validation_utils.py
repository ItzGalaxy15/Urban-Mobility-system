from models.user import PWD_ALLOWED_RE
import re

def validate_password(password: str):
    """
    Validates a password according to the rules:
    - 12-30 characters
    - Allowed special characters
    - Must include lowercase, uppercase, digit, and special char
    Returns (True, None) if valid, else (False, error_message)
    """
    if not password:
        return False, "Password is required."
    if not PWD_ALLOWED_RE.fullmatch(password):
        return False, "Password contains invalid characters or length (12-30)."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one digit."
    if not re.search(r"[~!@#$%&\-_+=`|\\(){}\[\]:;'<>,.?/]", password):
        return False, "Password must include at least one special character."
    return True, None 