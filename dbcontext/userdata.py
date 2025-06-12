import sqlite3
from dbcontext.crypto_utils import hash_password, encrypt, decrypt, check_password


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


def update_password(user_id, new_password):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    hashed = hash_password(new_password)
    c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
    conn.commit()
    conn.close()
