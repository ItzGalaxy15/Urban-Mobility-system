"""
Session Controller Module

This module handles user authentication and session management for the Urban Mobility System.
It provides a secure way to manage user sessions, including login, logout, and session validation.

The module integrates with the security utilities to provide:
- Rate-limited login attempts
- Secure session management
- Input sanitization
- Proper error handling
"""

from dbcontext.userdata import get_user_by_username, verify_user_password
from dbcontext.security_utils import (
    create_session,
    validate_session,
    invalidate_session,
    check_login_attempts,
    record_login_attempt,
    sanitize_input
)

class Session:
    """
    Manages user sessions and authentication.
    
    This class provides methods for:
    - User login with rate limiting
    - Session validation
    - Secure logout
    - Session state management
    
    Attributes:
        session_id (str): The current session ID if logged in
        user (dict): The current user's data if logged in
    """
    
    def __init__(self):
        """Initialize a new session with no user logged in."""
        self.session_id = None
        self.user = None

    def login(self, username: str, password: str) -> bool:
        """
        Attempt to log in a user.
        
        Args:
            username: The username to login with
            password: The password to verify
            
        Returns:
            bool: True if login successful, False otherwise
            
        Raises:
            SecurityError: If the user is locked out due to too many attempts
        """
        # Sanitize input
        username = sanitize_input(username)
        
        # Check rate limiting
        if not check_login_attempts(username):
            raise SecurityError("Too many login attempts. Please try again later.")
        
        # Get user and verify password
        user = get_user_by_username(username)
        if user and verify_user_password(user["user_id"], password):
            # Create session
            self.session_id = create_session(user["user_id"])
            self.user = user
            record_login_attempt(username, True)
            return True
        
        record_login_attempt(username, False)
        return False

    def logout(self) -> None:
        """
        Log out the current user and invalidate their session.
        
        This method:
        1. Invalidates the current session
        2. Clears the session ID
        3. Clears the user data
        """
        if self.session_id:
            invalidate_session(self.session_id)
            self.session_id = None
            self.user = None

    def is_valid(self) -> bool:
        """
        Check if the current session is valid.
        
        Returns:
            bool: True if the session is valid and not expired, False otherwise
            
        This method:
        1. Checks if there is an active session
        2. Validates the session hasn't expired
        3. Updates the user data if the session is invalid
        """
        if not self.session_id:
            return False
        user_id = validate_session(self.session_id)
        if not user_id:
            self.user = None
            return False
        return True

class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass
