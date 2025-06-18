# namespace: controllers

from models.user import User
from services.userservice import user_service
from utils.role_utils import require_role
from controllers.session import UserSession
from utils.log_decorator import log_action
from typing import Tuple, List

class UserController:
    #--------------------------------------------------------------------------------------
    #                   Change Password
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Change password -> {msg}")
    @require_role("service_engineer", "system_admin")
    def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user's own password."""
        return user_service.change_password(user_id, current_password, new_password)

    #--------------------------------------------------------------------------------------
    #                   Add User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Add user -> {msg}")
    @require_role("system_admin", "super")
    def add_user(current_user_id: int, username: str, password: str, first_name: str, last_name: str, role: str) -> Tuple[bool, str]:
        """Add a new user to the system."""
        # Validate new user data using User model
        try:
            new_user = User(
                username=username,
                password_plain=password,
                role=role,
                first_name=first_name,
                last_name=last_name
            )
        except ValueError as e:
            return False, str(e)

        return user_service.add_user(user=new_user)

    @staticmethod
    def add_user(username, password, first_name, last_name, role):
        """Direct wrapper for adding a user without role checks."""
        return user_service.add_user(username, password, first_name, last_name, role)
    
    #--------------------------------------------------------------------------------------
    #                   Update User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Update user -> {msg}")
    @require_role("system_admin", "super")
    def update_user(current_user_id: int, user_id: int, **updates) -> Tuple[bool, str]:
        """Update user information."""
        # Validate updates using User model
        if "password" in updates:
            new_password = updates["password"]
            user = user_service.get_user_by_id(user_id)
            if not user:
                return False, "User not found."

            # Validate new password using User model
            try:
                User(username=user.username_plain, password_plain=new_password, role=user.role_plain)
            except ValueError as e:
                return False, str(e)

        # Check permissions
        current_user = user_service.get_user_by_id(current_user_id)
        if not current_user:
            return False, "Current user not found."

        if current_user.role_plain == "system_admin":
            target_user = user_service.get_user_by_id(user_id)
            if not target_user:
                return False, "User not found."
            if target_user.role_plain == "service_engineer" or user_id == current_user_id:
                return user_service.update_user(user_id, **updates)
            else:
                return False, "System admins can only update service engineers or themselves."
        else:
            # Super admin can update anyone
            return user_service.update_user(user_id, **updates)

    #--------------------------------------------------------------------------------------
    #                   Delete User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Delete user -> {msg}")
    @require_role("system_admin", "super")
    def delete_user(current_user_id: int, user_id: int, username: str) -> Tuple[bool, str]:
        """Delete a user from the system."""
        # Check permissions
        current_user = user_service.get_user_by_id(current_user_id)
        if not current_user:
            return False, "Current user not found."

        if current_user.role_plain == "system_admin":
            target_user = user_service.get_user_by_id(user_id)
            if not target_user:
                return False, "User not found."
            if target_user.role_plain == "service_engineer" or user_id == current_user_id:
                return user_service.delete_user(user_id, username)
            else:
                return False, "System admins can only delete service engineers or themselves."
        else:
            # Super admin can delete anyone
            return user_service.delete_user(user_id, username)
    
    #--------------------------------------------------------------------------------------
    #                   List Users
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("List users -> {msg}")
    @require_role("system_admin", "super")
    def list_users(current_user_id: int) -> List[User]:
        """List all users in the system."""
        return user_service.list_users()
    
    #--------------------------------------------------------------------------------------
    #                   Change Password
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Change own password -> {msg}")
    @require_role("service_engineer", "system_admin")
    def change_own_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user's own password."""
        return user_service.change_password(user_id, current_password, new_password)




