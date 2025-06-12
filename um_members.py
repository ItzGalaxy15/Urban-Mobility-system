# um_members.py
from dbcontext.dbcontext import create_db
from dbcontext.dbcontext import add_user
from controllers.usercontroller import change_password
from controllers.session import UserSession
from controllers.scootercontroller import add_scooter_controller

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

    while True:
        print(f"\nWelcome, {session.username} ({session.role})")
        option = input("Choose option: \n 1. Change password\n 2. Add scooter\n 3. Logout\n 4. Exit\n")
        if option == "1":
            old_pw = input("Enter your old password: ")
            new_pw = input("Enter your new password: ")
            success, message = change_password(session.user_id, old_pw, new_pw)
            print(message)
        # elif option == "2":
        #     try:
        #         print("\nEnter scooter details:")
        #         brand = input("Brand (2-30 alphanumeric chars): ")
        #         model = input("Model (1-30 alphanumeric chars): ")
        #         serial_number = input("Serial Number (10-17 alphanumeric chars): ")
        #         top_speed = input("Top Speed (5-50 km/h): ")
        #         battery_capacity = input("Battery Capacity (0-5000 Wh): ")
        #         state_of_charge = input("State of Charge (0-100%): ")
        #         target_soc_min = input("Target SOC Min (0-100%): ")
        #         target_soc_max = input("Target SOC Max (0-100%): ")
        #         location_lat = input("Location Lat (-90 to 90): ")
        #         location_lon = input("Location Lon (-180 to 180): ")
        #         out_of_service = input("Out of Service (1 for Yes, 2 for No): ")
        #         mileage = input("Mileage (0-1,000,000 km): ")
        #         last_maint_date = input("Last Maintenance Date (YYYY-MM-DD): ")

        #         success, message = add_scooter_controller(
        #             brand, model, serial_number, top_speed, battery_capacity,
        #             state_of_charge, target_soc_min, target_soc_max, location_lat,
        #             location_lon, out_of_service, mileage, last_maint_date
        #         )
        #         print(message)
        #     except KeyboardInterrupt:
        #         print("\nScooter addition cancelled")
        #     except Exception as e:
        #         print(f"Error adding scooter: {str(e)}")
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
