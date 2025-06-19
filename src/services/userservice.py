import sqlite3
from utils.crypto_utils import hash_password, decrypt, check_password, encrypt
from models.user import User, USERNAME_RE, PWD_ALLOWED_RE
import re
from typing import Tuple
import random
import string
from datetime import datetime, timedelta
import os

class UserService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        # print(f"[DEBUG] _get_connection called, connecting to: {self.db_path}")
        try:
            conn = sqlite3.connect(self.db_path)
            # print(f"[DEBUG] Database connection successful")
            return conn
        except Exception as e:
            # print(f"[DEBUG] Database connection failed: {e}")
            raise

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
        if len(name) < 2 or len(name) > 20:
            return False, f"{field_name} must be between 2 and 20 characters"
        return True, ""


#-------------------------------------------------
#                   Add User
#-------------------------------------------------
    def add_user(self, username=None, password=None, first_name=None, last_name=None, role=None, user=None) -> Tuple[bool, str]:
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

                # Check if username already exists by comparing decrypted usernames
                conn = self._get_connection()
                c = conn.cursor()
                c.execute('SELECT username FROM User')
                rows = c.fetchall()
                conn.close()
                for row in rows:
                    if decrypt(row[0]).lower() == username.lower():
                        return False, "Username already exists. Please choose a different one."

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
            # First check if the new username is different from current username
            if new_username == current_user.username_plain.lower():
                return False, "New username must be different from current username"
            
            # Then check if the new username exists for any other user by comparing decrypted usernames
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT user_id, username FROM User')
            rows = c.fetchall()
            conn.close()
            for row in rows:
                if row[0] != user_id and decrypt(row[1]).lower() == new_username:
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
    def list_users(self) -> list[User]:
        """List all users in the system."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role, registration_date, password_hash FROM User')
        rows = c.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            try:
                user = User(
                    user_id=row[0],
                    username=decrypt(row[1]),
                    first_name=decrypt(row[2]),
                    last_name=decrypt(row[3]),
                    role=decrypt(row[4]),
                    password_hash=row[6]  # Use the stored password hash
                )
                # Set the registration_date from database if it exists
                if row[5]:
                    user.registration_date = row[5]
                users.append(user)
            except Exception as e:
                print(f"Error processing user row {row[0]}: {e}")
                continue
        return users
        
    
        
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
    def get_user_by_id(self, user_id) -> User:
        """Get user details by user_id."""
        # print(f"[DEBUG] get_user_by_id called with user_id: {user_id}")
        # print(f"[DEBUG] Using database path: {self.db_path}")
        
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role, registration_date, password_hash FROM User WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        # print(f"[DEBUG] Database query returned row: {row}")
        
        if row:
            try:
                user = User(
                    user_id=row[0],
                    username=decrypt(row[1]),
                    first_name=decrypt(row[2]),
                    last_name=decrypt(row[3]),
                    role=decrypt(row[4]),
                    password_hash=row[6]  # Use the stored password hash
                )
                # Set the registration_date from database if it exists
                if row[5]:
                    user.registration_date = row[5]
                # print(f"[DEBUG] Successfully created User object: {user}")
                return user
            except Exception as e:
                # Optionally log the error here
                # print(f"[DEBUG] Error creating User object: {e}")
                # print(f"[DEBUG] Invalid user data in DB: {e}")
                return None
        else:
            # print(f"[DEBUG] No user found in database for user_id: {user_id}")
            return None
        # return None
    
#-------------------------------------------------
#                   Get User by Username
#-------------------------------------------------
    def get_user_by_username(self, username) -> User:
        """Get user details by username."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, last_name, role, registration_date, password_hash FROM User')
        users = c.fetchall()
        conn.close()
        
        # Normalize input username to lowercase for comparison
        username_lower = username.lower()
        
        for row in users:
            try:
                decrypted_username = decrypt(row[1])
                if decrypted_username.lower() == username_lower:
                    # Handle NULL password_hash by providing a default empty string
                    password_hash = row[6] if row[6] is not None else b''
                    
                    user = User(
                        user_id=row[0],
                        username=decrypt(row[1]),
                        first_name=decrypt(row[2]),
                        last_name=decrypt(row[3]),
                        role=decrypt(row[4]),
                        password_hash=password_hash  # Use the stored password hash or empty bytes if NULL
                    )
                    # Set the registration_date from database if it exists
                    if row[5]:
                        user.registration_date = row[5]
                    return user
            except Exception as e:
                # Optionally log the error here
                print(f"Error decrypting user data: {e}")
                continue
        return None
        
