import sqlite3
from utils.crypto_utils import hash_password, decrypt, check_password, encrypt
from models.user import User, USERNAME_RE, PWD_ALLOWED_RE
import re
from typing import Tuple

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


#-------------------------------------------------
#                   Add User
#-------------------------------------------------
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
        
        
    def update_user(self, user_id: int, **updates) -> Tuple[bool, str]:
        """Update *one or more* fields of a user."""
        
        if not updates:
            return False, "No updates provided"
        
        # Only validate fields that are being updated
        validations = []
        if "first_name" in updates:
            validations.append(self.validate_name(updates["first_name"], "First name"))
        if "last_name" in updates:
            validations.append(self.validate_name(updates["last_name"], "Last name"))
        if "username" in updates:
            validations.append(self.validate_username(updates["username"]))
        if "password" in updates:
            validations.append(self.validate_password(updates["password"]))
        if "role" in updates:
            validations.append(self.validate_role(updates["role"]))
            
        for ok, msg in validations:
            if not ok:
                return False, msg

        # Get current user data
        current_user = self.get_user_by_id(user_id)
        if not current_user:
            return False, "User not found"

        # Check for username uniqueness if username is being updated
        if "username" in updates:
            new_username = updates["username"].lower()
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT user_id FROM User WHERE username = ?', (encrypt(new_username),))
            row = c.fetchone()
            conn.close()
            if row and row[0] != user_id:
                return False, "Username already exists. Please choose a different one."

        # Update database directly instead of creating a User object
        conn = self._get_connection()
        c = conn.cursor()
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if "username" in updates:
            update_fields.append("username = ?")
            update_values.append(encrypt(updates["username"].lower()))
        if "first_name" in updates:
            update_fields.append("first_name = ?")
            update_values.append(encrypt(updates["first_name"]))
        if "last_name" in updates:
            update_fields.append("last_name = ?")
            update_values.append(encrypt(updates["last_name"]))
        if "role" in updates:
            update_fields.append("role = ?")
            update_values.append(encrypt(updates["role"]))
        if "password" in updates:
            update_fields.append("password_hash = ?")
            update_values.append(hash_password(updates["password"]))
            
        if not update_fields:
            return False, "No valid fields to update"
            
        # Add user_id to values for WHERE clause
        update_values.append(user_id)
        
        # Execute update
        query = f"UPDATE User SET {', '.join(update_fields)} WHERE user_id = ?"
        c.execute(query, update_values)
        conn.commit()
        conn.close()
        
        return True, "User updated successfully"

#-------------------------------------------------
#                   List Users
#-------------------------------------------------
    def list_users(self):
        """List all users in the system."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role FROM User')
        rows = c.fetchall()
        conn.close()
        return [
            {
                "user_id": row[0],
                "username": decrypt(row[1]),
                "first_name": decrypt(row[2]),
                "last_name": decrypt(row[3]),
                "role": decrypt(row[4])
            } for row in rows
        ]
        
    
        
#-------------------------------------------------
#                   Delete User
#-------------------------------------------------
    def delete_user(self, user_id: int, username: str) -> Tuple[bool, str]:
        """Delete a user from the database."""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('DELETE FROM User WHERE user_id=?', (user_id,))
            c.execute('DELETE FROM User WHERE username=?', (username,))
            conn.commit()
            conn.close()
            return True, "User deleted successfully"
        except ValueError as e:
            return False, str(e)
        
#-------------------------------------------------
#                   Get User
#-------------------------------------------------
    def get_user_by_id(self, user_id):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role, registration_date FROM User WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "user_id": row[0],
                "username": decrypt(row[1]),
                "first_name": decrypt(row[2]),
                "last_name": decrypt(row[3]),
                "role": decrypt(row[4]),
                "registration_date": row[5]
            }
        return None
    
#-------------------------------------------------
#                   Get User by Username
#-------------------------------------------------
    def get_user_by_username(self, username):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role, registration_date FROM User')
        users = c.fetchall()
        conn.close()
        for row in users:
            if decrypt(row[1]) == username:
                return {
                    "user_id": row[0],
                    "username": decrypt(row[1]),
                    "first_name": decrypt(row[2]),
                    "last_name": decrypt(row[3]),
                    "role": decrypt(row[4]),
                    "registration_date": row[5]
                }
        return None
        
#-------------------------------------------------
#                   Verify User Password
#-------------------------------------------------
    def verify_user_password(self, user_id, password):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM User WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return check_password(password, row[0])
        return False


#-------------------------------------------------
#                   Update Password
#-------------------------------------------------
    def update_password(self, user_id, new_password):
        conn = self._get_connection()
        c = conn.cursor()
        hashed = hash_password(new_password)
        c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
        conn.commit()
        conn.close()

# Create a single instance of UserService
user_service = UserService("urban_mobility.db")
