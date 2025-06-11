# namespace: controllers

from models.user import User
from dbcontext.dbcontext import verify_user_password, get_user_by_id
from dbcontext.userdata import update_password
from controllers.role_utils import require_role

class UserController:
    def __init__(self):
        pass
        

def change_password(user_id, old_password, new_password):
    # Check if user exists
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
def add_user_controller(user_id, username, password, first_name, last_name, role):
    # Only system_admin and super_admin can add users
    from dbcontext.dbcontext import add_user
    add_user(username, password, first_name, last_name, role)
    print("User added successfully.")
        