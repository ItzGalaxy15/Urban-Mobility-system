import os
from controllers.session import UserSession
from controllers.usercontroller import UserController
from controllers.scootercontroller import ScooterController
from dashboard.actions import change_password_flow
from dashboard.actions import add_scooter_flow, update_scooter_flow, view_scooters_flow, search_scooters_flow, delete_scooter_flow
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu

# Main Menu #
def get_menu(session):
    return [
        ("Scooter Management", ("service_engineer", "system_admin", "super"), None, lambda: scooter_menu(session)),
        ("Change password", ("service_engineer", "system_admin"), UserController.change_password, lambda: change_password_flow(session)),
        ("Logout", None, None, session.logout)
    ]

# Scooter Management Menu #
def get_menu_scooter_management(session):
    return [
        ("Add Scooter", ("service_engineer", "system_admin", "super"), None, lambda: add_scooter_flow(session)),
        ("Update Scooter", ("service_engineer", "system_admin", "super"), None, lambda: update_scooter_flow(session)),
        ("View Scooters", ("service_engineer", "system_admin", "super"), None, lambda: view_scooters_flow(session)),
        ("Search Scooters", ("service_engineer", "system_admin", "super"), None, lambda: search_scooters_flow(session)),
        ("Delete Scooter", ("super", "system_admin"), None, lambda: delete_scooter_flow(session)),
        ("Back to Main Menu", None, None, lambda: None)
    ]

def scooter_menu(session):
    while True:
        os.system("cls")
        print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
        menu_items = get_menu_scooter_management(session)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
        # print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu, title="Scooter Management Menu")
        if choice is None:
            continue
        label, action = visible_menu[choice]

        if label == "Back to Main Menu":
            return
        action()
