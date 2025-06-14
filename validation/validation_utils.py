from models.user import PWD_ALLOWED_RE, USERNAME_RE
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

def validate_username(username: str):
    """
    Validates a username according to the rules:
    - 8-10 characters
    - Starts with letter or underscore
    - Contains only letters, numbers, underscores, periods, or apostrophes
    Returns (True, None) if valid, else (False, error_message)
    """
    if not username:
        return False, "Username is required."
    if not USERNAME_RE.fullmatch(username):
        return False, "Username must be 8-10 characters, start with a letter or underscore, and contain only letters, numbers, underscores, periods, or apostrophes."
    return True, None

def validate_name(name: str, field_name: str):
    """
    Validates a name field (first_name or last_name)
    Returns (True, None) if valid, else (False, error_message)
    """
    if not name:
        return False, f"{field_name} is required."
    return True, None

def validate_user_inputs(username: str, password: str, first_name: str, last_name: str, role: str):
    """
    Validates all user inputs according to the User model rules.
    Returns (True, None) if all valid, else (False, error_message)
    """
    # Validate username
    valid, message = validate_username(username)
    if not valid:
        return False, message

    # Validate password
    valid, message = validate_password(password)
    if not valid:
        return False, message

    # Validate names for non-super roles
    if role in {"system_admin", "service_engineer"}:
        valid, message = validate_name(first_name, "First name")
        if not valid:
            return False, message
        
        valid, message = validate_name(last_name, "Last name")
        if not valid:
            return False, message

    return True, None
