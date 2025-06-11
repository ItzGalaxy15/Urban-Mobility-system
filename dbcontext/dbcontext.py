import sqlite3
from dbcontext.crypto_utils import encrypt, hash_password, decrypt, check_password

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

def add_user(username, password, first_name, last_name, role):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO User (username, password_hash, first_name, last_name, registration_date, role)
        VALUES (?, ?, ?, ?, datetime('now'), ?)
    ''', (
        encrypt(username),
        hash_password(password),
        encrypt(first_name),
        encrypt(last_name),
        role
    ))
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, last_name, role FROM User WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "username": decrypt(row[1]),
            "first_name": decrypt(row[2]),
            "last_name": decrypt(row[3]),
            "role": row[4]
        }
    return None

def verify_user_password(user_id, password):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM User WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password(password, row[0])
    return False

def get_user_by_username(username):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, last_name, role FROM User')
    users = c.fetchall()
    conn.close()
    for row in users:
        if decrypt(row[1]) == username:
            return {
                "user_id": row[0],
                "username": decrypt(row[1]),
                "first_name": decrypt(row[2]),
                "last_name": decrypt(row[3]),
                "role": row[4]
            }
    return None

if __name__ == "__main__":
    create_db()
