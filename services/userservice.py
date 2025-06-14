import sqlite3
from utils.crypto_utils import hash_password, decrypt, check_password
from models.user import User


class UserService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and requirements."""
        if not username:
            return False, "Username is required"
        if not (8 <= len(username) <= 10):
            return False, "Username must be between 8 and 10 characters"
        if not (username[0].isalpha() or username[0] == '_'):
            return False, "Username must start with a letter or underscore"
        return True, ""

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password requirements."""
        if not password:
            return False, "Password is required"
        if not (12 <= len(password) <= 30):
            return False, "Password must be between 12 and 30 characters"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        return True, ""

    def validate_name(self, name: str, field_name: str) -> tuple[bool, str]:
        """Validate first/last name requirements."""
        if not name:
            return False, f"{field_name} is required"
        if not name.strip():
            return False, f"{field_name} cannot be empty"
        return True, ""

    def add_user_from_params(self, username, password, first_name, last_name, role):
        """
        Add a user to the database using individual parameters.
        This is a wrapper around the User model for backward compatibility.
        """
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

        try:
            user = User(
                username=username,
                password_plain=password,
                role=role,
                first_name=first_name,
                last_name=last_name
            )
            self.add_user(user)
            return True, "User added successfully"
        except ValueError as e:
            return False, str(e)

    def add_user(self, user):
        """
        Add a user to the database. The user object should already have encrypted data.
        
        Args:
            user: User object with encrypted username, password_hash, first_name, and last_name
        """
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
