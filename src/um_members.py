# um_members.py
from dbcontext.dbcontext import create_db
from services.userservice import user_service
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from dashboard.menu_config import get_menu
from dashboard.menus.password_reset_menu import use_reset_code_flow
import os
import sys

def main():
    print("Urban Mobility System Starting...")
    create_db()
    
    while True:
        # Login loop
        while not UserSession.is_authenticated():
            print("Type exit to exit the system")
            username = input("Username: ")
            if username.lower() == 'exit':
                print("Exiting system...")
                sys.exit(0)
            if username == "super_admin":
                password = input("Password: ")
                if password.lower() == 'exit':
                    print("Exiting system...")
                    sys.exit(0)
                if UserSession.login(username, password):
                    break
            else:
                if UserSession.login(username):
                    break
            # If login fails, loop again
            continue

        # Main menu loop
        try:
            while True:
                os.system("cls")
                print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
                menu_items = get_menu(UserSession)
                visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
                choice = display_menu(visible_menu)
                if choice is None:
                    continue
                label, action = visible_menu[choice]
                is_exiting = action()
                if is_exiting:
                    raise SystemExit("Exiting application...")
        except SystemError: # Logout return
            continue  # Return to login loop
        except SystemExit: # Exiting return
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
