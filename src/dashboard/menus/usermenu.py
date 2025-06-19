from controllers.usercontroller import UserController
from controllers.session import UserSession
from services.userservice import user_service

def add_user_flow(session):
    while True:
        # Username validation
        while True:
            username = input("Enter the username (8-10 chars, starts with letter/underscore): ")
            # First validate format
            valid, message = user_service.validate_username(username)
            if not valid:
                print(message)
                continue
            
            # Then check if username exists
            if user_service.get_user_by_username(username):
                print("Username already exists. Please choose a different one.")
                continue
            break

        # Password validation
        while True:
            password = input("Enter the password (12-30 chars, must include lowercase, uppercase, digit, and special char): ")
            valid, message = user_service.validate_password(password)
            if not valid:
                print(message)
                continue
            break

        # First name validation
        while True:
            first_name = input("Enter the first name: ")
            valid, message = user_service.validate_name(first_name, "First name")
            if not valid:
                print(message)
                continue
            break

        # Last name validation
        while True:
            last_name = input("Enter the last name: ")
            valid, message = user_service.validate_name(last_name, "Last name")
            if not valid:
                print(message)
                continue
            break
        
        # Get current user's role
        current_role = UserSession.get_current_role()
        current_user_id = UserSession.get_current_user_id()
        
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
        
        success, message = UserController.add_user(
            current_user_id, 
            username, 
            password, 
            first_name, 
            last_name, 
            role
        )
        print(message)
        input("Press enter to continue...")
        if success:
            break

def update_user_flow(session):
    while True:
        print("\n--- Update User ---")
        print("Enter 'back' or 'exit' to go back to user management")
        print("Enter the user id or username to update: ")
        update_user = input("Enter the user id or username: ")
        if update_user == "":
            print("Invalid input")
            continue
        elif update_user == "back" or update_user == "exit":
            break
        # Try username first, then user ID
        user = user_service.get_user_by_username(update_user)
        if not user and update_user.isdigit():
            user = user_service.get_user_by_id(int(update_user))
        if not user:
            print("User not found")
            continue
        while True:
            print(f"\n--- Updating User: {user.user_id} | {user.username_plain} | {user.role_plain} ---")
            print("1. Update username (8-10 chars, starts with letter/underscore)")
            print("2. Update first name (2-20 chars)")
            print("3. Update last name (2-20 chars)")
            print("4. Back")
            choice = input("Choose an option: ").strip()
            updates = {}
            if choice == "1":
                username = input("Enter the new username: ")
                valid, message = user_service.validate_username(username)
                if not valid:
                    print(message)
                    break
                updates["username"] = username
            elif choice == "2":
                first_name = input("Enter the new first name: ")
                valid, message = user_service.validate_name(first_name, "First name")
                if not valid:
                    print(message)
                    break
                updates["first_name"] = first_name
            elif choice == "3":
                last_name = input("Enter the new last name: ")
                valid, message = user_service.validate_name(last_name, "Last name")
                if not valid:
                    print(message)
                    break
                updates["last_name"] = last_name
            elif choice == "4":
                break
            else:
                print("Invalid choice")
                continue
            if updates:
                current_user_id = UserSession.get_current_user_id()
                success, message = UserController.update_user(
                    current_user_id,
                    user.user_id,
                    **updates
                )
                print(message)
                input("Press Enter to continue...")
                if success:
                    break

def delete_user_flow(session):
    while True:
        print("\n--- Delete User ---")
        print("Enter 'back' or 'exit' to go back to user management")
        print("Enter the user id or username to delete: ")
        delete_user = input("Enter the user id or username: ")
        if delete_user == "":
            print("Invalid input")
            continue
        elif delete_user == "back" or delete_user == "exit":
            break
        # Try username first, then user ID
        user = user_service.get_user_by_username(delete_user)
        if not user and delete_user.isdigit():
            user = user_service.get_user_by_id(int(delete_user))
        if not user:
            print("User not found")
            continue
        user_id = user.user_id
        current_user_id = UserSession.get_current_user_id()
        success, message = UserController.delete_user(
            current_user_id, user_id, user.username
        )
        print(message)
        if success:
            # If the deleted user is the currently logged-in user, log out immediately
            if user_id == UserSession.get_current_user_id():
                print("You have deleted your own account. Logging out...")
                input("\nPress Enter to continue...")
                session.logout()
            break

