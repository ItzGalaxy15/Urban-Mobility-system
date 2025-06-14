# namespace: controllers

from models.user import User
from services.userservice import user_service
from utils.role_utils import require_role
from validation.validation_utils import validate_password, validate_user_inputs

class UserController:
    @staticmethod
    @require_role("service_engineer", "system_admin")
    def change_password(user_id, old_password, new_password):
        # Special case for super admin
        if user_id == 0:
            if old_password != "Admin_123?":
                return False, "Old password is incorrect."
            # Validate new password for super admin as well
            valid, msg = validate_password(new_password)
            if not valid:
                return False, msg
            # For super admin, we don't actually change the password since it's hardcoded
            return True, "Password updated successfully."

        # Regular user password change
        user = user_service.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        # Check old password
        if not user_service.verify_user_password(user_id, old_password):
            return False, "Old password is incorrect."
        # Validate new password
        valid, msg = validate_password(new_password)
        if not valid:
            return False, msg
        # Update password
        user_service.update_password(user_id, new_password)
        return True, "Password updated successfully."

    @staticmethod
    @require_role("system_admin", "super")
    def add_user_controller(user_id, username, password, first_name, last_name, role):
        # Special case for super admin (user_id 0)
        if user_id == 0:
            current_role = "super"
        else:
            # Get the current user's role for regular users
            current_user = user_service.get_user_by_id(user_id)
            if not current_user:
                return False, "Current user not found."
            current_role = current_user["role"]
        
        # Check role restrictions
        if current_role == "system_admin" and role != "service_engineer":
            return False, "System admin can only add service engineers."
        elif current_role == "super" and role not in ["service_engineer", "system_admin"]:
            return False, "Super admin can only add service engineers or system admins."
        
        # Validate all inputs
        valid, message = validate_user_inputs(username, password, first_name, last_name, role)
        if not valid:
            return False, message
        
        try:
            user = User(
                username=username,
                password_plain=password,
                role=role,
                first_name=first_name,
                last_name=last_name
            )
            user_service.add_user(user)
            return True, "User added successfully."
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def add_user(username, password, first_name, last_name, role):
        return user_service.add_user_from_params(username, password, first_name, last_name, role)




