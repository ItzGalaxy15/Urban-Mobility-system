from controllers.traveller_controller import TravellerController
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.actions import change_password_flow, add_user_flow
from dashboard.actions import add_traveller_flow, update_traveller_flow, delete_traveller_flow, search_traveller_flow, manage_traveller_flow

def get_menu(session):
    return [
        ("Change password", ("service_engineer", "system_admin"),
         UserController.change_password, lambda: change_password_flow(session)),

        ("Add user", ("system_admin", "super"),
         UserController.add_user_controller, lambda: add_user_flow(session)),

        ("Manage travellers", ("system_admin", "super"),
        None, lambda: manage_traveller_flow(session)),

        ("Logout", None, None, session.logout)
    ]