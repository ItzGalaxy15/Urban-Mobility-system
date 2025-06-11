"""
User Data Access Module

This module provides secure access to user data in the database.
It includes:
- User creation and management
- Password verification
- User lookup by ID or username
- Password updates
- Input sanitization

All sensitive data is encrypted before storage and decrypted when retrieved.
"""

import sqlite3
from dbcontext.crypto_utils import encrypt, hash_password, decrypt, check_password
from dbcontext.security_utils import sanitize_input
from dbcontext.dbcontext import execute_query, DatabaseError

def add_user(username, password, first_name, last_name, role):
    """
    Add a new user to the database with proper security measures.
    
    Args:
        username: The user's username
        password: The user's password (will be hashed)
        first_name: The user's first name
        last_name: The user's last name
        role: The user's role in the system
        
    Raises:
        DatabaseError: If the user cannot be added to the database
        
    Security features:
    - Input sanitization
    - Password hashing
    - Data encryption
    """
    try:
        # Sanitize inputs
        username = sanitize_input(username)
        first_name = sanitize_input(first_name)
        last_name = sanitize_input(last_name)
        role = sanitize_input(role)

        execute_query('''
            INSERT INTO User (username, password_hash, first_name, last_name, registration_date, role)
            VALUES (?, ?, ?, ?, datetime('now'), ?)
        ''', (
            encrypt(username),
            hash_password(password),
            encrypt(first_name),
            encrypt(last_name),
            role
        ))
    except DatabaseError as e:
        raise DatabaseError(f"Failed to add user: {str(e)}")

def get_user_by_id(user_id):
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        dict: User data including decrypted fields, or None if not found
        
    Raises:
        DatabaseError: If the user cannot be retrieved
        
    Note:
        All encrypted fields are automatically decrypted before being returned.
    """
    try:
        cursor = execute_query('SELECT user_id, username, first_name, last_name, role FROM User WHERE user_id=?', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "user_id": row[0],
                "username": decrypt(row[1]),
                "first_name": decrypt(row[2]) if row[2] is not None else None,
                "last_name": decrypt(row[3]) if row[3] is not None else None,
                "role": row[4]
            }
        return None
    except DatabaseError as e:
        raise DatabaseError(f"Failed to get user by ID: {str(e)}")

def verify_user_password(user_id, password):
    """
    Verify a user's password.
    
    Args:
        user_id: The ID of the user
        password: The password to verify
        
    Returns:
        bool: True if the password is correct, False otherwise
        
    Raises:
        DatabaseError: If the password cannot be verified
        
    Security:
        Uses bcrypt for secure password verification
    """
    try:
        cursor = execute_query('SELECT password_hash FROM User WHERE user_id=?', (user_id,))
        row = cursor.fetchone()
        if row:
            return check_password(password, row[0])
        return False
    except DatabaseError as e:
        raise DatabaseError(f"Failed to verify password: {str(e)}")

def get_user_by_username(username):
    """
    Retrieve a user by their username.
    
    Args:
        username: The username to search for
        
    Returns:
        dict: User data including decrypted fields, or None if not found
        
    Raises:
        DatabaseError: If the user cannot be retrieved
        
    Security:
        - Input sanitization
        - Encrypted username comparison
    """
    try:
        # Sanitize username
        username = sanitize_input(username)
        
        cursor = execute_query('SELECT user_id, username, first_name, last_name, role FROM User')
        users = cursor.fetchall()
        for row in users:
            if decrypt(row[1]) == username:
                return {
                    "user_id": row[0],
                    "username": decrypt(row[1]),
                    "first_name": decrypt(row[2]) if row[2] is not None else None,
                    "last_name": decrypt(row[3]) if row[3] is not None else None,
                    "role": row[4]
                }
        return None
    except DatabaseError as e:
        raise DatabaseError(f"Failed to get user by username: {str(e)}")

def update_password(user_id, new_password):
    """
    Update a user's password.
    
    Args:
        user_id: The ID of the user
        new_password: The new password to set
        
    Raises:
        DatabaseError: If the password cannot be updated
        
    Security:
        - Password is hashed before storage
        - Uses bcrypt for secure hashing
    """
    try:
        hashed = hash_password(new_password)
        execute_query('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
    except DatabaseError as e:
        raise DatabaseError(f"Failed to update password: {str(e)}")
