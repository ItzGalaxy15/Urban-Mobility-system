import sqlite3
from models.user import User

def create_db():
    conn = sqlite3.connect('urban_mobility.db')
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

    # Check if super admin exists
    c.execute('SELECT COUNT(*) FROM User WHERE role = "super"')
    super_admin_count = c.fetchone()[0]

    # Only create super admin if none exists
    if super_admin_count == 0:
        super_admin = User(
            username="super_admin",
            password_plain="Admin_123?",
            role="super",
            first_name="John",
            last_name="Doe"
        )

        c.execute('''
        INSERT INTO User (
            user_id,
            username,
            password_hash,
            first_name,
            last_name,
            registration_date,
            role
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            super_admin.user_id,
            super_admin.username,
            super_admin.password_hash,
            super_admin.first_name,
            super_admin.last_name,
            super_admin.registration_date,
            super_admin.role
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
    conn.close()

if __name__ == "__main__":
    create_db()
