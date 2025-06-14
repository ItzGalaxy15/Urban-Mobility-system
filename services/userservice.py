import sqlite3
from utils.crypto_utils import hash_password, decrypt, check_password
from models.user import User


def add_user_from_params(username, password, first_name, last_name, role):
    """
    Add a user to the database using individual parameters.
    This is a wrapper around the User model for backward compatibility.
    """
    try:
        user = User(
            username=username,
            password_plain=password,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        add_user(user)
        return True
    except ValueError as e:
        print(f"Error adding user: {e}")
        return False


def add_user(user):
    """
    Add a user to the database. The user object should already have encrypted data.
    
    Args:
        user: User object with encrypted username, password_hash, first_name, and last_name
    """
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO User (username, password_hash, first_name, last_name, registration_date, role)
        VALUES (?, ?, ?, ?, datetime('now'), ?)
    ''', (
        user.username,
        user.password_hash,
        user.first_name,
        user.last_name,
        user.role
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
            "role": decrypt(row[4])
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
                "role": decrypt(row[4])
            }
    return None


def update_password(user_id, new_password):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    hashed = hash_password(new_password)
    c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
    conn.commit()
    conn.close()
