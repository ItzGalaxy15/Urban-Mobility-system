from typing import Optional, Dict, Any
from models.scooter import Scooter
from models.user import User
from services.scooterdata import ScooterData
from utils.role_utils import require_role

class ScooterController:
    def __init__(self, db_path: str):
        self.scooter_data = ScooterData(db_path)
        
    @require_role("system_admin")
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
    
    # Version 1: Only service engineer can call
    @require_role("service_engineer")
    def update_scooter_service_engineer(self, user: User, scooter_id: int, update_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Update specific scooter attributes.
        Only service engineer can perform this action, and only certain fields are editable.
        """
        if user.role != "service_engineer":
            return False, "Unauthorized: Only service engineer can use this function"

        # Only allow these fields to be updated by service engineer
        allowed_fields = {
            "state_of_charge",
            "mileage",
            "out_of_service",
            "last_maint_date"
        }

        try:
            scooter = self.scooter_data.get_scooter_by_id(scooter_id)
            if not scooter:
                return False, "Scooter not found"

            for key, value in update_data.items():
                if key in allowed_fields and hasattr(scooter, key):
                    setattr(scooter, key, value)

            if self.scooter_data.update_scooter(scooter):
                return True, f"Scooter {scooter_id} updated successfully"
            return False, "Failed to update scooter in database"

        except KeyError as e:
            return False, f"Invalid field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid input: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    # Version 2: Everyone except service engineer can call
    @require_role("system_admin")
    def update_scooter(self, user: User, scooter_id: int, update_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Update an existing scooter's information.
        All roles except service engineer can perform this action.
        """
        if user.role == "service_engineer":
            return False, "Unauthorized: Service engineer cannot use this function"

        try:
            scooter = self.scooter_data.get_scooter_by_id(scooter_id)
            if not scooter:
                return False, "Scooter not found"

            for key, value in update_data.items():
                if hasattr(scooter, key):
                    setattr(scooter, key, value)

            if self.scooter_data.update_scooter(scooter):
                return True, f"Scooter {scooter_id} updated successfully"
            return False, "Failed to update scooter in database"

        except KeyError as e:
            return False, f"Invalid field: {str(e)}"
        except ValueError as e:
            return False, f"Invalid input: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
        
    @require_role("system_admin")
    def delete_scooter(self, user: User, scooter_id: int) -> tuple[bool, str]:
        """
        Delete a scooter from the system.
        Only super admin and system admin can perform this action.
        
        Args:
            user: The user attempting to delete the scooter
            scooter_id: The ID of the scooter to delete
            
        Returns:
            tuple[bool, str]: (success, message)
        """
        # Role-based access control
        if user.role not in {"super", "system_admin"}:
            return False, "Unauthorized: Only super admin and system admin can delete scooters"

        if self.scooter_data.delete_scooter(scooter_id):
            return True, f"Scooter {scooter_id} deleted successfully"
        return False, "Failed to delete scooter from database"
