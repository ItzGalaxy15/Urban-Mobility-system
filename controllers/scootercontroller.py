from typing import Optional, Dict, Any
from models.scooter import Scooter
from models.user import User
from dbcontext.scooterdata import ScooterData
from utils.role_utils import requires_role

class ScooterController:
    def __init__(self, db_path: str):
        self.scooter_data = ScooterData(db_path)
        
    @requires_role("system_admin", "super")
    def add_scooter(self, user: User, scooter_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Add a new scooter to the system.
        Only super admin and system admin can perform this action.
        
        Args:
            user: The user attempting to add the scooter
            scooter_data: Dictionary containing scooter information
            
        Returns:
            tuple[bool, str]: (success, message)
        """
        # Role-based access control
        if user.role not in {"super", "system_admin"}:
            return False, "Unauthorized: Only super admin and system admin can add scooters"

        try:
            # Create scooter object (this will validate all inputs)
            scooter = Scooter(
                brand=scooter_data["brand"],
                model=scooter_data["model"],
                serial_number=scooter_data["serial_number"],
                top_speed=float(scooter_data["top_speed"]),
                battery_capacity=float(scooter_data["battery_capacity"]),
                state_of_charge=float(scooter_data["state_of_charge"]),
                target_soc_min=float(scooter_data["target_soc_min"]),
                target_soc_max=float(scooter_data["target_soc_max"]),
                location_lat=float(scooter_data["location_lat"]),
                location_lon=float(scooter_data["location_lon"]),
                mileage=float(scooter_data.get("mileage", 0.0)),
                out_of_service=bool(scooter_data.get("out_of_service", False)),
                last_maint_date=scooter_data.get("last_maint_date")
            )

            # Add to database
            if self.scooter_data.add_scooter(scooter):
                return True, f"Scooter {scooter.scooter_id} added successfully"
            return False, "Failed to add scooter to database"

        except KeyError as e:
            return False, f"Missing required field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid input: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def get_scooter(self, user: User, scooter_id: int) -> tuple[Optional[Scooter], str]:
        """
        Retrieve a scooter by ID.
        All authenticated users can view scooters.
        
        Args:
            user: The user requesting the scooter information
            scooter_id: The ID of the scooter to retrieve
            
        Returns:
            tuple[Optional[Scooter], str]: (scooter object or None, message)
        """
        scooter = self.scooter_data.get_scooter_by_id(scooter_id)
        if scooter:
            return scooter, "Scooter retrieved successfully"
        return None, "Scooter not found"
