import os
from controllers.usercontroller import UserController
from controllers.session import UserSession
from dashboard.dashboard import build_menu_with_roles_and_permissions, display_menu
from controllers.scootercontroller import ScooterController
import re

from models.scooter import BATTERY_CAP_MAX, BRAND_RE, DATE_RE, MILEAGE_MAX, MODEL_RE, SERIAL_RE, TOP_SPEED_MAX, TOP_SPEED_MIN

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
    success, message = ScooterController.service_scooter(session, scooter_id=scooter_id, update_data=new_scooter) if UserSession.get_current_role() == "service_engineer" else ScooterController.update_scooter(scooter)

    print(message)
    if success:
        print("Scooter updated successfully.")
    else:
        print("Failed to update scooter.")

def view_scooters_flow(session):
    scooters = ScooterController.view_scooters_flow(session)
    if scooters:
        print("\nScooters:")
        for scooter in scooters:
            print(f"{scooter.scooter_id}: {scooter.name} - {scooter.model} (State of Charge: {scooter.state_of_charge}%)")
    else:
        print("No scooters found.")

def delete_scooter_flow(session):
    scooter_id = input("Enter the ID of the scooter to delete: ")
    success, message = ScooterController.delete_scooter_flow(session, scooter_id)
    print(message)
    if success:
        print("Scooter deleted successfully.")
    else:
        print("Failed to delete scooter.")
