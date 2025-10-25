import datetime
from typing import Optional, Dict, Any
from models.scooter import Scooter
from models.user import User
from services.userservice import UserService, user_service
from services.scooterservice import ScooterService
from utils.role_utils import require_role
from models.scooter import BATTERY_CAP_MAX, MILEAGE_MAX, TOP_SPEED_MAX, TOP_SPEED_MIN
from utils.validation import validate_brand, validate_model, validate_serial_number, validate_scooter_date
from services.session_service import session_service
from utils.log_decorator import log_action
from config import DB_FILE

# Create singleton service instance
_scooterservice = ScooterService(DB_FILE) 

class ScooterController:
    @staticmethod
    @require_role("super", "system_admin")
    @log_action("Add scooter -> {msg}")
    def add_scooter(current_user_id: int, new_scooter: Scooter) -> tuple[bool, str]:
        try:
            if _scooterservice.add_scooter(scooter=new_scooter):
                return True, f"Scooter {new_scooter.serial_number_plain} added successfully"
            return False, "Failed to add scooter to database"

        except KeyError as e:
            return False, f"Missing required field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid scooter data: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    @log_action("Get scooter(s) -> {msg}")
    @require_role("super", "system_admin", "service_engineer")
    def get_scooter(user_id: int, scooter_id: int | None = None) -> tuple[Optional[Scooter], str]:
        try:
            if scooter_id is None:
                scooters = _scooterservice.get_all_scooters()
                if scooters:
                    return scooters, f"Retrieved {len(scooters)} scooters successfully"
                return None, "No scooters found"
            else:
                scooter = _scooterservice.get_scooter_by_id(scooter_id)
                if scooter:
                    return scooter, "Scooter retrieved successfully"
                return None, "Scooter not found"
        except Exception as e:
            return None, f"Error retrieving scooter(s): {str(e)}"

    @staticmethod
    @log_action("Service scooter -> {msg}") 
    @require_role("service_engineer")
    def service_scooter(user_id: int, scooter_id: int, update_data: Scooter) -> tuple[bool, str]:
        user = user_service.get_user_by_id(user_id)
        if user.role_plain != "service_engineer":
            return False, "Unauthorized: Only service engineer can use this function"

        allowed_fields = {
            "state_of_charge",
            "mileage",
            "out_of_service",
            "last_maint_date"
        }

        try:
            scooter = _scooterservice.get_scooter_by_id(scooter_id)
            if not scooter:
                return False, "Scooter not found"

            # Update only allowed fields for service engineers
            if hasattr(update_data, 'state_of_charge'):
                scooter.state_of_charge = update_data.state_of_charge
            if hasattr(update_data, 'mileage'):
                scooter.mileage = update_data.mileage
            if hasattr(update_data, 'out_of_service'):
                scooter.out_of_service = update_data.out_of_service
            if hasattr(update_data, 'last_maint_date'):
                scooter.last_maint_date = update_data.last_maint_date

            if _scooterservice.update_scooter(scooter):
                return True, f"Scooter {scooter_id} updated successfully"
            return False, "Failed to update scooter in database"

        except KeyError as e:
            return False, f"Invalid field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid input: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    @log_action("Update scooter -> {msg}")
    @require_role("super", "system_admin")
    def update_scooter(user_id: int, scooter_id: int, update_data: Scooter) -> tuple[bool, str]:
        try:
            scooter = _scooterservice.get_scooter_by_id(scooter_id)
            if not scooter:
                return False, "Scooter not found"

            # Update all fields from the new scooter object
            scooter.brand = update_data.brand
            scooter.model = update_data.model
            scooter.serial_number = update_data.serial_number
            scooter.top_speed = update_data.top_speed
            scooter.battery_capacity = update_data.battery_capacity
            scooter.state_of_charge = update_data.state_of_charge
            scooter.target_soc_min = update_data.target_soc_min
            scooter.target_soc_max = update_data.target_soc_max
            scooter.location_lat = update_data.location_lat
            scooter.location_lon = update_data.location_lon
            scooter.mileage = update_data.mileage
            scooter.out_of_service = update_data.out_of_service
            scooter.last_maint_date = update_data.last_maint_date

            if _scooterservice.update_scooter(scooter):
                return True, f"Scooter {scooter_id} updated successfully"
            return False, "Failed to update scooter in database"

        except KeyError as e:
            return False, f"Invalid field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid input: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    @log_action("Search scooters -> {msg}")
    @require_role("super", "system_admin", "service_engineer")
    def search_for_scooters(user_id: int, search_term: str, field_name: str, limit: int = 50) -> tuple[Optional[list[Scooter]], str]:
        """
        Search for scooters by partial text match across brand, model, and serial_number.
        Uses intelligent field detection and minimal decryption strategy.
        """
        scooters = _scooterservice.search_for_scooters(search_term, field_name, limit)
        if scooters:
            return scooters, f"Found {len(scooters)} scooter(s) matching '{search_term}'"
        return None, f"No scooters found matching '{search_term}'"

    @staticmethod
    @log_action("Delete scooter -> {msg}")
    @require_role("super", "system_admin")
    def delete_scooter(user_id: int, scooter_id: int) -> tuple[bool, str]:

        if _scooterservice.delete_scooter(scooter_id):
            return True, f"Scooter {scooter_id} deleted successfully"
        return False, "Failed to delete scooter from database"

    @staticmethod
    def create_scooter(old_scooter: Scooter | None = None, is_service: bool = False) -> Scooter:
        """
        Create a new scooter instance from the provided data. Or update an existing scooter's data.
        
        Args:
            old_scooter (Scooter | None): Existing scooter to prefill values from, or None.
            is_service (bool): If A service engineer calls then True, skip some input prompts and use defaults.
        
        Returns:
            Scooter: A new Scooter instance.
        """
        # Clear a row for readability
        print("")
        if old_scooter is None and is_service:
            raise ValueError("Cannot service a scooter without old scooter data.")

        # Brand
        while True:
            if is_service:
                brand = old_scooter.brand_plain
                print("Brand: " + old_scooter.brand_plain)
                break

            print("")
            if old_scooter != None:
                print(f"Old scooter brand: {old_scooter.brand_plain}")

            brand = input("Enter scooter brand (2-30 chars): ")
            valid, msg = validate_brand(brand)
            if valid:
                break
            else:
                print(f"Invalid brand: {msg}")

        # Model
        while True:
            if is_service:
                model = old_scooter.model_plain
                print("Model: " + old_scooter.model_plain)
                break
            
            print("")
            if old_scooter != None:
                print(f"Old scooter model: {old_scooter.model_plain}")

            model = input("Enter scooter model (1-30 chars): ")
            valid, msg = validate_model(model)
            if valid:
                break
            else:
                print(f"Invalid model: {msg}")

        # Serial Number
        while True:
            if is_service:
                serial_number = old_scooter.serial_number_plain
                print("Serial Number: " + old_scooter.serial_number_plain)
                break
            
            print("")
            if old_scooter != None:
                print(f"Old scooter serial number: {old_scooter.serial_number_plain}")

            serial_number = input("Enter serial number (10-17 chars): ")
            valid, msg = validate_serial_number(serial_number)
            if valid:
                break
            else:
                print(f"Invalid serial number: {msg}")

        # Top Speed
        while True:
            if is_service:
                top_speed = old_scooter.top_speed
                print("Top Speed: " + str(old_scooter.top_speed) + " km/h")
                break
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter top speed: {old_scooter.top_speed} km/h")

                top_speed = float(input(f"Enter top speed ({TOP_SPEED_MIN}-{TOP_SPEED_MAX} km/h): "))
                if TOP_SPEED_MIN <= top_speed <= TOP_SPEED_MAX:
                    break
                else:
                    print(f"Top speed must be between {TOP_SPEED_MIN} and {TOP_SPEED_MAX} km/h.")
            except ValueError:
                print("Please enter a valid number for top speed.")

        # Battery Capacity
        while True:
            if is_service:
                battery_capacity = old_scooter.battery_capacity
                print("Battery Capacity: " + str(old_scooter.battery_capacity) + " Wh")
                break
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter battery capacity: {old_scooter.battery_capacity} Wh")

                battery_capacity = float(input(f"Enter battery capacity (Wh, max {BATTERY_CAP_MAX}): "))
                if 0 < battery_capacity <= BATTERY_CAP_MAX:
                    break
                else:
                    #print("\033[3A", end="")
                    print(f"Battery capacity must be between 1 and {BATTERY_CAP_MAX} Wh.")
            except ValueError:
                #print("\033[3A", end="")
                print("Please enter a valid number for battery capacity.")

        # State of Charge
        while True:
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter state of charge: {old_scooter.state_of_charge}%")

                state_of_charge = float(input("Enter state of charge (0-100): "))
                if 0 <= state_of_charge <= 100:
                    break
                else:
                    #print("\033[3A", end="")
                    print("State of charge must be between 0 and 100.")
            except ValueError:
                #print("\033[3A", end="")
                print("Please enter a valid number for state of charge.")

        # Target SOC Min
        while True:
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter target SOC min: {old_scooter.target_soc_min}%")

                target_soc_min = float(input("Enter target minimum state of charge (0-100): "))
                if 0 <= target_soc_min <= 100:
                    break
                else:
                    print("Target SOC min must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for target SOC min.")

        # Target SOC Max
        while True:
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter target SOC max: {old_scooter.target_soc_max}%")

                target_soc_max = float(input("Enter target maximum state of charge, must be bigger than minimum state of charge (0-100): "))
                if 0 <= target_soc_max <= 100 and target_soc_max > target_soc_min:
                    break
                else:
                    print("Target SOC max must be between 0 and 100 and >= target SOC min.")
            except ValueError:
                print("Please enter a valid number for target SOC max.")

        # Location Latitude
        while True:
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter location latitude: {old_scooter.location_lat}")

                location_lat = float(input("Enter location latitude (-90 to 90): "))
                if -90 <= location_lat <= 90:
                    break
                else:
                    print("Latitude must be between -90 and 90.")
            except ValueError:
                print("Please enter a valid number for latitude.")

        # Location Longitude
        while True:
            try:
                print("")
                if old_scooter != None:
                    print(f"Old scooter location longitude: {old_scooter.location_lon}")

                location_lon = float(input("Enter location longitude (-180 to 180): "))
                if -180 <= location_lon <= 180:
                    break
                else:
                    print("Longitude must be between -180 and 180.")
            except ValueError:
                print("Please enter a valid number for longitude.")
        
        # Optional: Mileage
        while True:
            print("")
            if old_scooter != None:
                print(f"Old scooter mileage: {old_scooter.mileage} km")

            mileage_input = input(f"Enter mileage (km, max {MILEAGE_MAX}, default 0): ")
            if not mileage_input:
                mileage = 0.0
                break
            try:
                mileage = float(mileage_input)
                if 0 <= mileage <= MILEAGE_MAX:
                    break
                else:
                    print(f"Mileage must be between 0 and {MILEAGE_MAX}.")
            except ValueError:
                print("Please enter a valid number for mileage.")

        # Optional: Out of Service
        while True:
            print("")
            if old_scooter != None:
                print(f"Old scooter out of service: {'Yes' if old_scooter.out_of_service else 'No'}")

            out_of_service_input = input("Is the scooter out of service? (y/n): ")
            if out_of_service_input in ["y", "n"]:
                out_of_service = out_of_service_input == "y"
                break
            print("Invalid format (y/n).")

        # Optional: Last Maintenance Date
        print("")
        if old_scooter != None:
            print(f"Old scooter last maintenance date: {old_scooter.last_maint_date}")

        while True:
            print("")
            last_maint_date = input("Enter last maintenance date (YYYY-MM-DD, default today): ")
            if last_maint_date == "":
                last_maint_date = datetime.date.today().strftime('%Y-%m-%d')
                break
            else:
                valid, msg = validate_scooter_date(last_maint_date, "Last maintenance date")
                if valid:
                    break
                else:
                    print(f"Invalid date: {msg}")
            
        
        # Create new scooter instance
        return Scooter(
            scooter_id=None if old_scooter is None else old_scooter.scooter_id,  # If no old_scooter, will be set by the database
            brand=brand,
            model=model,
            serial_number=serial_number,
            top_speed=top_speed,
            battery_capacity=battery_capacity,
            state_of_charge=state_of_charge,
            target_soc_min=target_soc_min,
            target_soc_max=target_soc_max,
            location_lat=location_lat,
            location_lon=location_lon,
            mileage=mileage,
            out_of_service=out_of_service,
            last_maint_date=last_maint_date
        )
