import pytest
import os
import sys
import shutil
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dbcontext.dbcontext import create_db
from services.userservice import UserService
from services.traveller_service import TravellerService
from services.scooterservice import ScooterService
from controllers.session import UserSession

TEST_DB = "test_urban_mobility.db"
TEST_LOG = "test_activity.log"
TEST_SECRET_KEY = "test_secret.key"

@pytest.fixture(scope="function")
def test_db_path():
    """Provide path to test database"""
    return TEST_DB

@pytest.fixture(scope="function", autouse=True)
def setup_test_environment(monkeypatch):
    """Setup clean test environment before each test"""
    # Reset UserSession state before each test to prevent lockout carry-over
    UserSession.reset_session()
    
    # Inject test user service into UserSession
    test_user_service = UserService(TEST_DB)
    UserSession.set_user_service(test_user_service)
    
    # Cleanup test files if they exist from previous runs
    test_files = [TEST_DB, TEST_LOG, TEST_SECRET_KEY]
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass
    
    # Monkey patch create_db to use test database
    import dbcontext.dbcontext
    original_create_db = dbcontext.dbcontext.create_db
    
    def create_test_db():
        conn = sqlite3.connect(TEST_DB)
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
        
        # Traveller table
        c.execute('''
        CREATE TABLE IF NOT EXISTS Traveller (
            traveller_id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_date DATETIME,
            first_name TEXT,
            last_name TEXT,
            birthday DATE,
            gender TEXT,
            street_name TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            email TEXT,
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
        
        # Backup table
        c.execute('''
        CREATE TABLE IF NOT EXISTS Backup (
            backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            created_at DATETIME
        )
        ''')
        
        # RestoreCode table
        c.execute('''
        CREATE TABLE IF NOT EXISTS RestoreCode (
            code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            code TEXT,
            created_at DATETIME,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES User(user_id)
        )
        ''')
        
        # LogEntry table
        c.execute('''
        CREATE TABLE IF NOT EXISTS LogEntry (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES User(user_id)
        )
        ''')
        
        # TempCodes table
        c.execute('''
        CREATE TABLE IF NOT EXISTS TempCodes (
            user_id INTEGER PRIMARY KEY,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User(user_id)
        )
        ''')
        
        # LogStatus table
        c.execute('''
        CREATE TABLE IF NOT EXISTS LogStatus (
            user_id INTEGER PRIMARY KEY,
            last_seen_log_id INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # Create test database
    create_test_db()
    
    yield
    
    # Cleanup test files after test
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

@pytest.fixture
def user_service():
    """Provide UserService instance"""
    return UserService(TEST_DB)

@pytest.fixture
def traveller_service():
    """Provide TravellerService instance"""
    return TravellerService(TEST_DB)

@pytest.fixture
def scooter_service():
    """Provide ScooterService instance"""
    return ScooterService(TEST_DB)

@pytest.fixture
def test_user(user_service):
    """Create a test user"""
    success, msg = user_service.add_user(
        username="testuser1",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
        role="service_engineer"
    )
    assert success, f"Failed to create test user: {msg}"
    user = user_service.get_user_by_username("testuser1")
    return user

@pytest.fixture
def test_admin(user_service):
    """Create a test admin user"""
    success, msg = user_service.add_user(
        username="testadmin1",
        password="AdminPassword123!",
        first_name="Admin",
        last_name="User",
        role="system_admin"
    )
    assert success, f"Failed to create test admin: {msg}"
    user = user_service.get_user_by_username("testadmin1")
    return user
