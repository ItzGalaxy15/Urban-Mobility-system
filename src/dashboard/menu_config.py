import os
from controllers.session import UserSession
from controllers.usercontroller import UserController
from controllers.backupcontroller import BackupController
from dashboard.menus.backup_db_menu import backup_db_flow
from dashboard.menus.backup_management_menu import (
    request_backup_restore_flow,
    generate_restore_code_flow,
    restore_with_code_flow,
    restore_direct_flow,
    view_my_codes_flow
)
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from dashboard.menus.logmenu import view_logs_flow


# Import menu flows from their respective files
from dashboard.menus.usermenu import (
    add_user_flow,
    update_user_flow,
    delete_user_flow,
    list_users_flow,
    change_password_flow,
    edit_account_flow
)

from dashboard.menus.scootermenu import (
    add_scooter_flow,
    update_scooter_flow,
    view_scooters_flow,
    search_scooters_flow,
    delete_scooter_flow
)

from dashboard.menus.travellermenu import (
    add_traveller_flow,
    update_traveller_flow,
    delete_traveller_flow,
    search_traveller_flow
)

from dashboard.menus.password_reset_menu import (
    reset_password_flow,
    use_reset_code_flow
)


#--------------------------------------------------------------------------------------
#                                Main Menu Management
#--------------------------------------------------------------------------------------

def get_menu(session):
    return [
        ("Manage scooters", ("service_engineer", "system_admin", "super"),
         None, lambda: scooter_menu(session)),

        ("Manage users", ("system_admin", "super"),
         None, lambda: user_menu(session)),

        ("Manage travellers", ("system_admin", "super"),
         None, lambda: traveller_menu(session)),

        ("Change password", ("service_engineer", "system_admin"),
         UserController.change_password, lambda: change_password_flow(session)),

        ("Edit profile/account", ("system_admin"), None, lambda: edit_account_flow(session)),
        
        ("Manage backups", ("system_admin", "super"), None, lambda: backup_menu(session)),

        ("View system logs", ("system_admin", "super"), None, lambda: view_logs_flow(session)),

        ("Logout", None, None, session.logout),

        ("Exit", None, None, lambda: -1)
    ]

#--------------------------------------------------------------------------------------
#                           The End of Main Menu Management
#--------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------
#                                Traveller Management
#--------------------------------------------------------------------------------------

def get_menu_traveller_management(session):
    return [
        ("Add Traveller", ("system_admin", "super"),
         None, lambda: add_traveller_flow(session)),

        ("Update Traveller", ("system_admin", "super"),
         None, lambda: update_traveller_flow(session)),

        ("Delete Traveller", ("system_admin", "super"),
         None, lambda: delete_traveller_flow(session)),

        ("Search Travellers", ("system_admin", "super"),
         None, lambda: search_traveller_flow(session)),

        ("Back", None, None, lambda: None)
    ]

# -----------------------------------------------------------

def traveller_menu(session):
    while True:
        os.system("cls")
        print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
        menu_items = get_menu_traveller_management(session)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
        # print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu, title="Traveller Management Menu")
        if choice is None:
            continue
        label, action = visible_menu[choice]

        if label == "Back":
            return
        action()

#--------------------------------------------------------------------------------------
#                           The End of Traveller Management
#--------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------
#                                User Management
#--------------------------------------------------------------------------------------

def get_menu_user_management(session):
    return [
        ("Add User", ("system_admin", "super"),
         None, lambda: add_user_flow(session)),

        ("Update User", ("system_admin", "super"),
         None, lambda: update_user_flow(session)),

        ("Delete User", ("system_admin", "super"),
         None, lambda: delete_user_flow(session)),

        ("List Users", ("system_admin", "super"),
         None, lambda: list_users_flow(session)),

        ("Reset User Password", ("system_admin", "super"),
         None, lambda: reset_password_flow(session)),

        ("Back", None, None, lambda: None)
    ]

# -----------------------------------------------------------

def user_menu(session):
    while True:
        os.system("cls")
        print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
        menu_items = get_menu_user_management(session)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
        # print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu, title="Scooter Management Menu")
        if choice is None:
            continue
        label, action = visible_menu[choice]

        if label == "Back":
            return
        action()

#--------------------------------------------------------------------------------------
#                           The End of User Management
#--------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------
#                                Scooter Management
#--------------------------------------------------------------------------------------

def get_menu_scooter_management(session):
    return [
        ("Add Scooter", ("system_admin", "super"),
         None, lambda: add_scooter_flow(session)),

        ("Update Scooter", ("system_admin", "super"),
         None, lambda: update_scooter_flow(session)),

        ("View Scooters", ("service_engineer", "system_admin", "super"),
         None, lambda: view_scooters_flow(session)),

        ("Search Scooters", ("service_engineer", "system_admin", "super"),
         None, lambda: search_scooters_flow(session)),

        ("Delete Scooter", ("system_admin", "super"),
         None, lambda: delete_scooter_flow(session)),

        ("Back", None, None, lambda: None)
    ]

# -----------------------------------------------------------

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

        if label == "Back":
            return
        action()

#--------------------------------------------------------------------------------------
#                           The End of Scooter Management
#--------------------------------------------------------------------------------------

def get_menu_backup_management(session):
    return [
        ("Create Database Backup", ("system_admin", "super"), None, lambda: backup_db_flow(session)),

        ("Request Backup Restore", ("system_admin"), None, lambda: request_backup_restore_flow(session)),

        ("Generate Restore Code", ("super"), None, lambda: generate_restore_code_flow(session)),
        
        ("Restore Backup with Code", ("system_admin"), None, lambda: restore_with_code_flow(session)),
        
        ("Direct Backup Restore", ("super"), None, lambda: restore_direct_flow(session)),
        
        ("View My Restore Codes", ("system_admin"), None, lambda: view_my_codes_flow(session)),

        ("Back", None, None, lambda: None)
    ]

def backup_menu(session):
    while True:
        os.system("cls")
        print(f"\nWelcome, {UserSession.get_current_username()} ({UserSession.get_current_role()})")
        menu_items = get_menu_backup_management(session)
        visible_menu = build_menu_with_roles_and_permissions(menu_items, UserSession.get_current_role())
        # print("Visible menu:", visible_menu)
        choice = display_menu(visible_menu, title="Backup Management Menu")
        if choice is None:
            continue
        label, action = visible_menu[choice]
        
        if label == "Back":
            return
        action()
