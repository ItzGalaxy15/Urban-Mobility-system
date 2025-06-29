from controllers.scootercontroller import ScooterController
from controllers.session import UserSession
from models.scooter import Scooter
from utils.validation import validate_brand, validate_model, validate_serial_number
import re

# Validation patterns for user input
SCOOTER_ID_PATTERN = re.compile(r'^[0-9]+$')  # Only digits
SEARCH_TERM_PATTERN = re.compile(r'^[A-Za-z0-9\s\-_]{1,50}$')  # Alphanumeric, spaces, dashes, underscores
CHOICE_PATTERN = re.compile(r'^[ynYN]$')  # Only y/n

def validate_scooter_id(scooter_id: str) -> tuple[bool, str]:
    """Validate scooter ID input"""
    if not scooter_id:
        return False, "Scooter ID is required"
    if SCOOTER_ID_PATTERN.fullmatch(scooter_id):
        return True, ""
    return False, "Scooter ID must contain only digits"

def validate_search_term(search_term: str) -> tuple[bool, str]:
    """Validate search term input"""
    if not search_term:
        return False, "Search term is required"
    if SEARCH_TERM_PATTERN.fullmatch(search_term):
        return True, ""
    return False, "Search term must be 1-50 characters and contain only letters, numbers, spaces, dashes, and underscores"

def validate_choice(choice: str) -> tuple[bool, str]:
    """Validate y/n choice input"""
    if not choice:
        return False, "Choice is required"
    if CHOICE_PATTERN.fullmatch(choice):
        return True, ""
    return False, "Choice must be 'y' or 'n'"

def safe_input(prompt: str, validator=None) -> str:
    """Get user input with validation"""
    while True:
        value = input(prompt)
        if validator:
            valid, message = validator(value)
            if not valid:
                print(f"Error: {message}")
                continue
        return value

def display_scooter_data(scooter):
    """Display scooter data using decrypted properties"""
    print(f"  scooter_id: {scooter.scooter_id}")
    print(f"  brand: {scooter.brand_plain}")
    print(f"  model: {scooter.model_plain}")
    print(f"  serial_number: {scooter.serial_number_plain}")
    print(f"  top_speed: {scooter.top_speed} km/h")
    print(f"  battery_capacity: {scooter.battery_capacity} Wh")
    print(f"  state_of_charge: {scooter.state_of_charge}%")
    print(f"  target_soc_min: {scooter.target_soc_min}%")
    print(f"  target_soc_max: {scooter.target_soc_max}%")
    print(f"  location_lat: {scooter.location_lat}")
    print(f"  location_lon: {scooter.location_lon}")
    print(f"  mileage: {scooter.mileage} km")
    print(f"  out_of_service: {'Yes' if scooter.is_out_of_service else 'No'}")
    print(f"  last_maint_date: {scooter.last_maint_date}")
    print(f"  in_service_date: {scooter.in_service_date}")

def add_scooter_flow(session):
    print("\nAdd New Scooter")
    
    new_scooter = ScooterController.create_scooter()
    current_user_id = UserSession.get_current_user_id()

    success, message = ScooterController.add_scooter(current_user_id, new_scooter)
    print(message)
    if success:
        print("Scooter added successfully.")
    else:
        print("Failed to add scooter.")
    input("Press Enter to continue...")

def update_scooter_flow(session):
    print("\nUpdate Scooter")
    current_user_id = UserSession.get_current_user_id()
    
    # Validate scooter ID input
    scooter_id = safe_input("Enter the ID of the scooter to update: ", validate_scooter_id)
    
    # Get the scooter - returns (scooter, message) tuple
    scooter_result = ScooterController.get_scooter(current_user_id, scooter_id)
    scooter, message = scooter_result
    
    if not scooter:
        print("Scooter ID not found.")
        input("Press Enter to continue...")
        return

    new_scooter = ScooterController.create_scooter(scooter, session._current_role == "service_engineer")

    # Call the service method if the user is a service engineer otherwise call update method
    if UserSession.get_current_role() == "service_engineer":
        success, message = ScooterController.service_scooter(current_user_id, scooter_id=scooter_id, update_data=new_scooter)
    else:
        success, message = ScooterController.update_scooter(current_user_id, scooter_id, new_scooter)

    print(message)
    if success:
        print("Scooter updated successfully.")
    else:
        print("Failed to update scooter.")
    input("Press Enter to continue...")

def view_scooters_flow(session):
    print("\nView Scooters")
    current_user_id = UserSession.get_current_user_id()

    # Validate choice input
    choice = safe_input("Do you want to view all scooters? (y/n): ", validate_choice)
    
    if choice.lower() == 'n':
        # Validate scooter ID input
        scooter_id = safe_input("Enter the ID of the scooter to view: ", validate_scooter_id)
        scooters_result = ScooterController.get_scooter(current_user_id, scooter_id)
        scooters, message = scooters_result
    elif choice.lower() == 'y':
        scooters_result = ScooterController.get_scooter(current_user_id)
        scooters, message = scooters_result
    else:
        print("Invalid choice.")
        input("Press Enter to continue...")
        return

    if scooters:
        print("\nScooter(s):")
        # Handle both single scooter and list of scooters
        if isinstance(scooters, list):
            for scooter_id, scooter in enumerate(scooters, 1):
                print(f"\nScooter #{scooter_id}:")
                display_scooter_data(scooter)
                print("\n" + ("-" * 30))
        else:
            # Single scooter
            print(f"\nScooter:")
            display_scooter_data(scooters)
            print("\n" + ("-" * 30))
    else:
        print("No scooters found.")
    input("Press Enter to continue...")

def search_scooters_flow(session):
    print("\nSearch Scooters")
    current_user_id = UserSession.get_current_user_id()

    # Print out all fields from the scooter object as a reference for the user
    scooter_fields = [
        "brand",
        "model",
        "serial_number"
    ]
    print("\nAvailable fields to search by:")
    for idx, field_name in enumerate(scooter_fields, 1):
        print(f"{idx}. {field_name}")
    print(f"{len(scooter_fields) + 1}. All fields")

    # Ask user for the field to search by using a menu with validation
    while True:
        try:
            choice_input = input(f"Select field to search by (1-{len(scooter_fields) + 1}): ")
            if not choice_input.isdigit():
                print("Please enter a valid number.")
                continue
            choice = int(choice_input)
            if 1 <= choice <= len(scooter_fields):
                field = scooter_fields[choice - 1]
                break
            elif choice == len(scooter_fields) + 1:
                field = None
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Validate search term input
    search_term = safe_input("Enter search term: ", validate_search_term)

    # Call the search method - returns (scooters, message) tuple
    results = ScooterController.search_for_scooters(current_user_id, search_term, field)
    scooters, message = results
    
    if scooters:
        print(f"\nFound {len(scooters)} scooter(s):")
        for idx, scooter in enumerate(scooters, 1):
            print(f"\nScooter #{idx} - ({scooter.scooter_id}):")
            display_scooter_data(scooter)
            print("\n" + ("-" * 30))
    else:
        print("No scooters found matching your search.")
    input("Press Enter to continue...")

def delete_scooter_flow(session):
    current_user_id = UserSession.get_current_user_id()
    
    # Validate scooter ID input
    scooter_id = safe_input("Enter the ID of the scooter to delete: ", validate_scooter_id)
    
    success, message = ScooterController.delete_scooter(current_user_id, scooter_id)
    print(message)
    input("Press Enter to continue...")
