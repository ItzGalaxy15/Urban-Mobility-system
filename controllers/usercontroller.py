# namespace: controllers

from models.user import User
from services.userservice import user_service
from utils.role_utils import require_role
from utils.validation_utils import validate_password

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
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        # Check old password
        if not verify_user_password(user_id, old_password):
            return False, "Old password is incorrect."
        # Update password
        update_password(user_id, new_password)
        return True, "Password updated successfully."

    @staticmethod
    @require_role("system_admin")
    def add_sys_eng_user_controller(user_id, username, password, first_name, last_name, role):
        # Only system_admin and super_admin can add users
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




