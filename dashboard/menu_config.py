from controllers.traveller_controller import TravellerController
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.actions import change_password_flow, add_user_flow
from dashboard.actions import add_traveller_flow, update_traveller_flow, delete_traveller_flow, search_traveller_flow

def get_menu(session):
    return [
        ("Change password", ("service_engineer", "system_admin"),
         UserController.change_password, lambda: change_password_flow(session)),

        ("Add user", ("system_admin", "super"),
         UserController.add_user_controller, lambda: add_user_flow(session)),

        ("Add traveller",   ("system_admin", "super"),
         TravellerController.add_traveller_controller,
         lambda: add_traveller_flow(session)),

        ("Update traveller", ("system_admin", "super"),
         TravellerController.update_traveller_controller,
         lambda: update_traveller_flow(session)),

        ("Delete traveller", ("system_admin", "super"),
         TravellerController.delete_traveller_controller,
         lambda: delete_traveller_flow(session)),

        ("Search travellers", ("system_admin", "super"),
         TravellerController.search_travellers_controller,
         lambda: search_traveller_flow(session)),

        ("Logout", None, None, session.logout)
    ]