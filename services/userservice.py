import sqlite3
from utils.crypto_utils import hash_password, decrypt, check_password
from models.user import User, USERNAME_RE, PWD_ALLOWED_RE
import re


class UserService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and requirements."""
        if not username:
            return False, "Username is required"
        if not USERNAME_RE.fullmatch(username):
            return False, "Username must be 8-10 characters and start with a letter or underscore"
        return True, ""

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password requirements."""
        if not password:
            return False, "Password is required"
        if not PWD_ALLOWED_RE.fullmatch(password):
            return False, "Password must be 12-30 characters and contain only allowed special characters"
        if not (re.search(r"[a-z]", password)
                and re.search(r"[A-Z]", password)
                and re.search(r"\d", password)
                and re.search(r"[~!@#$%&\-_+=`|\\(){}\[\]:;'<>,.?/]", password)):
            return False, "Password must include lowercase, uppercase, digit and special character"
        return True, ""

    def validate_name(self, name: str, field_name: str) -> tuple[bool, str]:
        """Validate first/last name requirements."""
        if not name:
            return False, f"{field_name} is required"
        if not name.strip():
            return False, f"{field_name} cannot be empty"
        return True, ""

    def add_user(self, username=None, password=None, first_name=None, last_name=None, role=None, user=None):
        """
        Add a user to the database. Can be called with either individual parameters or a User object.
        
        Args:
            Either:
            - username, password, first_name, last_name, role: Individual parameters
            Or:
            - user: User object with encrypted data
        """
        try:
            if user is None:
                # Validate all fields first
                valid, message = self.validate_username(username)
                if not valid:
                    return False, message

                valid, message = self.validate_password(password)
                if not valid:
                    return False, message

                valid, message = self.validate_name(first_name, "First name")
                if not valid:
                    return False, message

                valid, message = self.validate_name(last_name, "Last name")
                if not valid:
                    return False, message

                # Create User object
                user = User(
                    username=username,
                    password_plain=password,
                    role=role,
                    first_name=first_name,
                    last_name=last_name
                )

            # Add to database
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO User (username, password_hash, first_name, last_name, registration_date, role)
                VALUES (?, ?, ?, ?, datetime('now'), ?)
            ''', (
                user.username,
                user.password_hash,
                user.first_name,
                user.last_name,
                user.role
            ))
            conn.commit()
            conn.close()
            return True, "User added successfully"
        except ValueError as e:
            return False, str(e)

    def get_user_by_id(self, user_id):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role FROM User WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "user_id": row[0],
                "username": decrypt(row[1]),
                "first_name": decrypt(row[2]),
                "last_name": decrypt(row[3]),
                "role": decrypt(row[4])
            }
        return None
        
    def verify_user_password(self, user_id, password):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM User WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return check_password(password, row[0])
        return False

    def get_user_by_username(self, username):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role FROM User')
        users = c.fetchall()
        conn.close()
        for row in users:
            if decrypt(row[1]) == username:
                return {
                    "user_id": row[0],
                    "username": decrypt(row[1]),
                    "first_name": decrypt(row[2]),
                    "last_name": decrypt(row[3]),
                    "role": decrypt(row[4])
                }
        return None

    def update_password(self, user_id, new_password):
        conn = self._get_connection()
        c = conn.cursor()
        hashed = hash_password(new_password)
        c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
        conn.commit()
        conn.close()

# Create a single instance of UserService
user_service = UserService("urban_mobility.db")
