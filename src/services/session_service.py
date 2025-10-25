import sqlite3
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from services.log_service import log_login_attempt, unread_suspicious_count
from services.userservice import user_service
from models.user import User
from utils.crypto_utils import decrypt

class SessionService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._current_user = None
        self._current_user_id = None
        self._current_username = None
        self._current_role = None
        self._global_failed_attempts = 0
        self._global_lockout_end = None
        
        # Whitelist of allowed usernames and roles
        self._allowed_usernames = {"super_admin", "john_admin", "john_engi"}
        self._allowed_roles = {"super", "system_admin", "service_engineer"}
        
        # Whitelist of allowed login times (24/7 for now, can be restricted)
        self._allowed_login_hours = list(range(24))  # 0-23 hours
        
        # Whitelist of allowed IP patterns (if needed in future)
        self._allowed_ip_patterns = ["*"]  # Allow all for now

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            raise

    def _is_username_allowed(self, username: str) -> bool:
        """Check if username is in whitelist."""
        return username in self._allowed_usernames

    def _is_role_allowed(self, role: str) -> bool:
        """Check if role is in whitelist."""
        return role in self._allowed_roles

    def _is_login_time_allowed(self) -> bool:
        """Check if current time is in allowed login hours."""
        current_hour = datetime.now().hour
        return current_hour in self._allowed_login_hours

    def _is_user_in_whitelist(self, username: str) -> bool:
        """Check if user is explicitly whitelisted (TRUE WHITELIST - default deny)."""
        # Only allow users who are explicitly in the whitelist
        return username in self._allowed_usernames

    def _handle_failed_attempt(self):
        """Handle a failed login attempt with lockout after 3 failed attempts."""
        self._global_failed_attempts += 1
        failed_count = self._global_failed_attempts
        
        # Lock system after 3 failed attempts
        if failed_count >= 3:
            # Lock system for 15 seconds (reduced for testing)
            timeout_seconds = 15
            self._global_lockout_end = datetime.now() + timedelta(seconds=timeout_seconds)
            print(f"System locked for {timeout_seconds} seconds due to {failed_count} failed attempts.")
        else:
            # Show remaining attempts before lockout
            remaining_attempts = 3 - failed_count
            print(f"Login failed. {remaining_attempts} attempts remaining before system lockout.")

    def _check_system_lockout(self) -> bool:
        """Check if system is currently locked out."""
        if self._global_lockout_end and datetime.now() < self._global_lockout_end:
            remaining_seconds = int((self._global_lockout_end - datetime.now()).total_seconds())
            print(f"System temporarily locked due to multiple failed attempts.")
            print(f"Please wait {remaining_seconds} seconds before trying again.")
            return True
        elif self._global_lockout_end and datetime.now() >= self._global_lockout_end:
            # Lockout period has expired, reset failed attempts
            self._global_failed_attempts = 0
            self._global_lockout_end = None
        return False

    def login(self, username: str, password: Optional[str] = None) -> bool:
        """Authenticate user login with whitelist approach."""
        # Check for exit command
        if username.lower() == 'exit':
            print("Exiting system...")
            sys.exit(0)
        
        # Check if system is locked
        if self._check_system_lockout():
            return False
        
        # Check if login time is allowed
        if not self._is_login_time_allowed():
            print("Login not allowed at this time.")
            return False
        
        # Check for hardcoded super admin (whitelisted)
        if username == "super_admin" and password == "Admin_123?":
            return self._handle_super_admin_login()
        
        # Check if user is in whitelist (exists and is active)
        if not self._is_user_in_whitelist(username):
            self._handle_failed_attempt()
            print("Access denied. User not authorized.")
            log_login_attempt(username, False)
            return False
        
        # Get user data for regular users
        user_data = user_service.get_user_by_username(username)
        if not user_data:
            self._handle_failed_attempt()
            print("Access denied. User not found.")
            log_login_attempt(username, False)
            return False
        
        # Check if user role is allowed
        if not self._is_role_allowed(user_data.role_plain):
            self._handle_failed_attempt()
            print("Access denied. Insufficient privileges.")
            log_login_attempt(username, False)
            return False
        
        # Handle password reset flow if needed
        if self._needs_password_reset(user_data):
            return self._handle_password_reset(user_data)
        
        # Get password if not provided
        if password is None:
            password = input("Password: ")
            if password.lower() == 'exit':
                print("Exiting system...")
                sys.exit(0)
        
        # Verify password
        if not user_service.verify_user_password(user_data.user_id, password):
            self._handle_failed_attempt()
            print("Access denied. Invalid credentials.")
            log_login_attempt(username, False)
            return False
        
        # Successful login
        return self._complete_successful_login(user_data, password, username)

    def _handle_super_admin_login(self) -> bool:
        """Handle super admin login."""
        self._current_user = User(
            username="super_admin",
            password_plain="Admin_123?",
            role="super"
        )
        self._current_user_id = 0
        self._current_username = "super_admin"
        self._current_role = "super"
        print(f"Logged in as {self._current_username} ({self._current_role})")
        
        # Reset failed attempts on successful login
        self._global_failed_attempts = 0
        self._global_lockout_end = None
        
        # Check for suspicious activities
        self._check_suspicious_activities()
        
        log_login_attempt("super_admin", True)
        return True

    def _needs_password_reset(self, user_data) -> bool:
        """Check if user needs password reset."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM User WHERE user_id = ?', (user_data.user_id,))
        row = c.fetchone()
        conn.close()
        
        return (row and row[0] is None) or user_service.has_pending_reset(user_data.user_id)

    def _handle_password_reset(self, user_data) -> bool:
        """Handle password reset flow."""
        from dashboard.menus.password_reset_menu import use_reset_code_flow
        print("\nA password reset has been requested for your account.")
        if use_reset_code_flow(user_data.user_id):
            print("Password reset successful. Please log in with your new password.")
            return False  # Force user to log in again with new password
        else:
            print("Password reset failed or cancelled.")
            return False

    def _complete_successful_login(self, user_data, password: str, username: str) -> bool:
        """Complete the successful login process."""
        # Reset failed attempts
        self._global_failed_attempts = 0
        self._global_lockout_end = None
        
        # Create User object
        self._current_user = User(
            username=user_data.username_plain,
            password_plain=password,
            role=user_data.role_plain,
            first_name=decrypt(user_data.first_name) if user_data.first_name else None,
            last_name=decrypt(user_data.last_name) if user_data.last_name else None
        )
        self._current_user_id = user_data.user_id
        self._current_username = user_data.username_plain
        self._current_role = user_data.role_plain
        print(f"Logged in as {self._current_username} ({self._current_role})")
        
        # Check for suspicious activities (only for sys/super)
        if self._current_role in ("system_admin", "super"):
            self._check_suspicious_activities()
        
        log_login_attempt(username, True)
        return True

    def _check_suspicious_activities(self):
        """Check and display suspicious activities."""
        cnt = unread_suspicious_count(self._current_user_id)
        if cnt:
            print(f"\n⚠  There are {cnt} unread suspicious activities in the log!"
                  "  Open 'View system logs' to review.\n")
            input("Press Enter to continue...")

    def logout(self):
        """Logout current user."""
        self._current_user = None
        self._current_user_id = None
        self._current_username = None
        self._current_role = None
        print("Logged out successfully.")
        # Return to login by raising a special exception
        raise SystemError("User logged out")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self._current_user is not None

    def get_current_user(self) -> Optional[User]:
        """Get current user object."""
        return self._current_user

    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID."""
        return self._current_user_id

    def get_current_username(self) -> Optional[str]:
        """Get current username."""
        return self._current_username

    def get_current_role(self) -> Optional[str]:
        """Get current user role."""
        return self._current_role

    def add_allowed_username(self, username: str) -> bool:
        """Add username to whitelist."""
        if username not in self._allowed_usernames:
            self._allowed_usernames.add(username)
            return True
        return False

    def remove_allowed_username(self, username: str) -> bool:
        """Remove username from whitelist."""
        if username in self._allowed_usernames:
            self._allowed_usernames.remove(username)
            return True
        return False

    def add_allowed_role(self, role: str) -> bool:
        """Add role to whitelist."""
        if role not in self._allowed_roles:
            self._allowed_roles.add(role)
            return True
        return False

    def remove_allowed_role(self, role: str) -> bool:
        """Remove role from whitelist."""
        if role in self._allowed_roles:
            self._allowed_roles.remove(role)
            return True
        return False

    def set_allowed_login_hours(self, hours: list) -> bool:
        """Set allowed login hours (0-23)."""
        if all(0 <= hour <= 23 for hour in hours):
            self._allowed_login_hours = hours
            return True
        return False

    def get_whitelist_status(self) -> dict:
        """Get current whitelist configuration."""
        return {
            "allowed_usernames": list(self._allowed_usernames),
            "allowed_roles": list(self._allowed_roles),
            "allowed_login_hours": self._allowed_login_hours,
            "failed_attempts": self._global_failed_attempts,
            "is_locked": self._global_lockout_end is not None and datetime.now() < self._global_lockout_end
        }

# Create global instance
session_service = SessionService("urban_mobility.db")
