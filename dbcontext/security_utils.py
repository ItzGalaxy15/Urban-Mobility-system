"""
Security Utilities Module

This module provides core security features for the Urban Mobility System:
- Session Management: Handles user sessions with timeouts and secure session IDs
- Rate Limiting: Prevents brute force attacks by limiting login attempts
- Input Sanitization: Protects against XSS and injection attacks

The module uses in-memory storage for sessions and login attempts.
In a production environment, these should be moved to a secure, distributed storage.
"""

from collections import defaultdict
from datetime import datetime, timedelta
import os
from typing import Optional

# Session management
SESSION_TIMEOUT = 30 * 60  # 30 minutes
active_sessions = {}

def create_session(user_id: int) -> str:
    """
    Create a new secure session for a user.
    
    Args:
        user_id: The ID of the user to create a session for
        
    Returns:
        str: A secure random session ID
        
    The session ID is a 32-byte random hex string, providing 256 bits of entropy.
    """
    session_id = os.urandom(32).hex()
    active_sessions[session_id] = {
        'user_id': user_id,
        'created_at': datetime.now()
    }
    return session_id

def validate_session(session_id: str) -> Optional[int]:
    """
    Validate a session and return the associated user ID if valid.
    
    Args:
        session_id: The session ID to validate
        
    Returns:
        Optional[int]: The user ID if the session is valid, None otherwise
        
    Sessions are automatically invalidated after SESSION_TIMEOUT minutes.
    """
    if session_id not in active_sessions:
        return None
    
    session = active_sessions[session_id]
    if (datetime.now() - session['created_at']).total_seconds() > SESSION_TIMEOUT:
        del active_sessions[session_id]
        return None
    
    return session['user_id']

def invalidate_session(session_id: str) -> None:
    """
    Invalidate a session, effectively logging out the user.
    
    Args:
        session_id: The session ID to invalidate
    """
    if session_id in active_sessions:
        del active_sessions[session_id]

# Rate limiting
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 15  # minutes

def check_login_attempts(username: str) -> bool:
    """
    Check if a user has exceeded the maximum number of login attempts.
    
    Args:
        username: The username to check
        
    Returns:
        bool: True if the user can attempt to login, False if they are locked out
        
    Users are locked out for LOCKOUT_TIME minutes after MAX_ATTEMPTS failed attempts.
    """
    now = datetime.now()
    attempts = login_attempts[username]
    # Remove old attempts
    attempts = [t for t in attempts if now - t < timedelta(minutes=LOCKOUT_TIME)]
    login_attempts[username] = attempts
    
    if len(attempts) >= MAX_ATTEMPTS:
        return False
    return True

def record_login_attempt(username: str, success: bool) -> None:
    """
    Record a login attempt for rate limiting purposes.
    
    Args:
        username: The username that attempted to login
        success: Whether the login attempt was successful
        
    Successful logins clear the attempt history for the user.
    """
    if not success:
        login_attempts[username].append(datetime.now())
    else:
        # Clear attempts on successful login
        login_attempts[username] = []

def sanitize_input(value: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        value: The input string to sanitize
        
    Returns:
        str: The sanitized input string
        
    Currently removes < and > characters to prevent basic XSS attacks.
    In a production environment, this should be enhanced with more comprehensive
    sanitization based on the specific use case.
    """
    if not value:
        return value
    # Remove potentially dangerous characters
    return value.replace('<', '').replace('>', '').strip() 