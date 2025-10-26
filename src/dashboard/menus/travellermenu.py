from controllers.traveller_controller import TravellerController
from services.session_service import session_service
from utils.validation import (
    validate_first_name, validate_last_name, validate_birthday, validate_gender,
    validate_street_name, validate_house_number, validate_zip, validate_city,
    validate_email, validate_phone, validate_license, CITY_CHOICES
)
from typing import Callable, Optional, Tuple
CANCEL_KEYWORDS = {"back", "exit"}

def ask(label: str, validator: Optional[Callable[[str], Tuple[bool, str]]] = None) -> Optional[str]:
    """
    Ask the user for a value. If a validator is given, repeat until it passes.
    If the user types 'back' or 'exit', return None to cancel.

    Args:
        label: The prompt shown to the user.
        validator: A function that takes the input string and returns (ok, message).

    Returns:
        The validated input string, or None if the user cancels.
    """
    while True:
        value = input(f"{label}: ")
        if value in CANCEL_KEYWORDS:
            return None
        if validator:
            ok, msg = validator(value)
            if not ok:
                print(f"Error: {msg}")
                continue
        return value

def add_traveller_flow(session) -> None:
    """
    Collect traveller details from the user and save them.

    Args:
        session: The current user session

    Returns:
        None. Prints feedback to the console.
    """
    print("\n=== Add Traveller ===")
    print("Type 'back' or 'exit' at any prompt to cancel.\n")

    # ── Collect data ─────────────────────────────────────────────
    data = {}

    data["first_name"] = ask("First name", validate_first_name)
    if data["first_name"] is None: return print("Add cancelled.")

    data["last_name"] = ask("Last name", validate_last_name)
    if data["last_name"] is None: return print("Add cancelled.")

    data["birthday"] = ask("Birthday (YYYY-MM-DD)", validate_birthday)
    if data["birthday"] is None: return print("Add cancelled.")

    data["gender"] = ask("Gender (male/female)", validate_gender)
    if data["gender"] is None: return print("Add cancelled.")

    data["street_name"] = ask("Street name", validate_street_name)
    if data["street_name"] is None: return print("Add cancelled.")

    data["house_number"] = ask("House nº", validate_house_number)
    if data["house_number"] is None: return print("Add cancelled.")

    data["zip_code"] = ask("ZIP (1234AB)", validate_zip)
    if data["zip_code"] is None: return print("Add cancelled.")

    data["city"] = ask(f"City {sorted(CITY_CHOICES)}", validate_city)
    if data["city"] is None: return print("Add cancelled.")

    data["email"] = ask("E-mail", validate_email)
    if data["email"] is None: return print("Add cancelled.")

    data["mobile_phone"] = ask("Mobile phone (+31-6-DDDDDDDD)", validate_phone)
    if data["mobile_phone"] is None: return print("Add cancelled.")

    data["driving_license_no"] = ask("Driving licence nº (XXDDDDDDD or XDDDDDDDD)", validate_license)
    if data["driving_license_no"] is None: return print("Add cancelled.")

    # ── Final review ────────────────────────────────────────────
    print("\nPlease review the entered data:")
    for k, v in data.items():
        print(f"  {k.replace('_',' ').title()}: {v}")

    answer = input("\nSave this traveller? (y/n): ")

    if answer != "y":
        print("Add cancelled.")
        input("Press Enter to continue...")
        return
    
    

    # ── Persist ─────────────────────────────────────────────────
    current_user_id = session_service.get_current_user_id()
    success, message = TravellerController.add_traveller_controller(
        current_user_id, **data
    )
    print(message)
    input("Press Enter to continue..." if success else "\nPress Enter to return...")

def _prompt_update(label: str, validator: Callable[[str], Tuple[bool, str]]) -> Optional[str]:
    """
    Ask once for a value and validate. If blank, keep current value.

    Args:
        label: The prompt shown to the user.
        validator: A function that validates the input, returning (ok, message).

    Returns:
        The new value if valid, or None to keep the current value.
    """
    while True:
        val = input(f"{label} (blank = keep): ")
        if val == "":
            return None                         # skip this field
        ok, msg = validator(val)
        if ok:
            return val                          # valid → use it
        print(msg)                              # invalid → try again

