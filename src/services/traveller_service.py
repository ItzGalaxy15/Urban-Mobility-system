import sqlite3
from datetime import date
from typing import Tuple, Optional

from utils.crypto_utils import encrypt, decrypt
from models.traveller import Traveller
from config import DB_FILE
from utils.validation import (
    validate_first_name, validate_last_name, validate_birthday, validate_gender,
    validate_street_name, validate_house_number, validate_zip, validate_city,
    validate_email, validate_phone, validate_license,
    CITY_CHOICES,
    ZIP_PATTERN,
    PHONE_PATTERN,
    LICENSE_PATTERN,
    NAME_PATTERN,
    STREET_PATTERN,
    BIRTH_PATTERN,
    EMAIL_PATTERN,
    HOUSE_PATTERN,
)


class TravellerService:
    """Service layer responsible for CRUD operations on *Traveller* records.
    * A thin validation layer to give quick feedback before creating a ``Traveller``.
    * Encryption happens **inside** the ``Traveller`` model ‑ the service never stores plain data.
    * Each public method returns ``(bool, str)`` → success flag + human‑readable message.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    # Low‑level helpers
    def _get_connection(self) -> sqlite3.Connection:
        """Return a *new* SQLite connection (caller closes it)."""
        return sqlite3.connect(self.db_path)

    # CRUD Methods
    def add_traveller(self, *, traveller: Optional[Traveller] = None, **fields) -> Tuple[bool, str]:
        """Add a traveller to the database.

        Accepts either a pre‑built *Traveller* instance **or** raw keyword
        arguments with the model fields (first_name=..., last_name=..., …).
        """
        try:
            if traveller is None:
                validations = [
                    validate_first_name(fields.get("first_name")),
                    validate_last_name(fields.get("last_name")),
                    validate_birthday(fields.get("birthday")),
                    validate_city(fields.get("city")),
                    validate_zip(fields.get("zip_code")),
                    validate_email(fields.get("email")),
                    validate_phone(fields.get("mobile_phone")),
                    validate_house_number(fields.get("house_number")),
                    validate_gender(fields.get("gender")),
                    validate_street_name(fields.get("street_name")),
                ]
                for ok, msg in validations:
                    if not ok:
                        return False, msg
                traveller = Traveller(**fields)

            # 3️ Persist (encrypted!)
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO Traveller (
                    first_name, last_name, birthday, gender, street_name, house_number,
                    zip_code, city, email, mobile_phone, driving_license_no,
                    registration_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    traveller.first_name,
                    traveller.last_name,
                    traveller.birthday,
                    traveller.gender,
                    traveller.street_name,
                    traveller.house_number,
                    traveller.zip_code,
                    traveller.city,
                    traveller.email,
                    traveller.mobile_phone,
                    traveller.driving_license_no,
                ),
            )
            conn.commit()
            conn.close()
            return True, "Traveller added successfully"
        except ValueError as exc:
            return False, str(exc)

    def update_traveller(self, traveller_id: int, **updates) -> Tuple[bool, str]:
        """Update *one or more* fields of a traveller."""

        if not updates:
            return False, "No updates supplied"

        validators = {
            "first_name": validate_first_name,
            "last_name": validate_last_name,
            "birthday": validate_birthday,
            "gender": validate_gender,
            "street_name": validate_street_name,
            "city": validate_city,
            "zip_code": validate_zip,
            "email": validate_email,
            "mobile_phone": validate_phone,
            "house_number": validate_house_number,
            "driving_license_no": validate_license,
        }

        # 1 Run pre‑checks
        for field, value in updates.items():
            check = validators.get(field)
            if check is None:
                return False, f"Unknown/readonly field: {field}"
            ok, msg = check(value)
            if not ok:
                return False, msg

        # 2️ Build dynamic UPDATE
        set_parts = []
        values: list[bytes] = []
        for col, val in updates.items():
            encrypted = encrypt(val.lower()) if col == "gender" else encrypt(val)
            set_parts.append(f"{col} = ?")
            values.append(encrypted)
        values.append(traveller_id)
        set_clause = ", ".join(set_parts)
        sql = f"UPDATE Traveller SET {set_clause} WHERE traveller_id = ?"

        # 3️ Execute & close
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(sql, tuple(values))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected:
            return True, "Traveller updated successfully"
        return False, "Traveller not found"

    def delete_traveller(self, traveller_id: int) -> Tuple[bool, str]:
        """Remove a traveller record by *traveller_id*."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Traveller WHERE traveller_id = ?", (traveller_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected:
            return True, "Traveller deleted successfully"
        return False, "Traveller not found"


    def search_travellers(self, key: str, limit: int = 50) -> list[Traveller]:
        """
        Search (partial, case-insensitive) for Travellers on the most common fields.
        Uses efficient database-level filtering to avoid loading all data into memory.
        
        Args:
            key: piece of text/number to search for ("mik", "2328", …)
            limit: max. number of results
        """
        if not key or not key:
            return []

        key_lc = key.lower()
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            # This query retrieves all traveller records that could potentially match our search.
            # We select only the searchable fields (first_name, last_name, etc) that contain text
            # we might want to search through.
            #
            # The WHERE clause ensures we only get records that have at least one searchable field 
            # populated (not NULL). This avoids processing empty records.
            #
            # We also add a basic filter to reduce the number of records we need to decrypt:
            # - For numeric searches (like zip codes, phone numbers), we look for records containing digits
            # - For text searches, we look for records that might contain the search term
            #
            # The fields are encrypted in the database, so we'll need to decrypt them later
            # to actually check if they contain our search term.
            
            # Determine if search term is numeric
            is_numeric = key.isdigit()
            
            if is_numeric:
                # For numeric searches, look for records that might contain numbers
                cur.execute('''
                    SELECT traveller_id, first_name, last_name, email, mobile_phone, 
                           driving_license_no, city, zip_code
                    FROM Traveller
                    WHERE (first_name IS NOT NULL OR last_name IS NOT NULL OR 
                           email IS NOT NULL OR mobile_phone IS NOT NULL OR 
                           driving_license_no IS NOT NULL OR city IS NOT NULL OR 
                           zip_code IS NOT NULL)
                    AND (mobile_phone IS NOT NULL OR driving_license_no IS NOT NULL OR zip_code IS NOT NULL)
                ''')
            else:
                # For text searches, look for records that might contain text
                cur.execute('''
                    SELECT traveller_id, first_name, last_name, email, mobile_phone, 
                           driving_license_no, city, zip_code
                    FROM Traveller
                    WHERE (first_name IS NOT NULL OR last_name IS NOT NULL OR 
                           email IS NOT NULL OR mobile_phone IS NOT NULL OR 
                           driving_license_no IS NOT NULL OR city IS NOT NULL OR 
                           zip_code IS NOT NULL)
                    AND (first_name IS NOT NULL OR last_name IS NOT NULL OR email IS NOT NULL OR city IS NOT NULL)
                ''')
            
            rows = cur.fetchall()
            
            # Find matching traveller IDs by decrypting and comparing
            matching_ids = []
            
            for row in rows:
                traveller_id = row[0]
                try:
                    # Decrypt all searchable fields and check if any contain the search term
                    searchable_fields = [
                        decrypt(row[1]) if row[1] else "",  # first_name
                        decrypt(row[2]) if row[2] else "",  # last_name
                        decrypt(row[3]) if row[3] else "",  # email
                        decrypt(row[4]) if row[4] else "",  # mobile_phone
                        decrypt(row[5]) if row[5] else "",  # driving_license_no
                        decrypt(row[6]) if row[6] else "",  # city
                        decrypt(row[7]) if row[7] else "",  # zip_code
                    ]
                    
                    # Combine all fields into one searchable string
                    searchable = " ".join(searchable_fields).lower()
                    
                    if key_lc in searchable:
                        matching_ids.append(traveller_id)
                        if len(matching_ids) >= limit:
                            break
                            
                except Exception as exc:
                    # Skip rows that fail to decrypt
                    print(f"Error processing traveller row {traveller_id}: {exc}")
                    continue
            
            # If no matches found, return empty list
            if not matching_ids:
                return []
            
            # Fetch only the matching travellers
            placeholders = ','.join(['?' for _ in matching_ids])
            cur.execute(f'''
                SELECT traveller_id, first_name, last_name, birthday, gender,
                       street_name, house_number, zip_code, city, email,
                       mobile_phone, driving_license_no, registration_date
                FROM Traveller 
                WHERE traveller_id IN ({placeholders})
            ''', matching_ids)
            
            matching_rows = cur.fetchall()
            
            results = []
            for row in matching_rows:
                try:
                    traveller = Traveller(
                        traveller_id=row[0],
                        first_name=decrypt(row[1]),
                        last_name=decrypt(row[2]),
                        birthday=decrypt(row[3]),
                        gender=decrypt(row[4]),
                        street_name=decrypt(row[5]),
                        house_number=decrypt(row[6]),
                        zip_code=decrypt(row[7]),
                        city=decrypt(row[8]),
                        email=decrypt(row[9]),
                        mobile_phone=decrypt(row[10]),
                        driving_license_no=decrypt(row[11])
                    )
                    results.append(traveller)
                except Exception as exc:
                    print(f"Error creating traveller object for row {row[0]}: {exc}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error in traveller search: {e}")
            return []
        finally:
            conn.close()

# Singleton instance
traveller_service = TravellerService(DB_FILE)
