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

# Allowed fields for search_travellers (must match column names in the Traveller table)
ALLOWED_FIELDS = {
    "first_name", "last_name", "birthday", "gender", "street_name",
    "house_number", "zip_code", "city", "email", "mobile_phone",
    "driving_license_no"
}

class TravellerService:
    """Service layer responsible for CRUD operations on *Traveller* records.
    * A thin validation layer to give quick feedback before creating a ``Traveller``.
    * Encryption happens **inside** the ``Traveller`` model - the service never stores plain data.
    * Each public method returns ``(bool, str)`` → success flag + human-readable message.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    # Low-level helpers
    def _get_connection(self) -> sqlite3.Connection:
        """Return a *new* SQLite connection (caller closes it)."""
        return sqlite3.connect(self.db_path)

    # CRUD Methods
    def add_traveller(self, *, traveller: Optional[Traveller] = None, **fields) -> Tuple[bool, str]:
        """Add a traveller to the database.

        Accepts either a pre-built *Traveller* instance **or** raw keyword
        arguments with the model fields (first_name=..., last_name=..., …).
        """
        success = False  # default whitelist: fail unless proven valid
        message = "Traveller could not be added"
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
            success, message = True, "Traveller added successfully"
        except ValueError as exc:
            message = str(exc)
        except Exception as exc:
            message = f"Unexpected error: {exc}"
        return success, message

    def update_traveller(self, traveller_id: int, **updates) -> Tuple[bool, str]:
        """Update *one or more* fields of a traveller."""
        success = False
        message = "Traveller could not be updated"

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

        # 1 Run pre-checks
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
            encrypted = encrypt(val)
            set_parts.append(f"{col} = ?")
            values.append(encrypted)
        values.append(traveller_id)
        set_clause = ", ".join(set_parts)
        sql = f"UPDATE Traveller SET {set_clause} WHERE traveller_id = ?"

        # 3️ Execute & close
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(sql, tuple(values))
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected:
                success, message = True, "Traveller updated successfully"
        except Exception as exc:
            message = f"Error updating traveller: {exc}"

        return success, message

    def delete_traveller(self, traveller_id: int) -> Tuple[bool, str]:
        """Remove a traveller record by *traveller_id*."""
        success = False
        message = "Traveller could not be deleted"
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Traveller WHERE traveller_id = ?", (traveller_id,))
            conn.commit()
            affected = cur.rowcount
            conn.close()
            if affected:
                success, message = True, "Traveller deleted successfully"
        except Exception as exc:
            message = f"Error deleting traveller: {exc}"
        return success, message

    def search_travellers(self, key: str, field_name: str, limit: int = 50) -> list[Traveller]:
        """
        Search for travellers in a SPECIFIC field only.
        More accurate for edge cases like "45DE" in ZIP or "john.smith" in email.
        
        Args:
            key: search term
            field_name: exact field to search ("first_name", "email", "zip_code", etc.)
            limit: max results
        """
        if not key or field_name not in ALLOWED_FIELDS:
            return []
        
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # PHASE 1: Fetch only specified field
            cur.execute(f'''
                SELECT traveller_id, {field_name}
                FROM Traveller
                WHERE {field_name} IS NOT NULL
            ''')
            
            rows = cur.fetchall()
            matching_ids = []
            key_lc = key
            
            # Decrypt and search ONLY the specified field
            for row in rows:
                traveller_id, encrypted_value = row
                try:
                    decrypted = decrypt(encrypted_value) if encrypted_value else ""
                    if key_lc in decrypted:
                        matching_ids.append(traveller_id)
                        if len(matching_ids) >= limit:
                            break
                except Exception:
                    continue
            
            if not matching_ids:
                return []
            
            # PHASE 2: Fetch full records for matches
            placeholders = ','.join(['?'] * len(matching_ids))
            cur.execute(f'''
                SELECT traveller_id, first_name, last_name, birthday, gender,
                    street_name, house_number, zip_code, city, email,
                    mobile_phone, driving_license_no, registration_date
                FROM Traveller 
                WHERE traveller_id IN ({placeholders})
            ''', matching_ids)            
            
            matching_rows = cur.fetchall()
            results = []

            # Now decrypt all fields only for matches
            for row in matching_rows:
                try:
                    traveller = Traveller(
                        traveller_id=row[0],
                        first_name=decrypt(row[1]) if row[1] else "",
                        last_name=decrypt(row[2]) if row[2] else "",
                        birthday=decrypt(row[3]) if row[3] else "",
                        gender=decrypt(row[4]) if row[4] else "",
                        street_name=decrypt(row[5]) if row[5] else "",
                        house_number=decrypt(row[6]) if row[6] else "",
                        zip_code=decrypt(row[7]) if row[7] else "",
                        city=decrypt(row[8]) if row[8] else "",
                        email=decrypt(row[9]) if row[9] else "",
                        mobile_phone=decrypt(row[10]) if row[10] else "",
                        driving_license_no=decrypt(row[11]) if row[11] else ""
                    )
                    results.append(traveller)
                except Exception as exc:
                    print(f"Error creating traveller {row[0]}: {exc}")
                    continue

        except Exception as e:
            print(f"Error in traveller search: {e}")
        finally:
            conn.close()

        return results


# Singleton instance
traveller_service = TravellerService(DB_FILE)
