import os
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from controllers.scootercontroller import ScooterController
import re

from models.scooter import Scooter, BATTERY_CAP_MAX, BRAND_RE, DATE_RE, MILEAGE_MAX, MODEL_RE, SERIAL_RE, TOP_SPEED_MAX, TOP_SPEED_MIN

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
    input("Press Enter to continue...")

# Scooter Management Menu Actions #
def add_scooter_flow(session):
    print("\nAdd New Scooter")
    
    new_scooter = ScooterController.create_scooter()

    success, message = ScooterController.add_scooter(session, new_scooter)
    print(message)
    if success:
        print("Scooter added successfully.")
    else:
        print("Failed to add scooter.")
    input("Press Enter to continue...")

def update_scooter_flow(session):
    print("\nUpdate Scooter")
    scooter_id = input("Enter the ID of the scooter to update: ")
    scooter = ScooterController.get_scooter(session, scooter_id)
    if not scooter:
        print("Scooter not found.")
        return

    new_scooter = ScooterController.create_scooter(scooter[0], session._current_role == "service_engineer")

    # Call the service method if the user is a service engineer otherwise call update method
    if UserSession.get_current_role() == "service_engineer":
        success, message = ScooterController.service_scooter(session, scooter_id=scooter_id, update_data=new_scooter)
    else:
        success, message = ScooterController.update_scooter(scooter)

    print(message)
    if success:
        print("Scooter updated successfully.")
    else:
        print("Failed to update scooter.")
    input("Press Enter to continue...")

def view_scooters_flow(session):
    print("\nView Scooters")

    choice = input("Do you want to view all scooters? (y/n): ")
    if choice.lower() == 'n':
        scooter_id = input("Enter the ID of the scooter to view: ")
        scooters = ScooterController.get_scooter(session, scooter_id)
    elif choice.lower() == 'y':
        scooters = ScooterController.get_scooter(session)
    else:
        print("Invalid choice.")
        return

    if scooters[0]:
        print("\nScooter(s):")
        for scooter_id, scooter in enumerate(scooters[0]):
            print(f"\nScooter #{scooter_id + 1}:")
            for attr, value in vars(scooter).items():
                print(f"  {attr}: {value}")
            print("\n" + ("-" * 30))
    else:
        print("No scooters found.")
    input("Press Enter to continue...")

def search_scooters_flow(session):
    print("\nSearch Scooters")

    # Print out all fields from the scooter object as a reference for the user
    scooter_fields = [
        "brand",
        "model",
        "serial_number",
        "top_speed",
        "battery_capacity",
        "state_of_charge",
        "target_soc_min",
        "target_soc_max",
        "location_lat",
        "location_lon",
        "scooter_id",
        "mileage",
        "out_of_service",
        "last_maint_date"
    ]
    print("\nAvailable fields to search by:\n" + " | ".join(scooter_fields))

    # Ask user for the field to search by
    field = input("Enter field to search by (leave blank to search all fields): ").strip() or None

    # Ask user for search term
    search_term = input("Enter search term: ")

    # Call the search method
    results = ScooterController.search_for_scooters(session, search_term, field)
    if results:
        print(f"\nFound {len(results[0])} scooter(s):")
        for idx, scooter in enumerate(results[0], 1):
            print(f"\nScooter #{idx} - ({scooter.scooter_id}):")
            for attr, value in vars(scooter).items():
                print(f"  {attr}: {value}")
            print("\n" + ("-" * 30))
    else:
        print("No scooters found matching your search.")
    input("Press Enter to continue...")

def delete_scooter_flow(session):
    scooter_id = input("Enter the ID of the scooter to delete: ")
    success, message = ScooterController.delete_scooter(session, scooter_id)
    print(message)
    if success:
        print("Scooter deleted successfully.")
    else:
        print("Failed to delete scooter.")
    input("Press Enter to continue...")
