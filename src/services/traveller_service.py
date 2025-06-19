import sqlite3
from datetime import date
from typing import Tuple, Optional

from utils.crypto_utils import encrypt, decrypt
from models.traveller import (
    Traveller,
    CITY_CHOICES,
    ZIP_RE,
    PHONE_RE,
    LICENSE_RE,
    BIRTH_RE,
    EMAIL_RE,
    HOUSE_RE,
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

    # Validation helpers (keep them simple & self‑contained)
    def _validate_name(self, value: str, field: str) -> Tuple[bool, str]:
        if not value:
            return False, f"{field} is required"
        if not value.strip():
            return False, f"{field} cannot be empty"
        return True, ""

    def _validate_birthday(self, birthday: str) -> Tuple[bool, str]:
        if not birthday:
            return False, "Birthday is required"
        if not BIRTH_RE.fullmatch(birthday):
            return False, "Birthday must be YYYY‑MM‑DD"
        y, m, d = map(int, birthday.split("-"))
        age = (date.today() - date(y, m, d)).days // 365
        if age < 18:
            return False, "Traveller must be at least 18 years old"
        return True, ""

    def _validate_zip(self, zip_code: str) -> Tuple[bool, str]:
        if not zip_code:
            return False, "Zip code is required"
        if not ZIP_RE.fullmatch(zip_code):
            return False, "Zip code must be 4 digits + 2 uppercase letters"
        return True, ""

    def _validate_city(self, city: str) -> Tuple[bool, str]:
        if not city:
            return False, "City is required"
        if city not in CITY_CHOICES:
            return False, f"City must be one of: {', '.join(sorted(CITY_CHOICES))}"
        return True, ""

    def _validate_email(self, email: str) -> Tuple[bool, str]:
        if not email:
            return False, "Email is required"
        if not EMAIL_RE.fullmatch(email):
            return False, "Invalid email format"
        return True, ""

    def _validate_phone(self, phone: str) -> Tuple[bool, str]:
        if not phone:
            return False, "Mobile phone is required"
        if not PHONE_RE.fullmatch(phone):
            return False, "Phone must be +31-6-XXXXXXXX"
        return True, ""

    def _validate_house_number(self, house_number: str) -> Tuple[bool, str]:
        if not house_number:
            return False, "House number is required"
        if not HOUSE_RE.fullmatch(house_number):
            return False, "House number must contain digits only"
        return True, ""

    def _validate_license(self, license_no: str) -> Tuple[bool, str]:
        if not license_no:
            return False, "Driving licence number is required"
        if not LICENSE_RE.fullmatch(license_no):
            return False, "Driving licence format invalid"
        return True, ""

    def _validate_gender(self, gender: str) -> Tuple[bool, str]:
        """Accept only "male" or "female" (case‑insensitive)."""
        if not gender:
            return False, "Gender is required"
        if gender.lower() not in {"male", "female"}:
            return False, "Gender must be 'male' or 'female'"
        return True, ""

    def _validate_street_name(self, street: str) -> Tuple[bool, str]:
        if not street:
            return False, "Street name is required"
        if not street.strip():
            return False, "Street name cannot be empty"
        return True, ""

    # CRUD Methods
    def add_traveller(self, *, traveller: Optional[Traveller] = None, **fields) -> Tuple[bool, str]:
        """Add a traveller to the database.

        Accepts either a pre‑built *Traveller* instance **or** raw keyword
        arguments with the model fields (first_name=..., last_name=..., …).
        """
        try:
            if traveller is None:
                # 1️ Quick validations (user‑friendly feedback)
                validations = [
                    self._validate_name(fields.get("first_name"), "First name"),
                    self._validate_name(fields.get("last_name"), "Last name"),
                    self._validate_birthday(fields.get("birthday")),
                    self._validate_city(fields.get("city")),
                    self._validate_zip(fields.get("zip_code")),
                    self._validate_email(fields.get("email")),
                    self._validate_phone(fields.get("mobile_phone")),
                    self._validate_house_number(fields.get("house_number")),
                    self._validate_gender(fields.get("gender")),
                    self._validate_street_name(fields.get("street_name")),
                ]
                for ok, msg in validations:
                    if not ok:
                        return False, msg

                # 2️ Let the model handle heavy validation & encryption
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

        # Map each updatable column to a validator (or None if not validated here)
        validators = {
            "first_name": lambda v: self._validate_name(v, "First name"),
            "last_name": lambda v: self._validate_name(v, "Last name"),
            "birthday": self._validate_birthday,
            "gender": self._validate_gender,
            "street_name": self._validate_street_name,
            "city": self._validate_city,
            "zip_code": self._validate_zip,
            "email": self._validate_email,
            "mobile_phone": self._validate_phone,
            "house_number": self._validate_house_number,
            "driving_license_no": self._validate_license,
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
        Returns a list of decrypted dicts; empty list = no match.

        Args:
        key : piece of text/number to search for ("mik", "2328", …)
        limit : max. number of results
        """
        if not key:
            return []

        key_lc = key.lower()
        conn   = self._get_connection()
        cur    = conn.cursor()

        cur.execute(
            '''SELECT traveller_id, first_name, last_name, birthday, gender,
                      street_name, house_number, zip_code, city, email,
                      mobile_phone, driving_license_no, registration_date
               FROM Traveller'''
        )
        rows = cur.fetchall()
        conn.close()

        results: list[dict] = []
        for row in rows:
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
                    # registration_date is set internally by the Traveller model
                )
            except Exception as exc:
                # Skip rows that fail to decrypt or instantiate
                print(f"Error processing traveller row {row[0]}: {exc}")
                continue

            # Combine all fields into one string and check substring (if None, use empty string)
            searchable = (
                str(traveller.traveller_id or "")
                + (traveller.first_name_plain or "")
                + (traveller.last_name_plain or "")
                + (traveller.email_plain or "")
                + (traveller.mobile_phone_plain or "")
                + (traveller.driving_license_no_plain or "")
                + (traveller.city_plain or "")
                + (traveller.zip_code_plain or "")
            ).lower()

            if key_lc in searchable:
                results.append(traveller)
                if len(results) >= limit:
                    break

        return results

# Singleton instance (keeps import code clean)
traveller_service = TravellerService("urban_mobility.db")
