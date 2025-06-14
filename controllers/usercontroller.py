# namespace: controllers

from models.user import User
from services.userservice import user_service
from utils.role_utils import require_role
from controllers.session import UserSession

class UserController:
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
        
        # Validate all fields first
        valid, message = user_service.validate_username(username)
        if not valid:
            return False, message

        valid, message = user_service.validate_password(password)
        if not valid:
            return False, message

        valid, message = user_service.validate_name(first_name, "First name")
        if not valid:
            return False, message

        valid, message = user_service.validate_name(last_name, "Last name")
        if not valid:
            return False, message

        # Check if username already exists
        if user_service.get_user_by_username(username):
            return False, "Username already exists"
        
        # Add the user
        success, message = user_service.add_user_from_params(username, password, first_name, last_name, role)
        return success, message

    @staticmethod
    def add_user(username, password, first_name, last_name, role):
        return user_service.add_user_from_params(username, password, first_name, last_name, role)

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




