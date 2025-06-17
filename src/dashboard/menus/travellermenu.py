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
)

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
        current_user_id = UserSession.get_current_user_id()
        success, message = TravellerController.add_traveller_controller(
            current_user_id,      # role-check needs this
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

    current_user_id = UserSession.get_current_user_id()
    ok, msg = TravellerController.update_traveller_controller(
        current_user_id, traveller_id, **updates
    )
    print(msg)
    input("Press Enter to continue...")

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
    key = input("\nSearch key (name / e-mail / phone): ")
    current_user_id = UserSession.get_current_user_id()
    results = TravellerController.search_travellers_controller(
        current_user_id, key
    )
    if not results:
        print("No matches.")
    else:
        for row in results:
            print(row)
        input("Press Enter to continue...")
