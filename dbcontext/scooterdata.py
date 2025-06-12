import sqlite3
from utils.crypto_utils import encrypt, decrypt 
from models.scooter import Scooter
from datetime import datetime
from typing import Optional, Tuple, Union

def add_scooter(scooter: Scooter) -> Tuple[bool, str]:
    """
    Add a scooter to the database. The scooter object should already have encrypted data.
    
    Args:
        scooter: Scooter object with encrypted brand, model, and serial_number
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        conn = sqlite3.connect('urban_mobility.db')
        c = conn.cursor()
        
        # Check if serial number already exists
        c.execute('SELECT serial_number FROM Scooter WHERE serial_number = ?', (scooter.serial_number,))
        if c.fetchone():
            return False, "A scooter with this serial number already exists"
            
        c.execute('''
            INSERT INTO Scooter (
                brand, model, serial_number, 
                top_speed, battery_capacity, state_of_charge, 
                target_soc_min, target_soc_max, location_lat, 
                location_lon, out_of_service, mileage, 
                last_maint_date, in_service_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scooter.brand,
            scooter.model,
            scooter.serial_number,
            scooter.top_speed,
            scooter.battery_capacity,
            scooter.state_of_charge,
            scooter.target_soc_min,
            scooter.target_soc_max,
            scooter.location_lat,
            scooter.location_lon,
            scooter.out_of_service,
            scooter.mileage,
            scooter.last_maint_date,
            scooter.in_service_date
        ))
        conn.commit()
        return True, "Scooter added successfully"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()
    
def add_scooter_from_params(
    brand: str,
    model: str,
    serial_number: str,
    top_speed: Union[float, str],
    battery_capacity: Union[float, str],
    state_of_charge: Union[float, str],
    target_soc_min: Union[float, str],
    target_soc_max: Union[float, str],
    location_lat: Union[float, str],
    location_lon: Union[float, str],
    *,
    mileage: Union[float, str] = 0.0,
    out_of_service: Union[bool, str] = False,
    last_maint_date: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Add a scooter to the database using individual parameters.
    This is a wrapper around the Scooter model for backward compatibility.
    
    Args:
        brand: Scooter brand (2-30 alphanumeric chars)
        model: Scooter model (1-30 alphanumeric chars)
        serial_number: Unique serial number (10-17 alphanumeric chars)
        top_speed: Maximum speed in km/h (5-50)
        battery_capacity: Battery capacity in Wh (0-5000)
        state_of_charge: Current battery charge percentage (0-100)
        target_soc_min: Minimum target state of charge (0-100)
        target_soc_max: Maximum target state of charge (0-100)
        location_lat: Latitude (-90 to 90)
        location_lon: Longitude (-180 to 180)
        mileage: Current mileage in km (0-1,000,000)
        out_of_service: Whether the scooter is out of service
        last_maint_date: Last maintenance date (YYYY-MM-DD)
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Convert numeric parameters to float
        numeric_params = {
            'top_speed': top_speed,
            'battery_capacity': battery_capacity,
            'state_of_charge': state_of_charge,
            'target_soc_min': target_soc_min,
            'target_soc_max': target_soc_max,
            'location_lat': location_lat,
            'location_lon': location_lon,
            'mileage': mileage
        }
        
        for param_name, value in numeric_params.items():
            try:
                numeric_params[param_name] = float(value)
            except (ValueError, TypeError):
                return False, f"Invalid {param_name}: must be a number"
        
        # Convert boolean parameter
        try:
            out_of_service = bool(out_of_service)
        except (ValueError, TypeError):
            return False, "Invalid out_of_service: must be a boolean"
            
        scooter = Scooter(
            brand=brand,
            model=model,
            serial_number=serial_number,
            top_speed=numeric_params['top_speed'],
            battery_capacity=numeric_params['battery_capacity'],
            state_of_charge=numeric_params['state_of_charge'],
            target_soc_min=numeric_params['target_soc_min'],
            target_soc_max=numeric_params['target_soc_max'],
            location_lat=numeric_params['location_lat'],
            location_lon=numeric_params['location_lon'],
            mileage=numeric_params['mileage'],
            out_of_service=out_of_service,
            last_maint_date=last_maint_date
        )
        return add_scooter(scooter)
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


