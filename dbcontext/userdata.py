import sqlite3
from dbcontext.crypto_utils import hash_password

def update_password(user_id, new_password):
    conn = sqlite3.connect('urban_mobility.db')
    c = conn.cursor()
    hashed = hash_password(new_password)
    c.execute('UPDATE User SET password_hash = ? WHERE user_id = ?', (hashed, user_id))
    conn.commit()
    conn.close()
