# models/user.py
import bcrypt, random
from cryptography.fernet import Fernet
from datetime import datetime

# Load the saved key
with open("secret.key", "rb") as key_file:
    fernet_key = key_file.read()

fernet = Fernet(fernet_key) # same as fernet = Fernet(b'Kwt0p0c1eA42Houf6jG8L1a05JltQHNF_jmCGnSvU8s=')
# it can: Encrypt text, Decrypt it later


class User:
    def __init__(
        self, username: str, password_plain: str, role: str, *,
        first_name = None, last_name = None):

        # --- Basic checks ---------------------------------------------------
        if not username or not password_plain or not role:
            raise ValueError("username, password and role are mandatory")

        role = role
        if role not in {"super", "system_admin", "service_engineer"}:
            raise ValueError(f"Unknown role: {role}")

        if role in {"system_admin", "service_engineer"}:
            if first_name is None or last_name is None:
                raise ValueError(f"first_name and last_name are required for this role: {role}")
        
        # make random id
        self.user_id = random.randint(1_000_000, 9_999_999)  
        # Core fields 
        self.username: bytes = self._encrypt(username)
        self.password_hash: bytes = self._hash_password(password_plain)
        self.role: str = role
        # self.role: str = self._encrypt(role)

        # Optional profile
        self.first_name = self._encrypt(first_name) if first_name else None
        self.last_name = self._encrypt(last_name) if last_name else None

        # Registration date
        if role == "super":
            self.registration_date = None
        else:
            self.registration_date = datetime.now().isoformat()

    @staticmethod
    def _hash_password(password: str) -> bytes:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    @staticmethod
    def _encrypt(value: str) -> bytes:
        return fernet.encrypt(value.encode())

    @staticmethod
    def _decrypt(encrypted_value: bytes) -> str:
        return fernet.decrypt(encrypted_value).decode()

    def verify_password(self, password_input: str) -> bool:
        return bcrypt.checkpw(password_input.encode(), self.password_hash)

    @property
    def username_plain(self) -> str:
        return self._decrypt(self.username)

    # @property
    # def role_plain(self) -> str:
    #     return self._decrypt(self.role)

    @property
    def full_name(self) -> str:
        first = self._decrypt(self.first_name) if self.first_name else ""
        last = self._decrypt(self.last_name) if self.last_name else ""
        return f"{first} {last}".strip()

    def __repr__(self) -> str:
        uname = self.username_plain if self.username else "<unset>"
        date = self.registration_date or "<N/A>"
        return f"User(username={uname}, role={self.role}, registration_date={date})"
