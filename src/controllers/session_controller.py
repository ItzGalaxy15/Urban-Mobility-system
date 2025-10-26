# namespace: controllers

from services.session_service import SessionService
from services.userservice import user_service
from typing import Tuple
from models.user import User

class SessionController:
    """Controller layer for session operations."""
    
    def __init__(self, session_service: SessionService):
        self._session_service = session_service
    
    def login(self, username: str, password: str = None) -> bool:
        """Login authentication flow."""
        return self._session_service.login(username, password)
    
    def logout(self):
        """Logout current user."""
        self._session_service.logout()
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self._session_service.is_authenticated()
    
    def get_current_user(self) -> User:
        """Get current user object."""
        return self._session_service.get_current_user()
    
    def get_current_user_id(self) -> int:
        """Get current user ID."""
        return self._session_service.get_current_user_id()
    
    def get_current_username(self) -> str:
        """Get current username."""
        return self._session_service.get_current_username()
    
    def get_current_role(self) -> str:
        """Get current user role."""
        return self._session_service.get_current_role()
    
    def add_whitelisted_username(self, username: str) -> Tuple[bool, str]:
        """Add username to whitelist."""
        if self._session_service.add_allowed_username(username):
            return True, f"Username '{username}' added to whitelist successfully."
        return False, f"Username '{username}' is already in the whitelist."
    
    def remove_whitelisted_username(self, username: str) -> Tuple[bool, str]:
        """Remove username from whitelist."""
        if self._session_service.remove_allowed_username(username):
            return True, f"Username '{username}' removed from whitelist successfully."
        return False, f"Username '{username}' not found in whitelist."
    
    def add_whitelisted_role(self, role: str) -> Tuple[bool, str]:
        """Add role to whitelist."""
        if self._session_service.add_allowed_role(role):
            return True, f"Role '{role}' added to whitelist successfully."
        return False, f"Role '{role}' is already in the whitelist."
    
    def remove_whitelisted_role(self, role: str) -> Tuple[bool, str]:
        """Remove role from whitelist."""
        if self._session_service.remove_allowed_role(role):
            return True, f"Role '{role}' removed from whitelist successfully."
        return False, f"Role '{role}' not found in whitelist."
    
    def get_whitelist_status(self) -> dict:
        """Get current whitelist configuration."""
        return self._session_service.get_whitelist_status()

# Create global instance
from services.session_service import session_service
session_controller = SessionController(session_service)
