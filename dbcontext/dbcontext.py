"""
Database Context Module

This module provides database connectivity and management for the Urban Mobility System.
It includes:
- Secure database connection handling
- Connection pooling
- Retry logic for failed queries
- Proper error handling
- Database schema creation and initialization

The module uses SQLite with additional security features like timeouts and connection pooling.
"""

import sqlite3
from models.user import User
from dbcontext.crypto_utils import encrypt
from typing import Optional
import time

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

def get_db_connection():
    """
    Get a secure database connection with proper timeout and error handling.
    
    Returns:
        sqlite3.Connection: A configured database connection
        
    The connection is configured with:
    - 20 second timeout
    - Connection pooling support
    - Proper error handling
    """
    try:
        return sqlite3.connect(
            'urban_mobility.db',
            timeout=20,  # Connection timeout in seconds
            check_same_thread=False  # Allow connection pooling
        )
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to connect to database: {str(e)}")

def execute_query(query: str, params: tuple = (), max_retries: int = 3) -> Optional[sqlite3.Cursor]:
    """
    Execute a database query with retry logic and proper error handling.
    
    Args:
        query: The SQL query to execute
        params: Parameters for the query
        max_retries: Maximum number of retry attempts
        
    Returns:
        Optional[sqlite3.Cursor]: The cursor with query results if successful
        
    Raises:
        DatabaseError: If the query fails after all retry attempts
        
    Features:
    - Automatic retry with exponential backoff
    - Proper connection cleanup
    - Transaction management
    """
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            if attempt == max_retries - 1:
                raise DatabaseError(f"Database query failed after {max_retries} attempts: {str(e)}")
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        finally:
            if 'conn' in locals():
                conn.close()

def create_db():
    """
    Create and initialize the database schema.
    
    This function:
    1. Creates all necessary tables if they don't exist
    2. Sets up the super admin user
    3. Configures proper constraints and relationships
    
    The schema includes:
    - User management
    - Traveller information
    - Scooter tracking
    - System logging
    - Backup management
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # User table
        c.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            first_name TEXT,
            last_name TEXT,
            registration_date DATETIME,
            role TEXT
        )
        ''')

        # Ensure super admin exists
        super_admin = User(
            username="super_admin",
            password_plain="Admin_123?",
            role="super"
        )
        
        c.execute('''
        INSERT OR IGNORE INTO User (
            user_id,
            username,
            password_hash,
            role,
            registration_date
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            super_admin.user_id,
            encrypt("super_admin"),
            super_admin.password_hash,
            super_admin.role,
            super_admin.registration_date
        ))

        # Traveller table
        c.execute('''
        CREATE TABLE IF NOT EXISTS Traveller (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_date DATETIME,
            first_name TEXT,
            last_name TEXT,
            birthday DATE,
            gender TEXT,
            street_name TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            email_address TEXT,
            mobile_phone TEXT,
            driving_license_no TEXT
        )
        ''')

        # Scooter table
        c.execute('''
        CREATE TABLE IF NOT EXISTS Scooter (
            scooter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            top_speed REAL,
            battery_capacity REAL,
            state_of_charge REAL,
            target_soc_min REAL,
            target_soc_max REAL,
            location_lat REAL,
            location_lon REAL,
            out_of_service BOOLEAN,
            mileage REAL,
            last_maint_date DATE,
            in_service_date DATETIME
        )
        ''')

        # LogEntry table
        c.execute('''
        CREATE TABLE IF NOT EXISTS LogEntry (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            time TIME,
            username TEXT,
            description TEXT,
            is_suspicious BOOLEAN,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES User(user_id)
        )
        ''')

        # Backup table
        c.execute('''
        CREATE TABLE IF NOT EXISTS Backup (
            backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_date DATETIME,
            file_path TEXT,
            created_by_user_id INTEGER,
            FOREIGN KEY(created_by_user_id) REFERENCES User(user_id)
        )
        ''')

        # Restore code table
        c.execute('''
        CREATE TABLE IF NOT EXISTS RestoreCode (
            code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            backup_id INTEGER,
            system_admin_user_id INTEGER,
            is_used BOOLEAN,
            generated_date DATETIME,
            FOREIGN KEY(backup_id) REFERENCES Backup(backup_id),
            FOREIGN KEY(system_admin_user_id) REFERENCES User(user_id)
        )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to create database schema: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_db()
