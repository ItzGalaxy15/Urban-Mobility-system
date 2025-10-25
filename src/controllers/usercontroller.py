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
        # Super admin doesn't need password change through this method
        if user_id == 0:
            return False, "Super admin password cannot be changed through this method."
        return user_service.change_password(user_id, current_password, new_password)

    #--------------------------------------------------------------------------------------
    #                   Add User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Add user -> {msg}")
    @require_role("system_admin", "super")
    def add_user(user_id: int, username: str, password: str, first_name: str, last_name: str, role: str) -> Tuple[bool, str]:
        """Add a new user to the system."""
        # Check permissions - handle super admin case
        if user_id == 0:
            # Super admin case - can add any role
            current_user_role = "super"
        else:
            current_user = user_service.get_user_by_id(user_id)
            if not current_user:
                return False, "Current user not found."
            current_user_role = current_user.role_plain

        # System admin can only add service_engineer roles
        if current_user_role == "system_admin":
            if role != "service_engineer":
                return False, "System admins can only add service engineers."
        
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

    #--------------------------------------------------------------------------------------
    #                   Update User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Update user -> {msg}")
    @require_role("system_admin", "super")
    def update_user(user_id: int, target_user_id: int, **updates) -> Tuple[bool, str]:
        """Update user information."""
        # Validate updates using User model
        if "password" in updates:
            new_password = updates["password"]
            user = user_service.get_user_by_id(target_user_id)
            if not user:
                return False, "User not found."

            # Validate new password using User model
            try:
                User(username=user.username_plain, password_plain=new_password, role=user.role_plain)
            except ValueError as e:
                return False, str(e)

        # Check permissions - handle super admin case
        if user_id == 0:
            # Super admin case - can update anyone
            current_user_role = "super"
        else:
            current_user = user_service.get_user_by_id(user_id)
            if not current_user:
                return False, "Current user not found."
            current_user_role = current_user.role_plain

        if current_user_role == "system_admin":
            target_user = user_service.get_user_by_id(target_user_id)
            if not target_user:
                return False, "User not found."
            
            # System admin can only update service_engineer, NOT other system_admins or super admins
            if target_user.role_plain != "service_engineer":
                return False, "System admins can only update service engineers."
            
            # Check if trying to escalate the target user's role
            if "role" in updates:
                if updates["role"] != "service_engineer":
                    return False, "System admins cannot escalate roles."
            
            return user_service.update_user(target_user_id, **updates)
        else:
            # Super admin can update anyone, but check for self privilege escalation
            if user_id != 0 and target_user_id == user_id and "role" in updates:
                current_user = user_service.get_user_by_id(user_id)
                if current_user and updates["role"] != current_user.role_plain:
                    return False, "Users cannot change their own role."
            
            return user_service.update_user(target_user_id, **updates)

    #--------------------------------------------------------------------------------------
    #                   Delete User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("Delete user -> {msg}")
    @require_role("system_admin", "super")
    def delete_user(user_id: int, target_user_id: int, username: str) -> Tuple[bool, str]:
        """Delete a user from the system."""
        # Check permissions - handle super admin case
        if user_id == 0:
            # Super admin case - can delete anyone
            current_user_role = "super"
        else:
            current_user = user_service.get_user_by_id(user_id)
            if not current_user:
                return False, "Current user not found."
            current_user_role = current_user.role_plain

        if current_user_role == "system_admin" or user_id == target_user_id:
            target_user = user_service.get_user_by_id(target_user_id)
            if not target_user:
                return False, "User not found."
            # System admin can only delete service_engineer, NOT other system_admins or themselves
            if target_user.role_plain == "service_engineer":
                return user_service.delete_user(target_user_id, username)
            else:
                return False, "System admins can only delete service engineers."
        else:
            # Super admin can delete anyone
            return user_service.delete_user(target_user_id, username)
    
    #--------------------------------------------------------------------------------------
    #                   List Users
    #--------------------------------------------------------------------------------------
    @staticmethod
    @log_action("List users -> {msg}")
    @require_role("system_admin", "super")
    def list_users(user_id: int) -> List[User]:
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
        # Super admin doesn't need password change through this method
        if user_id == 0:
            return False, "Super admin password cannot be changed through this method."
        return user_service.change_password(user_id, current_password, new_password)




