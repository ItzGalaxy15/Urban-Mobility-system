from cryptography.fernet import Fernet
import bcrypt

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())

def encrypt(data: str) -> bytes:
    return fernet.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    return fernet.decrypt(token).decode()

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
