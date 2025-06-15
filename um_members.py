# um_members.py
from dbcontext.dbcontext import create_db
from services.userservice import user_service #, add_scooter
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from dashboard.menu_config import get_menu
import os

def main():
    print("Urban Mobility System Starting...")
    create_db()
    
    # Only add user if username does not exist
    if not user_service.get_user_by_username("mike_admin"):
        UserController.add_user("mike_admin", "StrongPass123!", "Mike", "Jansen", "system_admin")
    if not user_service.get_user_by_username("john_eng"):
        UserController.add_user("john_eng", "Password123!", "John", "Doe", "service_engineer")

    # add_scooter("UrbanScoot", "ModelX", "SN123456789", 25.0, 500.0, 80.0, 20.0, 90.0, 52.5200, 13.4050, 100.0, False, None, None)

    while not UserSession.is_authenticated():
        username = input("Username: ")
        password = input("Password: ")
        UserSession.login(username, password)

    while True:
        os.system("cls")
        print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
        menu_items = get_menu(UserSession)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
        print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu)
        if choice is None:
            continue
        label, action = visible_menu[choice]
        action()

if __name__ == "__main__":
    main()
