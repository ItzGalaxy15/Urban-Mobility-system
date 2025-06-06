# models/user.py
import bcrypt
from cryptography.fernet import Fernet
from datetime import datetime

# Load the saved key
with open("secret.key", "rb") as key_file:
    fernet_key = key_file.read()

fernet = Fernet(fernet_key) # same as fernet = Fernet(b'Kwt0p0c1eA42Houf6jG8L1a05JltQHNF_jmCGnSvU8s=')
# Think of fernet as a secret machine that can:
# Encrypt text (hide it)
# Decrypt it later (reveal it)

class User:
    def __init__(self, username, password_plain, role, first_name, last_name):
        print("Before lower():", username)
        print("After lower():", username.lower())
        self.username = self.encrypt(username.lower())
        self.password_hash = self.hash_password(password_plain)
        self.role = role
        self.first_name = self.encrypt(first_name)
        self.last_name = self.encrypt(last_name)
        self.registration_date = datetime.now().isoformat()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(self, password_input):
        return bcrypt.checkpw(password_input.encode(), self.password_hash)

    def encrypt(self, value):
        return fernet.encrypt(value.encode())

    def decrypt(self, encrypted_value):
        return fernet.decrypt(encrypted_value).decode()

    def get_username(self):
        return self.decrypt(self.username)

    def get_full_name(self):
        return f"{self.decrypt(self.first_name)} {self.decrypt(self.last_name)}"
