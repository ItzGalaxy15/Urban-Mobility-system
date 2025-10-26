from controllers.scootercontroller import ScooterController
from controllers.session_controller import session_controller
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
    current_user_id = session_controller.get_current_user_id()

    success, message = ScooterController.add_scooter(current_user_id, new_scooter)
    print(message)
    if success:
        print("Scooter added successfully.")
    else:
        print("Failed to add scooter.")
    input("Press Enter to continue...")

def update_scooter_flow(session):
    print("\nUpdate Scooter")
    current_user_id = session_controller.get_current_user_id()
    
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
    if session_controller.get_current_role() == "service_engineer":
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
    current_user_id = session_controller.get_current_user_id()

    # Validate choice input
    choice = safe_input("Do you want to view all scooters? (y/n): ", validate_choice)
    
    if choice == 'n':
        # Validate scooter ID input
        scooter_id = safe_input("Enter the ID of the scooter to view: ", validate_scooter_id)
        scooters_result = ScooterController.get_scooter(current_user_id, scooter_id)
        scooters, message = scooters_result
    elif choice == 'y':
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
    print("\n=== Scooter Search ===")
    
    current_user_id = session_controller.get_current_user_id()

    # Advanced Search - field-specific
    print("\n--- Advanced Search ---")
    print("Select field to search:")
    print("1. Brand")
    print("2. Model")
    print("3. Serial Number")

    field_choice = input("\nSelect field (1-3): ")
    if field_choice not in ["1", "2", "3"]:
        print("Invalid choice. Search cancelled.")
        input("Press Enter to continue...")
        return

    # Map to actual field names
    field_map = {
        "1": "brand",
        "2": "model",
        "3": "serial_number"
    }
    
    field_name = field_map[field_choice]
    field_display = {
        "brand": "Brand",
        "model": "Model", 
        "serial_number": "Serial Number"
    }[field_name]

    search_term = input(f"Enter {field_display} to search: ")

    if not search_term:
        print("Search cancelled.")
        input("Press Enter to continue...")
        return
    
    # Call field-specific search method
    results = ScooterController.search_for_scooters(current_user_id, search_term, field_name)
    scooters, message = results
    
    # Display results
    if scooters:
        print(f"\n{message}")
        for idx, scooter in enumerate(scooters, 1):
            print(f"\nScooter #{idx} - (ID: {scooter.scooter_id}):")
            display_scooter_data(scooter)
            print("\n" + ("-" * 30))
    else:
        print(f"\n{message}")
    input("Press Enter to continue...")

def delete_scooter_flow(session):
    current_user_id = session_controller.get_current_user_id()
    
    # Validate scooter ID input
    scooter_id = safe_input("Enter the ID of the scooter to delete: ", validate_scooter_id)
    
    success, message = ScooterController.delete_scooter(current_user_id, scooter_id)
    print(message)
    input("Press Enter to continue...")
