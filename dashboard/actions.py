from controllers.traveller_controller import TravellerController
from services.traveller_service import traveller_service
from models.traveller import (
    Traveller,
    CITY_CHOICES,
    ZIP_RE,
    PHONE_RE,
    LICENSE_RE,
    BIRTH_RE,
    EMAIL_RE,
    HOUSE_RE,
)
from controllers.usercontroller import UserController
from controllers.session import UserSession
from services.userservice import user_service

#--------------------------------------------------------------------------------------
#                                  User Management
#--------------------------------------------------------------------------------------

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
        
def manage_user_flow(session):
    while True:
        print("\n--- Manage Users ---")
        print("1. Add user")
        print("2. Update user")
        print("3. Delete user")
        print("4. List users")
        print("5. Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_user_flow(session)
        elif choice == "2":
            update_user_flow(session)
        elif choice == "3":
            delete_user_flow(session)
        elif choice == "4":
            list_users_flow(session)
        elif choice == "5":
            break
        else:
            print("Invalid choice")

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
            print(f"\n--- Updating User: {user['user_id']} | {user['username']} | {user['role']} ---")
            print("1. Update username (8-10 chars, starts with letter/underscore)")
            print("2. Update first name (2-20 chars)")
            print("3. Update last name (2-20 chars)")
            # print("4. Update role (service_engineer/system_admin)")
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
            # elif choice == "4":
            #     role = input("Enter the new role: ")
            #     valid, message = user_service.validate_role(role)
            #     if not valid:
            #         print(message)
            #         break
            #     updates["role"] = role
            elif choice == "4":
                break
            else:
                print("Invalid choice")
                continue
            if updates:
                success, message = UserController.update_user(
                    UserSession.get_current_user_id(),
                    user["user_id"],
                    **updates
                )
                print(message)
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
        user_id = user["user_id"]
        success, message = UserController.delete_user(
            UserSession.get_current_user_id(), user_id, user["username"]
        )
        print(message)
        if success:
            # If the deleted user is the currently logged-in user, log out immediately
            if user_id == UserSession.get_current_user_id():
                print("You have deleted your own account. Logging out...")
                session.logout()
            break

def list_users_flow(session):
    users = UserController.list_users(UserSession.get_current_user_id())
    print("\n--- User List ---")
    print("ID | Username | First Name | Last Name | Role")
    print("-" * 50)
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"{user['user_id']} | {user['username']} | {user['first_name']} | {user['last_name']} | {user['role']}")
    input("\nPress Enter to continue...")

