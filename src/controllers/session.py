from services.log_service import log_login_attempt
from services.log_service import unread_suspicious_count
from services.userservice import user_service
from models.user import User
import sys
import os

from utils.crypto_utils import decrypt

class UserSession:
    _current_user = None
    _current_user_id = None
    _current_username = None
    _current_role = None

    @staticmethod
    def login(username, password=None):
        # Check for hardcoded super admin
        if username == "super_admin" and password == "Admin_123?":
            # Create a proper User object for super admin
            UserSession._current_user = User(
                username="super_admin",
                password_plain="Admin_123?",
                role="super"
            )
            UserSession._current_user_id = 0  # Special ID for super admin
            UserSession._current_username = "super_admin"
            UserSession._current_role = "super"
            print(f"Logged in as {UserSession._current_username} ({UserSession._current_role})")

            # ---- unread-suspicious alert ----
            cnt = unread_suspicious_count(UserSession._current_user_id)
            if cnt:
                print(f"\n⚠  There are {cnt} unread suspicious activities in the log!"
                    "  Open 'View system logs' to review.\n")
            # ---------------------------------

            log_login_attempt(username, True)  # successful login
            return True

        # Get password if not provided
        if password is None:
            password = input("Password: ")

        # Regular user login - check database only after both username and password are provided
        user_data = user_service.get_user_by_username(username)
        if not user_data:
            print("Username or password incorrect.")
            log_login_attempt(username, False)         # failed login
            return False

        # Check if password_hash is NULL (no password set)
        conn = user_service._get_connection()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM User WHERE user_id = ?', (user_data.user_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0] is None:
            # Password is missing, force reset code flow
            from dashboard.menus.password_reset_menu import use_reset_code_flow
            # print("\nA password reset has been requested for your account.")
            if use_reset_code_flow(user_data.user_id):
                print("Password reset successful. Please log in with your new password.")
                return False  # Force user to log in again with new password
            else:
                print("Password reset failed or cancelled.")
                return False

        # Check for pending password reset (legacy, in case password_hash is not NULL but reset is pending)
        if user_service.has_pending_reset(user_data.user_id):
            from dashboard.menus.password_reset_menu import use_reset_code_flow
            # print("\nA password reset has been requested for your account.")
            if use_reset_code_flow(user_data.user_id):
                print("Password reset successful. Please log in with your new password.")
                return False  # Force user to log in again with new password
            else:
                print("Password reset failed or cancelled.")
                return False

        # If no reset is pending, proceed with normal password check
        if not user_service.verify_user_password(user_data.user_id, password):
            print("Username or password incorrect.")
            log_login_attempt(username, False)         # failed login
            return False
        
        # Create User object for regular users
        UserSession._current_user = User(
            username=user_data.username_plain,
            password_plain=password,  # We already verified it's correct
            role=user_data.role_plain,
            first_name=decrypt(user_data.first_name) if user_data.first_name else None,
            last_name=decrypt(user_data.last_name) if user_data.last_name else None
        )
        UserSession._current_user_id = user_data.user_id
        UserSession._current_username = user_data.username_plain
        UserSession._current_role = user_data.role_plain
        print(f"Logged in as {UserSession._current_username} ({UserSession._current_role})")

        # ---- unread-suspicious alert (only for sys/super) ----
        if UserSession._current_role in ("system_admin", "super"):
            cnt = unread_suspicious_count(UserSession._current_user_id)
            if cnt:
                print(f"\n⚠  There are {cnt} unread suspicious activities in the log!"
                    "  Open 'View system logs' to review.\n")
        # ------------------------------------------------------
        log_login_attempt(username, True)              # successful login
        return True

    @staticmethod
    def logout():
        UserSession._current_user = None
        UserSession._current_user_id = None
        UserSession._current_username = None
        UserSession._current_role = None
        print("Logged out successfully.")
        # Return to login by raising a special exception
        raise SystemError("User logged out")  # This will exit the current loop and return to main()

    @staticmethod
    def is_authenticated():
        return UserSession._current_user is not None

    @staticmethod
    def get_current_user():
        return UserSession._current_user

    @staticmethod
    def get_current_user_id():
        return UserSession._current_user_id

    @staticmethod
    def get_current_username():
        return UserSession._current_username

    @staticmethod
    def get_current_role():
        return UserSession._current_role
