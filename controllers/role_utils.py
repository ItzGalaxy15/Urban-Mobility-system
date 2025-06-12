from functools import wraps
from dbcontext.userdata import get_user_by_id

# Role hierarchy defines the permission levels for different roles
# Higher numbers indicate higher permission levels
ROLE_HIERARCHY = {
    "service_engineer": 1,  # Basic access level
    "system_admin": 2,      # Administrative access
    "super_admin": 3        # Full system access
}

def require_role(required_role):
    """
    Decorator that checks if a user has sufficient role permissions before executing a function.
    
    Args:
        required_role (str): The minimum role level required to execute the decorated function
        
    Returns:
        function: Decorated function that includes role permission checking
        
    Example:
        @require_role("system_admin")
        def admin_only_function(user_id):
            # Only users with system_admin role or higher can execute this
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            user = get_user_by_id(user_id)
            if not user:
                print("User not found.")
                return None
            user_role = user["role"]
            if ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0):
                return func(user_id, *args, **kwargs)
            else:
                print(f"Permission denied: {user_role} cannot perform this action (requires {required_role}).")
                return None
        return wrapper
    return decorator

def has_permission(user_id, required_role):
    """
    Checks if a user has sufficient permissions for a given role level.
    
    Args:
        user_id: The ID of the user to check permissions for
        required_role (str): The role level to check against
        
    Returns:
        bool: True if user has sufficient permissions, False otherwise
        
    Example:
        if has_permission(user_id, "system_admin"):
            # Perform admin-only operation
            pass
    """
    user = get_user_by_id(user_id)
    if not user:
        return False
    user_role = user["role"]
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
