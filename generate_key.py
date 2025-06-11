# generate_key.py
from cryptography.fernet import Fernet
import os

key = Fernet.generate_key()

with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Key generated and saved to secret.key")

def load_key():
    # Use environment variables or a secure key management service
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        raise SecurityError("Encryption key not found")
    return key

fernet = Fernet(load_key())