# um_members.py
from dbcontext.dbcontext import create_db
from dbcontext.dbcontext import add_user
from controllers.usercontroller import change_password
from controllers.session import UserSession
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from dashboard.menu_config import get_menu
from dashboard.actions import change_password_flow
from services.userdata import get_user_by_username

import os

def main():
    print("Urban Mobility System Starting...")
    create_db()
    # Only add user if username does not exist
    if not get_user_by_username("mike_admin"):
        add_user("mike_admin", "StrongPass123!", "Mike", "Jansen", "system_admin")
    if not get_user_by_username("john_eng"):
        add_user("john_eng", "Password123!", "John", "Doe", "service_engineer")

    session = UserSession()
    while not session.is_authenticated():
        username = input("Username: ")
        password = input("Password: ")
        session.login(username, password)

    while True:
        os.system("cls")
        print(f"\nWelcome, {session.username} ({session.role})")
        menu_items = get_menu(session)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, session.role)
        print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu)
        if choice is None:
            continue
        label, action = visible_menu[choice]
        action()

if __name__ == "__main__":
    main()
