# um_members.py
from dbcontext.dbcontext import create_db
from dbcontext.dbcontext import add_user
from controllers.usercontroller import change_password
from controllers.session import UserSession
from controllers.scootercontroller import ScooterController
from validation.scooter_validation import validate_scooter_inputs
import os

def main():
    print("Urban Mobility System Starting...")
    create_db()
    add_user("mike_admin", "StrongPass123!", "Mike", "Jansen", "system_admin")
    add_user("john_eng", "Password123!", "John", "Doe", "service_engineer")

    session = UserSession()
    while not session.is_authenticated():
        username = input("Username: ")
        password = input("Password: ")
        session.login(username, password)

    scooter_controller = ScooterController("urban_mobility.db")

    while True:
        os.system("cls")
        print(f"\nWelcome, {session.username} ({session.role})")
        print("\nMain Menu:")
        print("1. Change password")
        print("2. Scooter Management")
        print("3. Logout")
        print("4. Exit")
        
        option = input("\nChoose an option (1-4): ")
        
        if option == "1":
            old_pw = input("Enter your old password: ")
            new_pw = input("Enter your new password: ")
            success, message = change_password(session.user_id, old_pw, new_pw)
            print(message)
            
        elif option == "2":
            if session.role not in {"super", "system_admin"}:
                print("Access denied: Only super admin and system admin can manage scooters")
                continue
                
            print("\nScooter Management:")
            print("1. Add new scooter")
            print("2. View scooter details")
            print("3. Back to main menu")
            
            scooter_option = input("\nChoose an option (1-3): ")
            
            if scooter_option == "1":
                scooter_data, success = validate_scooter_inputs()
                if success:
                    success, message = scooter_controller.add_scooter(session.user, scooter_data)
                    print(message)
                    
            elif scooter_option == "2":
                try:
                    scooter_id = int(input("\nEnter scooter ID to view: "))
                    scooter, message = scooter_controller.get_scooter(session.user, scooter_id)
                    if scooter:
                        print("\nScooter Details:")
                        print(f"ID: {scooter.scooter_id}")
                        print(f"Brand: {scooter.brand_plain}")
                        print(f"Model: {scooter.model_plain}")
                        print(f"Serial Number: {scooter.serial_number_plain}")
                        print(f"Top Speed: {scooter.top_speed} km/h")
                        print(f"Battery Capacity: {scooter.battery_capacity} Wh")
                        print(f"State of Charge: {scooter.state_of_charge}%")
                        print(f"Target SOC Range: {scooter.target_soc_min}% - {scooter.target_soc_max}%")
                        print(f"Location: {scooter.location_lat}, {scooter.location_lon}")
                        print(f"Status: {'Out of Service' if scooter.is_out_of_service else 'In Service'}")
                        print(f"Mileage: {scooter.mileage} km")
                        if scooter.last_maint_date:
                            print(f"Last Maintenance: {scooter.last_maint_date}")
                    else:
                        print(message)
                except ValueError:
                    print("Invalid scooter ID")
                except Exception as e:
                    print(f"Error retrieving scooter: {str(e)}")
                    
            elif scooter_option == "3":
                continue
            else:
                print("Invalid option")
                
        elif option == "3":
            session.logout()
            break
        elif option == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
