
# namespace: controllers

from services.traveller_service import traveller_service
from utils.role_utils import require_role
from controllers.session import UserSession


class TravellerController:
    """Controller layer for Traveller operations (add/update/delete/search).
    Only *super* and *system_admin* roles can invoke these endpoints.
    """
    @staticmethod
    @require_role("system_admin", "super")
    def add_traveller_controller(current_user_id: int, **traveller_fields):
        """Create a traveller record."""
        return traveller_service.add_traveller(**traveller_fields)

    @staticmethod
    @require_role("system_admin", "super")
    def update_traveller_controller(current_user_id: int, traveller_id: int, **updates):
        """Modify an existing traveller record."""
        return traveller_service.update_traveller(traveller_id, **updates)

    @staticmethod
    @require_role("system_admin", "super")
    def delete_traveller_controller(current_user_id: int, traveller_id: int):
        """Remove a traveller record."""
        return traveller_service.delete_traveller(traveller_id)

    @staticmethod
    @require_role("system_admin", "super")
    def search_travellers_controller(current_user_id: int, key: str, limit: int = 50):
        """Find travellers via partial-text search."""
        return traveller_service.search_travellers(key, limit)

    # # methods without role checks (e.g. internal use / tests)
    # @staticmethod
    # def add_traveller(**traveller_fields):
    #     return traveller_service.add_traveller(**traveller_fields)

    # @staticmethod
    # def update_traveller(traveller_id: int, **updates):
    #     return traveller_service.update_traveller(traveller_id, **updates)

    # @staticmethod
    # def delete_traveller(traveller_id: int):
    #     return traveller_service.delete_traveller(traveller_id)

    # @staticmethod
    # def search_travellers(key: str, limit: int = 50):
    #     return traveller_service.search_travellers(key, limit)



traveller_controller = TravellerController()
