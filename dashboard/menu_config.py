from controllers.usercontroller import change_password
from controllers.session import UserSession
from dashboard.actions import change_password_flow

def get_menu(session):
    return [
        ("Change password", ("service_engineer", "system_admin"), change_password, lambda: change_password_flow(session)),
        ("Logout", None, None, session.logout)
    ] 