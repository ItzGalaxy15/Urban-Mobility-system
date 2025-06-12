# generate_key.py
from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Key generated and saved to secret.key")

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())