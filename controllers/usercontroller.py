# namespace: controllers

from models.user import User
from services.userservice import UserService
from utils.role_utils import require_role
from utils.validation_utils import validate_password

class UserController:
    _user_service = UserService("urban_mobility.db")

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
        user = UserController._user_service.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        # Check old password
        if not UserController._user_service.verify_user_password(user_id, old_password):
            return False, "Old password is incorrect."
        # Validate new password
        valid, msg = validate_password(new_password)
        if not valid:
            return False, msg
        # Update password
        UserController._user_service.update_password(user_id, new_password)
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
            UserController._user_service.add_user(user)
            return True, "User added successfully."
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def add_user(username, password, first_name, last_name, role):
        return UserController._user_service.add_user_from_params(username, password, first_name, last_name, role)




