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
    def login(username, password):
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
            return True

        # Regular user login
        user_data = user_service.get_user_by_username(username)
        if not user_data:
            print("Username or password incorrect.")
            return False
        if not user_service.verify_user_password(user_data["user_id"], password):
            print("Password incorrect.")
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
