from controllers.usercontroller import UserController
from controllers.session import UserSession
from models.user import User, USERNAME_RE, PWD_ALLOWED_RE
import re
from validation.validation_utils import validate_username, validate_password, validate_name

def change_password_flow(session):
    while True:
        old_pw = input("Enter your old password: ")
        new_pw = input("Enter your new password (or leave blank to cancel): ")
        if not new_pw:
            print("Password change cancelled.")
            break
        success, message = UserController.change_password(UserSession.get_current_user_id(), old_pw, new_pw)
        print(message)
        if success:
            break 
        
def add_user_flow(session):
    while True:
        # Username validation
        while True:
            username = input("Enter the username (8-10 chars, starts with letter/underscore): ")
            valid, message = validate_username(username)
            if not valid:
                print(message)
                continue
            break

        # Password validation
        while True:
            password = input("Enter the password (12-30 chars, must include lowercase, uppercase, digit, and special char): ")
            valid, message = validate_password(password)
            if not valid:
                print(message)
                continue
            break

        # First name validation
        while True:
            first_name = input("Enter the first name: ")
            valid, message = validate_name(first_name, "First name")
            if not valid:
                print(message)
                continue
            break

        # Last name validation
        while True:
            last_name = input("Enter the last name: ")
            valid, message = validate_name(last_name, "Last name")
            if not valid:
                print(message)
                continue
            break
        
        # Get current user's role
        current_role = UserSession.get_current_role()
        
        # Show appropriate role options based on current user's role
        if current_role == "system_admin":
            print("Role: Service Engineer")
            role = "service_engineer"
        else:  # super admin
            print("Choose the role: ")
            print("1. Service Engineer")
            print("2. System Admin")
            role_choice = input("Enter the role (1 or 2): ")
            if role_choice == "1":
                role = "service_engineer"
            elif role_choice == "2":
                role = "system_admin"
            else:
                print("Invalid role choice. Please try again.")
                continue
        
        success, message = UserController.add_user_controller(
            UserSession.get_current_user_id(), 
            username, 
            password, 
            first_name, 
            last_name, 
            role
        )
        print(message)
        if success:
            break