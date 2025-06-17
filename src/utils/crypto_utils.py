from cryptography.fernet import Fernet
import bcrypt
import os

# Singleton pattern for Fernet instance
_fernet = None

def get_fernet():
    global _fernet
    if _fernet is None:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
        _fernet = Fernet(key)
    return _fernet

def encrypt(data: str) -> bytes:
    if data is None:
        return None
    return get_fernet().encrypt(data.encode())

def decrypt(token: bytes) -> str:
    if token is None:
        return None
    return get_fernet().decrypt(token).decode()

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
