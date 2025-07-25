from functools import wraps
from models.user import User

# Role hierarchy defines the permission levels for different roles
# Higher numbers indicate higher permission levels
ROLE_HIERARCHY = {
    "service_engineer": 1,  # Basic access level
    "system_admin": 2,      # Administrative access
    "super": 3        # Full system access
}

def require_role(*required_roles):
    """
    Decorator that checks if a user has any of the required role permissions before executing a function.
    
    Args:
        *required_roles (str): One or more role levels required to execute the decorated function
        
    Returns:
        function: Decorated function that includes role permission checking
        
    Example:
        @require_role("system_admin", "service_engineer")
        def admin_or_engineer_function(user_id):
            # Only users with system_admin or service_engineer role can execute this
            pass
    """
    def decorator(func):
        func._required_roles = required_roles  # Attach roles for introspection
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            # print(f"[DEBUG] require_role wrapper called with user_id={user_id}, required_roles={required_roles}")
            
            # Special case for super admin (user_id 0)
            if user_id == 0:
                # print(f"[DEBUG] Super admin detected (user_id=0), bypassing role check")
                return func(user_id, *args, **kwargs)
            
            # Import user_service here to avoid circular imports
            from services.userservice import user_service
            user = user_service.get_user_by_id(user_id)
            # print(f"[DEBUG] User from database: {user}")
            if not user:
                return False, "User not found."
            
            user_role = user.role_plain
            # print(f"[DEBUG] User role: {user_role}, required_roles: {required_roles}")
            # Exact match: only listed roles can access
            if user_role in required_roles:
                # print(f"[DEBUG] Role check passed")
                return func(user_id, *args, **kwargs)
            else:
                # print(f"[DEBUG] Role check failed")
                return False, f"Permission denied: {user_role} cannot perform this action (requires one of: {', '.join(required_roles)})."
        return wrapper
    return decorator

def has_permission(user_id, required_role):
    """
    Checks if a user has sufficient permissions for a given role level (exact match).
    
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
    if user_id == 0:
        user = User(
            username="super_admin",
            password_plain="Admin_123?",
            role="super"
        )
    else:
        # Import user_service here to avoid circular imports
        from services.userservice import user_service
        user = user_service.get_user_by_id(user_id)
    
    if not user:
        return False
    user_role = user.role_plain
    return user_role == required_role