#-------------------------------------------------
#                   Verify User Password
#-------------------------------------------------
    def verify_user_password(self, user_id, password) -> bool:
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
    def update_password(self, user_id, new_password) -> None:
        conn = self._get_connection()
        c = conn.cursor()
        hashed = hash_password(new_password)
        c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
        conn.commit()
        conn.close()

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user's password by verifying current password first.
        
        Args:
            user_id: ID of the user
            current_password: Current password to verify
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        # Verify current password
        if not self.verify_user_password(user_id, current_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        valid, message = self.validate_password(new_password)
        if not valid:
            return False, message
        
        # Update password
        try:
            self.update_password(user_id, new_password)
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Failed to update password: {str(e)}"

    def generate_temp_code(self, admin_id: int, target_user_id: int) -> Tuple[bool, str]:
        """
        Generate a temporary code for password reset.
        Only system admin can reset service engineer passwords.
        Super admin can reset both system admin and service engineer passwords.
        """
        # Special-case for hardcoded super admin
        if admin_id == 0:
            admin_role = 'super'
        else:
            admin = self.get_user_by_id(admin_id)
            if not admin:
                return False, "Admin user not found"
            admin_role = admin.role_plain
            
        target = self.get_user_by_id(target_user_id)
        if not target:
            return False, "Target user not found"
            
        # Check permissions
        if admin_role == "system_admin":
            if target.role_plain != "service_engineer":
                return False, "System admin can only reset service engineer passwords"
        elif admin_role == "super":
            if target.role_plain not in ("system_admin", "service_engineer"):
                return False, "Super admin can only reset system admin or service engineer passwords"
        else:
            return False, "Only system admin or super admin can reset passwords"

        # Generate a 5-digit code
        code = ''.join(random.choices(string.digits, k=5))
        
        # Store the code
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            # Remove any existing code for this user
            c.execute('DELETE FROM TempCodes WHERE user_id = ?', (target_user_id,))
            # Set the user's password_hash to NULL
            c.execute('UPDATE User SET password_hash = NULL WHERE user_id = ?', (target_user_id,))
            
            # Insert new code
            c.execute('INSERT INTO TempCodes (user_id, code) VALUES (?, ?)',
                     (target_user_id, encrypt(code)))
            conn.commit()
            
            # Verify the code was stored correctly
            c.execute('SELECT code FROM TempCodes WHERE user_id = ?', (target_user_id,))
            stored = c.fetchone()
            if not stored or decrypt(stored[0]) != code:
                return False, "Failed to store reset code properly"
                
            return True, code
        except Exception as e:
            conn.rollback()
            return False, f"Error storing reset code: {str(e)}"
        finally:
            conn.close()

    def verify_temp_code(self, user_id: int, code: str) -> bool:
        """Verify if the temporary code is valid for the user."""
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            # Get the stored code
            c.execute('SELECT code, created_at FROM TempCodes WHERE user_id = ?', (user_id,))
            row = c.fetchone()
            
            if not row:
                print("No reset code found for user")  # Debug
                return False
                
            stored_code, created_at = row
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            
            # Check if code is expired (10 minutes)
            # if datetime.now() - created_at > timedelta(minutes=10):
            #     print("Reset code has expired")  # Debug
            #     return False
                
            # Compare codes - decrypt the stored code before comparing
            decrypted_code = decrypt(stored_code)
            # print(f"Comparing codes - Input: {code}, Stored: {decrypted_code}")  # Debug
            return decrypted_code == code
        except Exception as e:
            print(f"Error verifying code: {str(e)}")  # Debug
            return False
        finally:
            conn.close()

    def reset_password_with_code(self, user_id: int, code: str, new_password: str) -> Tuple[bool, str]:
        """Reset password using temporary code."""
        # Verify code
        if not self.verify_temp_code(user_id, code):
            return False, "Invalid or expired code"
            
        # Validate new password
        valid, message = self.validate_password(new_password)
        if not valid:
            return False, message
            
        # Update password
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?',
                 (hash_password(new_password), user_id))
        conn.commit()
        
        # Remove used code
        c.execute('DELETE FROM TempCodes WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return True, "Password reset successfully"

    def has_pending_reset(self, user_id: int) -> bool:
        """Check if user has a pending password reset."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT 1 FROM TempCodes WHERE user_id = ?', (user_id,))
        has_reset = c.fetchone() is not None
        conn.close()
        return has_reset

# Create a singleton instance with absolute path
SRC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(SRC_FOLDER, 'urban_mobility.db')
user_service = UserService(DB_FILE)
