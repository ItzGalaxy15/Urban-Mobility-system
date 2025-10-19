# models/user.py
import re, random
from datetime import datetime
from typing import Optional
from utils.crypto_utils import encrypt, decrypt, hash_password, check_password
from utils.validation import USERNAME_PATTERN, PASSWORD_PATTERN

# These are now imported from utils/validation.py
# # Username & password validation patterns
# USERNAME_RE    | USERNAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_'.]{7,9}$", re.IGNORECASE)
# # Allowed special chars for password as per spec
# PWD_ALLOWED_RE | PASSWORD_PATTERN = re.compile(r"^[A-Za-z0-9~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]{12,30}$")

class User:
    def __init__(
        self,
        username: str,
        role: str,
        *,
        password_plain: Optional[str] = None,
        password_hash: Optional[bytes] = None,
        user_id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> None:
        
        # Basic presence checks
        if not username or not role:
            raise ValueError("username and role are mandatory")
        
        # Either password_plain or password_hash must be provided
        if password_plain is None and password_hash is None:
            raise ValueError("Either password_plain or password_hash must be provided")

        # Validate role without modification
        if role not in {"super", "system_admin", "service_engineer"}:
            raise ValueError(f"Unknown role: {role}")

        # Username & password rules (skip super admin hard‑coded user)
        if role != "super":
            # Username rules
            if not USERNAME_PATTERN.fullmatch(username):
                raise ValueError("username does not meet format/length rules")
            # Password rules (only validate if password_plain is provided)
            if password_plain is not None:
                if not PASSWORD_PATTERN.fullmatch(password_plain):
                    raise ValueError("password contains invalid characters or length")
                # complexity check
                if not (re.search(r"[a-z]", password_plain)
                        and re.search(r"[A-Z]", password_plain)
                        and re.search(r"\d",   password_plain)
                        and re.search(r"[~!@#$%&\-_+=`|\\(){}\[\]:;'<>,.?/]", password_plain)):
                    raise ValueError("password must include lowercase, uppercase, digit and special char")

        # extra profile requirement
        if role in {"system_admin", "service_engineer"}:
            if first_name is None or last_name is None:
                raise ValueError("first_name and last_name are required for this role")

        # Core fields
        self.username: bytes = encrypt(username)  # case‑insensitive store
        
        # Handle password - either use provided hash or create hash from plain text
        if password_hash is not None:
            self.password_hash: bytes = password_hash
        else:
            self.password_hash: bytes = hash_password(password_plain)
            
        self.role: str = encrypt(role)  # Store role encrypted

        # Optional profile (encrypted)
        self.user_id = user_id
        self.first_name = encrypt(first_name) if first_name else None
        self.last_name  = encrypt(last_name)  if last_name  else None

        # Registration date
        if role == "super":
            self.registration_date = None
        else:
            self.registration_date = datetime.now().isoformat()

    def verify_password(self, password_input: str) -> bool:
        return check_password(password_input, self.password_hash)

    @property
    def username_plain(self) -> str:
        return decrypt(self.username)

    @property
    def role_plain(self) -> str:
        return decrypt(self.role)

    @property
    def first_name_plain(self) -> str:
        return decrypt(self.first_name) if self.first_name else ""

    @property
    def last_name_plain(self) -> str:
        return decrypt(self.last_name) if self.last_name else ""

    @property
    def full_name(self) -> str:
        first = decrypt(self.first_name) if self.first_name else ""
        last  = decrypt(self.last_name)  if self.last_name  else ""
        return f"{first} {last}"

    def __repr__(self) -> str:
        uname = self.username_plain if self.username else "<unset>"
        date  = self.registration_date or "<N/A>"
        return f"User(username={uname}, role={self.role_plain}, registration_date={date})"
