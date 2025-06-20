from controllers.traveller_controller import TravellerController
from controllers.session import UserSession
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
    STREET_RE
)
CANCEL_KEYWORDS = {"back", "exit"}

def ask(label: str, validator) -> str | None:
    """
    Prompt until the validator returns (True, _).
    Return None if the user types a cancel keyword.
    """
    while True:
        value = input(f"{label}: ").strip()
        if value.lower() in CANCEL_KEYWORDS:
            return None
        ok, msg = validator(value)
        if ok:
            return value
        print(msg)

def add_traveller_flow(session):
    print("\n=== Add Traveller ===")
    print("Type 'back' or 'exit' at any prompt to cancel.\n")

    # ── Collect data ─────────────────────────────────────────────
    data = {}

    data["first_name"] = ask("First name", 
                             lambda v: traveller_service._validate_name(v, "First name"))
    if data["first_name"] is None: return print("Add cancelled.")

    data["last_name"] = ask("Last name",  
                            lambda v: traveller_service._validate_name(v, "Last name"))
    if data["last_name"] is None: return print("Add cancelled.")

    data["birthday"] = ask("Birthday (YYYY-MM-DD)", traveller_service._validate_birthday)
    if data["birthday"] is None: return print("Add cancelled.")

    data["gender"] = ask("Gender (male/female)", traveller_service._validate_gender)
    if data["gender"] is None: return print("Add cancelled.")

    data["street_name"] = ask("Street name", traveller_service._validate_street_name)
    if data["street_name"] is None: return print("Add cancelled.")

    data["house_number"] = ask("House nº", traveller_service._validate_house_number)
    if data["house_number"] is None: return print("Add cancelled.")

    data["zip_code"] = ask("ZIP (1234AB)", traveller_service._validate_zip)
    if data["zip_code"] is None: return print("Add cancelled.")

    data["city"] = ask(f"City {sorted(CITY_CHOICES)}", traveller_service._validate_city)
    if data["city"] is None: return print("Add cancelled.")

    data["email"] = ask("E-mail", traveller_service._validate_email)
    if data["email"] is None: return print("Add cancelled.")

    data["mobile_phone"] = ask("Mobile phone (+31-6-DDDDDDDD)", 
                               traveller_service._validate_phone)
    if data["mobile_phone"] is None: return print("Add cancelled.")

    data["driving_license_no"] = ask("Driving licence nº (XXDDDDDDD or XDDDDDDDD)",
                                     traveller_service._validate_license)
    if data["driving_license_no"] is None: return print("Add cancelled.")

    # ── Final review ────────────────────────────────────────────
    print("\nPlease review the entered data:")
    for k, v in data.items():
        print(f"  {k.replace('_',' ').title()}: {v}")

    if input("\nSave this traveller? (y/n): ").strip().lower() != "y":
        print("Add cancelled.")
        input("Press Enter to continue...")
        return

    # ── Persist ─────────────────────────────────────────────────
    current_user_id = UserSession.get_current_user_id()
    success, message = TravellerController.add_traveller_controller(
        current_user_id, **data
    )
    print(message)
    input("Press Enter to continue..." if success else "\nPress Enter to return...")

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
    user_input = input("Enter Traveller ID to update (leave blank to cancel): ").strip()

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

    phone  = _prompt_update("Mobile phone (+31-6-DDDDDDDD)",
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

    current_user_id = UserSession.get_current_user_id()
    ok, msg = TravellerController.update_traveller_controller(
        current_user_id, traveller_id, **updates
    )
    print(msg)
    input("Press Enter to continue...")

def delete_traveller_flow(session):
    print("\n=== Delete Traveller ===")

    user_input = input("Enter Traveller ID to delete (leave blank to cancel): ").strip()

    if user_input == "":
        print("Deletion cancelled.")
        input("Press Enter to continue...")
        return

    if not user_input.isdigit():
        print("Invalid input. Please enter a number.")
        input("Press Enter to continue...")
        return

    traveller_id = int(user_input)
    confirm = input("Type YES to confirm: ")
    if confirm.strip().lower() == "yes":
        current_user_id = UserSession.get_current_user_id()
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

def search_traveller_flow(session):
    key = input("\nSearch key (name / e-mail / phone, leave blank to cancel): ").strip()

    if key == "":
        print("Search cancelled.")
        input("Press Enter to continue...")
        return

    current_user_id = UserSession.get_current_user_id()
    results = TravellerController.search_travellers_controller(current_user_id, key)

    if not results:
        print("No matches found.")
    else:
        for row in results:
            print(row)

    input("Press Enter to continue...")
