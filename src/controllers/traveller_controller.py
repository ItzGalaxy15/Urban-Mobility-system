# namespace: controllers

from services.traveller_service import traveller_service
from utils.role_utils import require_role
from services.session_service import session_service
from utils.log_decorator import log_action 


class TravellerController:
    """Controller layer for Traveller operations (add/update/delete/search).
    Only *super* and *system_admin* roles can invoke these endpoints.
    """
    @staticmethod
    @log_action("Add traveller -> {msg}")  
    @require_role("system_admin", "super")
    def add_traveller_controller(current_user_id: int, **traveller_fields):
        """Create a traveller record."""
        return traveller_service.add_traveller(**traveller_fields)

    @staticmethod
    @log_action("Update traveller -> {msg}")
    @require_role("system_admin", "super")
    def update_traveller_controller(current_user_id: int, traveller_id: int, **updates):
        """Modify an existing traveller record."""
        return traveller_service.update_traveller(traveller_id, **updates)

    @staticmethod
    @log_action("Delete traveller -> {msg}") 
    @require_role("system_admin", "super")
    def delete_traveller_controller(current_user_id: int, traveller_id: int):
        """Remove a traveller record."""
        return traveller_service.delete_traveller(traveller_id)

    @staticmethod
    @log_action("Search travellers -> {msg}") 
    @require_role("system_admin", "super")
    def search_travellers_controller(current_user_id: int, key: str, limit: int = 50):
        """Find travellers via partial-text search."""
        return traveller_service.search_travellers(key, limit)


traveller_controller = TravellerController()
