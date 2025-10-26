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
            
            # Special case for super admin (user_id 0)
            if user_id == 0:
                return func(user_id, *args, **kwargs)
            
            # Import user_service here to avoid circular imports
            from services.userservice import user_service
            user = user_service.get_user_by_id(user_id)
            if not user:
                return False, "User not found."
            
            user_role = user.role_plain
            # Exact match: only listed roles can access
            if user_role in required_roles:
                return func(user_id, *args, **kwargs)
            else:
                return False, f"Permission denied: {user_role} cannot perform this action (requires one of: {', '.join(required_roles)})."
        return wrapper
    return decorator
