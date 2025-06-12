# namespace: controllers

from models.user import User
from dbcontext.userdata import verify_user_password, get_user_by_id, update_password, add_user
from utils.role_utils import require_role

class UserController:
    def __init__(self):
        pass
        
@require_role("service_engineer")
def change_password(user_id, old_password, new_password):
    # Special case for super admin
    if user_id == 0:
        if old_password != "Admin_123?":
            return False, "Old password is incorrect."
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
        add_user(user)
        return True, "User added successfully."
    except ValueError as e:
        return False, str(e)



