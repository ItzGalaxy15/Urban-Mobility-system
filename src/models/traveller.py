# models/traveller.py
from datetime import datetime, date
from typing import Optional
from utils.crypto_utils import encrypt, decrypt
from utils.validation import (
    validate_first_name, validate_last_name, validate_birthday,
    validate_gender, validate_street_name, validate_house_number,
    validate_zip, validate_city, validate_email, validate_phone,
    validate_license
)


class Traveller:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        email: str,
        mobile_phone: str,
        driving_license_no: str,
        traveller_id: Optional[int] = None,  # Optional, for existing travellers
    ):
        
        # Basic empty check
        required_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "birthday": birthday,
            "gender": gender,
            "street_name": street_name,
            "house_number": house_number,
            "zip_code": zip_code,
            "city": city,
            "email": email,
            "mobile_phone": mobile_phone,
            "driving_license_no": driving_license_no,
        }

        for field, value in required_fields.items():
            if not value:
                raise ValueError(f"{field} is required")

        # Centralized validation (from utils/validation.py)
        checks = [
            validate_first_name(first_name),
            validate_last_name(last_name),
            validate_birthday(birthday),
            validate_gender(gender),
            validate_street_name(street_name),
            validate_house_number(house_number),
            validate_zip(zip_code),
            validate_city(city),
            validate_email(email),
            validate_phone(mobile_phone),
            validate_license(driving_license_no),
        ]
        for ok, msg in checks:
            if not ok:
                raise ValueError(msg)

        if traveller_id is not None and not isinstance(traveller_id, int):
            raise ValueError("traveller_id must be an integer")
    
        # store(encrypted)
        self.traveller_id       = traveller_id
        self.registration_date  = datetime.now()
        self.first_name         = encrypt(first_name)
        self.last_name          = encrypt(last_name)
        self.birthday           = encrypt(birthday)
        self.gender             = encrypt(gender)
        self.street_name        = encrypt(street_name)
        self.house_number       = encrypt(house_number)
        self.zip_code           = encrypt(zip_code)
        self.city               = encrypt(city)
        self.email              = encrypt(email)
        self.mobile_phone       = encrypt(mobile_phone)
        self.driving_license_no = encrypt(driving_license_no)


    @property
    def first_name_plain(self) -> str:
        return decrypt(self.first_name)

    @property
    def last_name_plain(self) -> str:
        return decrypt(self.last_name)

    @property
    def birthday_plain(self) -> str:
        return decrypt(self.birthday)

    @property
    def gender_plain(self) -> str:
        return decrypt(self.gender)

    @property
    def street_name_plain(self) -> str:
        return decrypt(self.street_name)

    @property
    def house_number_plain(self) -> str:
        return decrypt(self.house_number)

    @property
    def zip_code_plain(self) -> str:
        return decrypt(self.zip_code)

    @property
    def city_plain(self) -> str:
        return decrypt(self.city)

    @property
    def email_plain(self) -> str:
        return decrypt(self.email)

    @property
    def mobile_phone_plain(self) -> str:
        return decrypt(self.mobile_phone)

    @property
    def driving_license_no_plain(self) -> str:
        return decrypt(self.driving_license_no)

    @property
    def full_name(self) -> str:
        return f"{self.first_name_plain} {self.last_name_plain}"

    def __repr__(self):
        return f"Traveller(name={self.full_name})"
