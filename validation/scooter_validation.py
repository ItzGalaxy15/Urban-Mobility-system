from typing import Optional, Tuple
from models.scooter import (
    BRAND_RE, MODEL_RE, SERIAL_RE, DATE_RE,
    TOP_SPEED_MIN, TOP_SPEED_MAX, BATTERY_CAP_MAX, MILEAGE_MAX
)

def validate_float_input(prompt: str, min_val: float, max_val: float) -> float:
    """
    Validates and converts a float input within specified range.
    
    Args:
        prompt: The input prompt to display
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        float: Validated float value
    """
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Value must be between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def validate_text_input(prompt: str, pattern, error_msg: str) -> str:
    """
    Validates text input against a regex pattern.
    
    Args:
        prompt: The input prompt to display
        pattern: Regex pattern to validate against
        error_msg: Error message to display if validation fails
        
    Returns:
        str: Validated text input
    """
    while True:
        value = input(prompt)
        if pattern.fullmatch(value):
            return value
        print(error_msg)

def validate_date_input(prompt: str) -> Optional[str]:
    """
    Validates date input in YYYY-MM-DD format.
    
    Args:
        prompt: The input prompt to display
        
    Returns:
        Optional[str]: Validated date string or None if empty
    """
    while True:
        value = input(prompt)
        if not value:  # Allow empty input for optional date
            return None
        if DATE_RE.fullmatch(value):
            return value
        print("Date must be in YYYY-MM-DD format")

def validate_scooter_inputs() -> Tuple[dict, bool]:
    """
    Validates all scooter input fields according to the model requirements.
    
    Returns:
        Tuple[dict, bool]: (scooter_data dictionary, success status)
    """
    try:
        scooter_data = {
            "brand": validate_text_input(
                "Brand (2-30 alphanumeric chars): ",
                BRAND_RE,
                "Brand must be 2-30 alphanumeric characters"
            ),
            "model": validate_text_input(
                "Model (1-30 alphanumeric chars): ",
                MODEL_RE,
                "Model must be 1-30 alphanumeric characters"
            ),
            "serial_number": validate_text_input(
                "Serial Number (10-17 alphanumeric chars): ",
                SERIAL_RE,
                "Serial number must be 10-17 alphanumeric characters"
            ),
            "top_speed": validate_float_input(
                f"Top Speed ({TOP_SPEED_MIN}-{TOP_SPEED_MAX} km/h): ",
                TOP_SPEED_MIN,
                TOP_SPEED_MAX
            ),
            "battery_capacity": validate_float_input(
                f"Battery Capacity (0-{BATTERY_CAP_MAX} Wh): ",
                0,
                BATTERY_CAP_MAX
            ),
            "state_of_charge": validate_float_input(
                "State of Charge (0-100%): ",
                0,
                100
            ),
            "target_soc_min": validate_float_input(
                "Target SOC Min (0-100%): ",
                0,
                100
            ),
            "target_soc_max": validate_float_input(
                "Target SOC Max (0-100%): ",
                0,
                100
            ),
            "location_lat": validate_float_input(
                "Location Lat (-90 to 90): ",
                -90,
                90
            ),
            "location_lon": validate_float_input(
                "Location Lon (-180 to 180): ",
                -180,
                180
            ),
            "mileage": validate_float_input(
                f"Mileage (0-{MILEAGE_MAX} km): ",
                0,
                MILEAGE_MAX
            ),
            "out_of_service": input("Out of Service (y/n): ").lower() == 'y',
            "last_maint_date": validate_date_input("Last Maintenance Date (YYYY-MM-DD, optional): ")
        }
        
        # Validate target SOC range
        if scooter_data["target_soc_min"] >= scooter_data["target_soc_max"]:
            print("Error: Target SOC Min must be less than Target SOC Max")
            return None, False
            
        return scooter_data, True
        
    except KeyboardInterrupt:
        print("\nScooter addition cancelled")
        return None, False
    except Exception as e:
        print(f"Error in validation: {str(e)}")
        return None, False 