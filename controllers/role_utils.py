from functools import wraps
from dbcontext.dbcontext import get_user_by_id

# Define role hierarchy
ROLE_HIERARCHY = {
    "service_engineer": 1,
    "system_admin": 2,
    "super_admin": 3
}

def require_role(required_role):
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
    user = get_user_by_id(user_id)
    if not user:
        return False
    user_role = user["role"]
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
