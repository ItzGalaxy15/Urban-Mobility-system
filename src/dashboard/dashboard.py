import sys
from utils.role_utils import ROLE_HIERARCHY

def user_can_access(user_role, func):
    """
    Checks if a user with the given role can access the function based on its required roles.
    """
    required_roles = getattr(func, '_required_roles', None)
    # print(f"Checking access: user_role={user_role}, required_roles={required_roles}, func={func.__name__}")
    if not required_roles:
        return True  # No restriction
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    return any(user_level >= ROLE_HIERARCHY.get(role, 0) for role in required_roles)

def build_menu(menu_items, user_role):
    """
    Filters menu items based on user role permissions.
    menu_items: list of (label, function) tuples
    user_role: str
    Returns: list of (label, function) tuples visible to the user
    """
    return [item for item in menu_items if user_can_access(user_role, item[1])]

def display_menu(menu_items, title="Main Menu") -> int | None:
    """
    Displays the menu and returns the user's choice (1-based index).
    menu_items: list of (label, function) tuples
    Returns: index of selected item (or None if invalid)
    """
    print(f"\n-----=== {title} ===-----")
    for idx, (label, _) in enumerate(menu_items, 1):
        if label == "Logout" or label == "Back":
            print()
        print(f"{idx}. {label}")
    print("------------------" + "-" * len(title))
    try:
        option = int(input("\nChoose an option: "))
        print(option)
        if 1 <= option <= len(menu_items):
            return option - 1
    except Exception:
        pass
    
    print("Invalid option.")
    return None

def build_menu_with_roles_and_permissions(menu_items, user_role):
    """
    Filters menu items based on both menu visibility (required_roles) and permission_func.
    menu_items: list of (label, required_roles, permission_func, action_func) tuples
    user_role: str
    Returns: list of (label, action_func) tuples visible to the user
    """
    visible = []
    for (label, required_roles, perm_func, action_func) in menu_items:
        # Menu visibility check
        if required_roles is not None and user_role not in required_roles:
            continue
        # Permission check (if provided)
        if perm_func is not None and not user_can_access(user_role, perm_func):
            continue
        visible.append((label, action_func))
    return visible
