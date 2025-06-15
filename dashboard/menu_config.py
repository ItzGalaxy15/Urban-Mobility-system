from controllers.traveller_controller import TravellerController
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.actions import change_password_flow, manage_user_flow
from dashboard.actions import add_traveller_flow, update_traveller_flow, delete_traveller_flow, search_traveller_flow, manage_traveller_flow
from dashboard.actions import edit_account_flow

def get_menu(session):
    return [
        ("Change password", ("service_engineer", "system_admin"),
         UserController.change_password, lambda: change_password_flow(session)),

        ("Manage users", ("system_admin", "super"),
         None, lambda: manage_user_flow(session)),

        ("Manage travellers", ("system_admin", "super"),
        None, lambda: manage_traveller_flow(session)),

        ("Edit profile/account", ("system_admin"), None, lambda: edit_account_flow(session)),

        ("Logout", None, None, session.logout)
    ]