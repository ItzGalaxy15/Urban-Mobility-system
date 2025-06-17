# namespace: controllers

from models.user import User
from services.userservice import user_service
from utils.role_utils import require_role
from controllers.session import UserSession

class UserController:
    #--------------------------------------------------------------------------------------
    #                   Change Password
    #--------------------------------------------------------------------------------------
    @staticmethod
    @require_role("service_engineer", "system_admin")
    def change_password(user_id, old_password, new_password):
        # Special case for super admin
        if user_id == 0:
            if old_password != "Admin_123?":
                return False, "Old password is incorrect."

            # Validate new password for super admin
            try:
                User(username="dummy", password_plain=new_password, role="super")
            except ValueError as e:
                return False, str(e)
            # For super admin, we don't actually change the password since it's hardcoded
            return True, "Password updated successfully."

        # Regular user password change
        user = user_service.get_user_by_id(user_id)
        if not user:
            return False, "User not found."

        # Check old password
        if not user_service.verify_user_password(user_id, old_password):
            return False, "Old password is incorrect."

        # Validate new password using User model
        try:
            User(username=user["username"], password_plain=new_password, role=user["role"])
        except ValueError as e:
            return False, str(e)

        # Update password
        user_service.update_password(user_id, new_password)
        return True, "Password updated successfully."

    #--------------------------------------------------------------------------------------
    #                   Add User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @require_role("system_admin", "super")
    def add_user_controller(current_user_id, username, password, first_name, last_name, role):
        """
        Add a new user to the system.
        Only super admins can add system admins.
        System admins can only add service engineers.
        """
        # Get current user's role
        current_role = UserSession.get_current_role()
        
        # Check if current user has permission to add the specified role
        if role == "system_admin" and current_role != "super":
            return False, "Only super admins can add system admins"
        if role == "service_engineer" and current_role not in ["super", "system_admin"]:
            return False, "Only super admins and system admins can add service engineers"
        
        # Check if username already exists
        if user_service.get_user_by_username(username):
            return False, "Username already exists"
        
        # Add the user
        return user_service.add_user(username, password, first_name, last_name, role)

    @staticmethod
    def add_user(username, password, first_name, last_name, role):
        """Direct wrapper for adding a user without role checks."""
        return user_service.add_user(username, password, first_name, last_name, role)
    
    #--------------------------------------------------------------------------------------
    #                   Update User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @require_role("system_admin", "super")
    def update_user(current_user_id, user_id, **updates):
        """
        Update a user in the system.
        Only super admins can update super admin and system admins.
        System admins can update service engineers or themselves.
        """
        current_role = UserSession.get_current_role()
        if current_role == "super":
            return user_service.update_user(user_id, **updates)
        elif current_role == "system_admin":
            # System admins can update service engineers or themselves
            target_user = user_service.get_user_by_id(user_id)
            if not target_user:
                return False, "User not found."
            if target_user["role"] == "service_engineer" or user_id == current_user_id:
                return user_service.update_user(user_id, **updates)
            else:
                return False, "System admins can only update service engineers or themselves."
        else:
            return False, "Only super admins and system admins can update users."

    #--------------------------------------------------------------------------------------
    #                   Delete User
    #--------------------------------------------------------------------------------------
    @staticmethod
    @require_role("system_admin", "super")
    def delete_user(current_user_id, user_id, username):
        """
        Delete a user from the system.
        Only super admins can delete users
        System admins can only delete service engineers or themselves
        """        
        current_role = UserSession.get_current_role()
        if current_role == "super":
            return user_service.delete_user(user_id, username)
        elif current_role == "system_admin":
            target_user = user_service.get_user_by_id(user_id)
            if not target_user:
                return False, "User not found."
            if target_user["role"] == "service_engineer" or user_id == current_user_id:
                return user_service.delete_user(user_id, username)
            else:
                return False, "System admins can only delete service engineers or themselves."
        else:
            return False, "Only super admins and system admins can delete users"
    
    #--------------------------------------------------------------------------------------
    #                   List Users
    #--------------------------------------------------------------------------------------
    @staticmethod
    @require_role("system_admin", "super")
    def list_users(user_id):
        """List all users in the system."""
        return user_service.list_users()
    
    #--------------------------------------------------------------------------------------
    #                   Change Password
    #--------------------------------------------------------------------------------------
    @staticmethod
    def change_password_controller(current_user_id, current_password, new_password):
        """
        Change the password for a user.
        Users can only change their own password.
        Super admins can change their own password.
        """
        # Verify current password
        if not user_service.verify_user_password(current_user_id, current_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        valid, message = user_service.validate_password(new_password)
        if not valid:
            return False, message
        
        # Update password
        user_service.update_password(current_user_id, new_password)
        return True, "Password changed successfully"




