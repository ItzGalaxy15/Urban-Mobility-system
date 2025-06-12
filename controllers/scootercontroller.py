from dbcontext.scooterdata import add_scooter
from utils.role_utils import require_role
from models.scooter import Scooter
from typing import Tuple, Union

def validate_scooter_input(
    brand: str,
    model: str,
    serial_number: str,
    top_speed: Union[str, float],
    battery_capacity: Union[str, float],
    state_of_charge: Union[str, float],
    target_soc_min: Union[str, float],
    target_soc_max: Union[str, float],
    location_lat: Union[str, float],
    location_lon: Union[str, float],
    out_of_service: Union[str, bool],
    mileage: Union[str, float],
    last_maint_date: str
) -> Tuple[bool, Union[str, Tuple]]:
    """
    Validates scooter input data and converts to appropriate types.
    Returns (success, result) where result is either an error message or a tuple of validated data.
    """
    try:
        # Convert numeric inputs
        numeric_inputs = {
            'top_speed': top_speed,
            'battery_capacity': battery_capacity,
            'state_of_charge': state_of_charge,
            'target_soc_min': target_soc_min,
            'target_soc_max': target_soc_max,
            'location_lat': location_lat,
            'location_lon': location_lon,
            'mileage': mileage
        }
        
        for name, value in numeric_inputs.items():
            try:
                numeric_inputs[name] = float(value)
            except (ValueError, TypeError):
                return False, f"Invalid {name}: must be a number"
        
        # Convert boolean input
        if isinstance(out_of_service, str):
            if out_of_service == "1":
                out_of_service = True
            elif out_of_service == "2":
                out_of_service = False
            else:
                return False, "Invalid out_of_service: must be 1 (Yes) or 2 (No)"
        
        # Create Scooter object to validate all inputs
        scooter = Scooter(
            brand=brand,
            model=model,
            serial_number=serial_number,
            top_speed=numeric_inputs['top_speed'],
            battery_capacity=numeric_inputs['battery_capacity'],
            state_of_charge=numeric_inputs['state_of_charge'],
            target_soc_min=numeric_inputs['target_soc_min'],
            target_soc_max=numeric_inputs['target_soc_max'],
            location_lat=numeric_inputs['location_lat'],
            location_lon=numeric_inputs['location_lon'],
            out_of_service=out_of_service,
            mileage=numeric_inputs['mileage'],
            last_maint_date=last_maint_date
        )
        
        return True, (brand, model, serial_number, numeric_inputs['top_speed'],
                     numeric_inputs['battery_capacity'], numeric_inputs['state_of_charge'],
                     numeric_inputs['target_soc_min'], numeric_inputs['target_soc_max'],
                     numeric_inputs['location_lat'], numeric_inputs['location_lon'],
                     out_of_service, numeric_inputs['mileage'], last_maint_date)
    except ValueError as e:
        return False, str(e)

@require_role("system_admin")
def add_scooter_controller(brand, model, serial_number, top_speed, battery_capacity, 
                          state_of_charge, target_soc_min, target_soc_max, location_lat, 
                          location_lon, out_of_service, mileage, last_maint_date):
    """
    Controller function to add a new scooter.
    Handles input validation and database operations.
    """
    # Validate input
    success, result = validate_scooter_input(
        brand, model, serial_number, top_speed, battery_capacity,
        state_of_charge, target_soc_min, target_soc_max, location_lat,
        location_lon, out_of_service, mileage, last_maint_date
    )
    
    if not success:
        return False, result
        
    try:
        # Create and add scooter
        scooter = Scooter(*result)
        add_scooter(scooter)
        return True, "Scooter added successfully."
    except ValueError as e:
        return False, str(e)