def update_traveller_flow(session) -> None:
    """
    Update selected traveller fields.

    Args:
        session: The current user session

    Returns:
        None. Prints feedback to the console.
    """
    user_input = input("Enter Traveller ID to update (leave blank to cancel): ")

    if user_input == "":
        print("Update cancelled.")
        input("Press Enter to continue...")
        return

    if not user_input.isdigit():
        print("Invalid input. Please enter a number.")
        input("Press Enter to continue...")
        return

    traveller_id = int(user_input)

    updates = {}

    # ---------- names ----------
    first = _prompt_update("First name", validate_first_name)
    if first is not None: updates["first_name"] = first

    last  = _prompt_update("Last name", validate_last_name)
    if last is not None:  updates["last_name"] = last

    # ---------- birthday & gender ----------
    bday  = _prompt_update("Birthday (YYYY-MM-DD)", validate_birthday)
    if bday is not None:  updates["birthday"] = bday

    gender = _prompt_update("Gender (male/female)", validate_gender)
    if gender is not None: updates["gender"] = gender

    # ---------- address ----------
    street = _prompt_update("Street name", validate_street_name)
    if street is not None: updates["street_name"] = street

    house  = _prompt_update("House nº", validate_house_number)
    if house is not None:  updates["house_number"] = house

    zipc   = _prompt_update("ZIP (1234AB)", validate_zip)
    if zipc is not None:   updates["zip_code"] = zipc

    city   = _prompt_update(f"City {sorted(CITY_CHOICES)}", validate_city)
    if city is not None:   updates["city"] = city

    # ---------- contact ----------
    email  = _prompt_update("E-mail", validate_email)
    if email is not None:  updates["email"] = email

    phone  = _prompt_update("Mobile phone (+31-6-DDDDDDDD)", validate_phone)
    if phone is not None:  updates["mobile_phone"] = phone

    # ---------- licence ----------
    licence = _prompt_update("Driving licence nº", validate_license)
    if licence is not None: updates["driving_license_no"] = licence

    # ---------- send to controller ----------
    if not updates:
        print("No updates given!")
        input("Press Enter to continue...")
        return

    current_user_id = session_service.get_current_user_id()
    ok, msg = TravellerController.update_traveller_controller(
        current_user_id, traveller_id, **updates
    )
    print(msg)
    input("Press Enter to continue...")

def delete_traveller_flow(session) -> None:
    """
    Delete a traveller by id after confirmation.

    Args:
        session: The current user session (not used directly here)

    Returns:
        None. Prints feedback to the console.
    """
    print("\n=== Delete Traveller ===")

    user_input = input("Enter Traveller ID to delete (leave blank to cancel): ")

    if user_input == "":
        print("Deletion cancelled.")
        input("Press Enter to continue...")
        return

    if not user_input.isdigit():
        print("Invalid input. Please enter a number.")
        input("Press Enter to continue...")
        return

    traveller_id = int(user_input)
    confirm = input("Type 'yes' to confirm: ")
    if confirm == "yes":
        current_user_id = session_service.get_current_user_id()
        ok, msg = TravellerController.delete_traveller_controller(
            current_user_id, traveller_id
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

def search_traveller_flow(session) -> None:
    """
    Search travellers by a free text key.

    Args:
        session: The current user session

    Returns:
        None. Prints the search results.
    """
    # Traveller Search Menu
    print("\n=== Traveller Search ===")

    # Field-specific search
    print("\nSelect field to search:")
    print("1. First Name")
    print("2. Last Name") 
    print("3. Email")
    print("4. Mobile Phone")
    print("5. ZIP Code")
    print("6. City")
    print("7. Street Name")
    print("8. Driving License")
    
    field_choice = input("Select field (1-8): ")
    if field_choice not in [str(i) for i in range(1, 9)]:
        print("Invalid choice. Search cancelled.")
        input("Press Enter to continue...")
        return
    search_term = input("Enter search term: ")
    
    # Map to actual field name
    field_map = {
        "1": "first_name",
        "2": "last_name",
        "3": "email",
        "4": "mobile_phone",
        "5": "zip_code",
        "6": "city",
        "7": "street_name",
        "8": "driving_license",
    }

    search_field = field_map[field_choice]
    current_user_id = session_service.get_current_user_id()
    results = TravellerController.search_travellers_controller(current_user_id, search_term, search_field)

    if not results or not results[0]:
        print("No matches found.")
    else:
        print(f"\nFound {len(results)} traveller(s):\n")
        for row in results:
            print(row)

    input("Press Enter to continue...")