#--------------------------------------------------------------------------------------
#                                The End of User Management
#--------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------
#                                  Traveller Management
#--------------------------------------------------------------------------------------
def manage_traveller_flow(session):
    """Nested menu for all traveller CRUD actions."""
    while True:
        print("\n--- Manage Travellers ---")
        print("1. Add traveller")
        print("2. Update traveller")
        print("3. Delete traveller")
        print("4. Search travellers")
        print("5. Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_traveller_flow(session)
        elif choice == "2":
            update_traveller_flow(session)
        elif choice == "3":
            delete_traveller_flow(session)
        elif choice == "4":
            search_traveller_flow(session)
        elif choice == "5":
            break
        else:
            print("Invalid choice")


# -----------------------------------------------------------
def add_traveller_flow(session):
    """CLI wizard to add a traveller (same pattern as add_user_flow)."""
    while True:
        # ------- names -------
        while True:
            first_name = input("First name: ")
            ok, msg = traveller_service._validate_name(first_name, "First name")
            if ok: break
            print(msg)
        while True:
            last_name = input("Last name: ")
            ok, msg = traveller_service._validate_name(last_name, "Last name")
            if ok: break
            print(msg)

        # ------- birthday & gender -------
        while True:
            birthday = input("Birthday (YYYY-MM-DD): ")
            ok, msg = traveller_service._validate_birthday(birthday)
            if ok: break
            print(msg)
        while True:
            gender = input("Gender (male/female): ")
            ok, msg = traveller_service._validate_gender(gender)
            if ok: break
            print(msg)

        # ------- address -------
        while True:
            street_name = input("Street name: ")
            ok, msg = traveller_service._validate_street_name(street_name)
            if ok: break
            print(msg)
        while True:
            house_number = input("House nº: ")
            ok, msg = traveller_service._validate_house_number(house_number)
            if ok: break
            print(msg)
        while True:
            zip_code = input("ZIP (1234AB): ")
            ok, msg = traveller_service._validate_zip(zip_code)
            if ok: break
            print(msg)
        while True:
            city = input(f"City {sorted(CITY_CHOICES)}: ")
            ok, msg = traveller_service._validate_city(city)
            if ok: break
            print(msg)

        # ------- contact -------
        while True:
            email = input("E-mail: ")
            ok, msg = traveller_service._validate_email(email)
            if ok: break
            print(msg)
        while True:
            mobile_phone = input("Mobile phone (+31-6-XXXXXXXX): ")
            ok, msg = traveller_service._validate_phone(mobile_phone)
            if ok: break
            print(msg)

        # ------- licence -------
        while True:
            driving_license_no = input("Driving licence nº (XXDDDDDDD or XDDDDDDDD): ")
            ok, msg = traveller_service._validate_license(driving_license_no)
            if ok: break
            print(msg)

        # ------- save -------
        success, message = TravellerController.add_traveller_controller(
            UserSession.get_current_user_id(),      # role-check needs this
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            street_name=street_name,
            house_number=house_number,
            zip_code=zip_code,
            city=city,
            email=email,
            mobile_phone=mobile_phone,
            driving_license_no=driving_license_no,
        )
        print(message)
        if success:
            input("Press Enter to continue...")
            break

# -----------------------------------------------------------
def _prompt_update(label: str, validator):
    """
    Ask for a field once or until it passes validation.
    Return None if user leaves it blank (→ keep current value).
    """
    while True:
        val = input(f"{label} (blank = keep): ").strip()
        if val == "":
            return None                         # skip this field
        ok, msg = validator(val)
        if ok:
            return val                          # valid → use it
        print(msg)                              # invalid → try again


def update_traveller_flow(session):
    print("\n=== Update traveller ===")
    try:
        traveller_id = int(input("Traveller ID to update: "))
    except ValueError:
        print("Not a number!")
        input("Press Enter to continue...")
        return

    updates = {}

    # ---------- names ----------
    first = _prompt_update("First name",
            lambda v: traveller_service._validate_name(v, "First name"))
    if first is not None: updates["first_name"] = first

    last  = _prompt_update("Last name",
            lambda v: traveller_service._validate_name(v, "Last name"))
    if last is not None:  updates["last_name"] = last

    # ---------- birthday & gender ----------
    bday  = _prompt_update("Birthday (YYYY-MM-DD)",
            traveller_service._validate_birthday)
    if bday is not None:  updates["birthday"] = bday

    gender = _prompt_update("Gender (male/female)",
            traveller_service._validate_gender)
    if gender is not None: updates["gender"] = gender

    # ---------- address ----------
    street = _prompt_update("Street name",
            traveller_service._validate_street_name)
    if street is not None: updates["street_name"] = street

    house  = _prompt_update("House nº",
            traveller_service._validate_house_number)
    if house is not None:  updates["house_number"] = house

    zipc   = _prompt_update("ZIP (1234AB)",
            traveller_service._validate_zip)
    if zipc is not None:   updates["zip_code"] = zipc

    city   = _prompt_update(f"City {sorted(CITY_CHOICES)}",
            traveller_service._validate_city)
    if city is not None:   updates["city"] = city

    # ---------- contact ----------
    email  = _prompt_update("E-mail",
            traveller_service._validate_email)
    if email is not None:  updates["email"] = email

    phone  = _prompt_update("Mobile phone (+31-6-XXXXXXXX)",
            traveller_service._validate_phone)
    if phone is not None:  updates["mobile_phone"] = phone

    # ---------- licence ----------
    licence = _prompt_update("Driving licence nº",
            traveller_service._validate_license)
    if licence is not None: updates["driving_license_no"] = licence

    # ---------- send to controller ----------
    if not updates:
        print("No updates given!")
        input("Press Enter to continue...")
        return

    ok, msg = TravellerController.update_traveller_controller(
        session.get_current_user_id(), traveller_id, **updates
    )
    print(msg)
    input("Press Enter to continue...")


# -----------------------------------------------------------
def delete_traveller_flow(session):
    print("\n=== Delete traveller ===")
    try:
        traveller_id = int(input("Traveller ID to delete: "))
    except ValueError:
        print("Not a number!")
        input("Press Enter to continue...")
        return
    confirm = input("Type YES to confirm: ")
    if confirm.strip().lower() == "yes":
        ok, msg = TravellerController.delete_traveller_controller(
            UserSession.get_current_user_id(), traveller_id
        )
        if not ok:
            print("Error:", msg)
            input("Press Enter to continue...")
            return
        else:
            msg = f"Traveller with ID {traveller_id} deleted successfully."
            print(msg)
            input("Press Enter to continue...")
    else:
        input("Deletion cancelled. Press Enter to continue...")



# -----------------------------------------------------------
def search_traveller_flow(session):
    key = input("\nSearch key (name / e-mail / phone): ")
    results = TravellerController.search_travellers_controller(
        UserSession.get_current_user_id(), key
    )
    if not results:
        print("No matches.")
    else:
        for row in results:
            print(row)
        input("Press Enter to continue...")


#--------------------------------------------------------------------------------------
#                                The End of Traveller Management
#--------------------------------------------------------------------------------------

def edit_account_flow(session):
    while True:
        user_id = UserSession.get_current_user_id()
        user = user_service.get_user_by_id(user_id)
        if not user:
            print("User not found.")
            return
        
        # Get user's role
        role = UserSession.get_current_role()
        
        # Display profile based on role
        if role in ["service_engineer", "system_admin"]:
            print(f"\n--- Profile Information ---")
            print(f"First Name: {user['first_name']}")
            print(f"Last Name: {user['last_name']}")
            print(f"Registration Date: {user['registration_date']}")
            print("\n1. Change first name")
            print("2. Change last name")
            print("3. Back/Exit to main menu")
        else:
            print(f"\n--- Edit Profile/Account: {user['user_id']} | {user['username']} ---")
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
                user_id,
                user_id,
                **updates
            )
            print(message)
            if success:
                # Optionally refresh session info if username was changed
                if "username" in updates:
                    UserSession._current_username = updates["username"]
                if "first_name" in updates:
                    UserSession._current_user.first_name = updates["first_name"]
                if "last_name" in updates:
                    UserSession._current_user.last_name = updates["last_name"]