def list_users_flow(session):
    current_user_id = UserSession.get_current_user_id()
    users = UserController.list_users(current_user_id)
    print("\n--- User List ---")
    print("ID | Username | First Name | Last Name | Role")
    print("-" * 50)
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"{user.user_id} | {user.username_plain} | {user.first_name} | {user.last_name} | {user.role_plain}")
    input("\nPress Enter to continue...")

def change_password_flow(session):
    while True:
        current_user_id = UserSession.get_current_user_id()
        old_pw = input("Enter your old password: ")
        new_pw = input("Enter your new password (or leave blank to cancel): ")
        if not new_pw:
            print("Password change cancelled.")
            break
        success, message = UserController.change_password(current_user_id, old_pw, new_pw)
        print(message)
        if success:
            break
    input("Press Enter to continue...")

def edit_account_flow(session):
    while True:
        current_user_id = UserSession.get_current_user_id()
        user = user_service.get_user_by_id(current_user_id)
        if not user:
            print("User not found.")
            input("\nPress Enter to continue...")
            return
        
        
        # Get user's role
        role = UserSession.get_current_role()
        
        # Display profile based on role
        if role in ["service_engineer", "system_admin"]:
            print(f"\n--- Profile Information ---")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Registration Date: {user.registration_date}")
            print("\n1. Change first name")
            print("2. Change last name")
            print("3. Back/Exit to main menu")
        else:
            print(f"\n--- Edit Profile/Account: {user.user_id} | {user.username} ---")
            print("1. Change username")
            print("2. Change first name")
            print("3. Change last name")
            print("4. Back/Exit to main menu")
        
        choice = input("Choose an option: ").strip()
        updates = {}
        
        if role in ["service_engineer", "system_admin"]:
            if choice == "1":
                first_name = input("Enter the new first name: ")
                valid, message = user_service.validate_name(first_name, "First name")
                if not valid:
                    print(message)
                    continue
                updates["first_name"] = first_name
            elif choice == "2":
                last_name = input("Enter the new last name: ")
                valid, message = user_service.validate_name(last_name, "Last name")
                if not valid:
                    print(message)
                    continue
                updates["last_name"] = last_name
            elif choice == "3":
                break
            else:
                print("Invalid choice")
                continue
        else:
            if choice == "1":
                username = input("Enter the new username: ")
                valid, message = user_service.validate_username(username)
                if not valid:
                    print(message)
                    continue
                updates["username"] = username
            elif choice == "2":
                first_name = input("Enter the new first name: ")
                valid, message = user_service.validate_name(first_name, "First name")
                if not valid:
                    print(message)
                    continue
                updates["first_name"] = first_name
            elif choice == "3":
                last_name = input("Enter the new last name: ")
                valid, message = user_service.validate_name(last_name, "Last name")
                if not valid:
                    print(message)
                    continue
                updates["last_name"] = last_name
            elif choice == "4":
                break
            else:
                print("Invalid choice")
                continue
        
        if updates:
            success, message = UserController.update_user(
                current_user_id,
                current_user_id,
                **updates
            )
            print(message)
            input("\nPress Enter to continue...")
            if success:
                # Optionally refresh session info if username was changed
                if "username" in updates:
                    UserSession._current_username = updates["username"]
                if "first_name" in updates:
                    UserSession._current_user.first_name = updates["first_name"]
                if "last_name" in updates:
                    UserSession._current_user.last_name = updates["last_name"]
