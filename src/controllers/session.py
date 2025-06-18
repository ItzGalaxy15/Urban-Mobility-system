from services.log_service import log_login_attempt
from services.userservice import user_service
from models.user import User
import sys
import os

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
            log_login_attempt(username, True)          # successful login
            return True

        # Regular user login
        user_data = user_service.get_user_by_username(username)
        if not user_data:
            print("Username or password incorrect.")
            log_login_attempt(username, False)         # failed login
            return False

        # Check if password_hash is NULL (no password set)
        conn = user_service._get_connection()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM User WHERE user_id = ?', (user_data["user_id"],))
        row = c.fetchone()
        conn.close()
        if row and row[0] is None:
            # Password is missing, force reset code flow
            from dashboard.menus.password_reset_menu import use_reset_code_flow
            # print("\nA password reset has been requested for your account.")
            if use_reset_code_flow(user_data["user_id"]):
                print("Password reset successful. Please log in with your new password.")
                return False  # Force user to log in again with new password
            else:
                print("Password reset failed or cancelled.")
                return False

        # Check for pending password reset (legacy, in case password_hash is not NULL but reset is pending)
        if user_service.has_pending_reset(user_data["user_id"]):
            from dashboard.menus.password_reset_menu import use_reset_code_flow
            # print("\nA password reset has been requested for your account.")
            if use_reset_code_flow(user_data["user_id"]):
                print("Password reset successful. Please log in with your new password.")
                return False  # Force user to log in again with new password
            else:
                print("Password reset failed or cancelled.")
                return False

        # If no reset is pending, proceed with normal password check
        if password is None:
            password = input("Password: ")
        if not user_service.verify_user_password(user_data["user_id"], password):
            print("Password incorrect.")
            log_login_attempt(username, False)         # failed login
            return False
        
        # Create User object for regular users
        UserSession._current_user = User(
            username=user_data["username"],
            password_plain=password,  # We already verified it's correct
            role=user_data["role"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        UserSession._current_user_id = user_data["user_id"]
        UserSession._current_username = user_data["username"]
        UserSession._current_role = user_data["role"]
        print(f"Logged in as {UserSession._current_username} ({UserSession._current_role})")
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
        raise SystemExit(0)  # This will exit the current loop and return to main()

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
