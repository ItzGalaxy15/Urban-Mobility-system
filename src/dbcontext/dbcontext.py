import sqlite3

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

    # Temporary password reset code table
    c.execute('''
    CREATE TABLE IF NOT EXISTS TempCodes (
        user_id INTEGER PRIMARY KEY,
        code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    ''')

    # table LogStatus to track “last seen” ID per user
    c.execute('''
    CREATE TABLE IF NOT EXISTS LogStatus (
        user_id INTEGER PRIMARY KEY,
        last_seen_log_id INTEGER
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
