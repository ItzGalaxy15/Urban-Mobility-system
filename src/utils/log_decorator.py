from functools import wraps
from services.log_service import write_log_entry
from models.log_entry import LogEntry
from services.session_service import session_service

def log_action(description: str):
    """
    Decorator to log the result of a menu-level action (add, update, delete, …).

    The wrapped function may:
      • return (success: bool, message: str)           → normal path
      • return anything else (e.g. list of users)     → we log as success, msg="OK"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Normalise return value
            if not (isinstance(result, tuple) and len(result) == 2
                    and isinstance(result[0], bool)):
                success, message = True, ""
            else:
                success, message = result

            user_id  = session_service.get_current_user_id() or "-"
            username = session_service.get_current_username() or "-"

            write_log_entry(LogEntry(
                user_id=str(user_id),
                username=username,
                description=description.format(msg=message),
                additional="",
                suspicious= False
            ))
            return result  # preserve original return value (tuple or other)
        return wrapper
    return decorator
