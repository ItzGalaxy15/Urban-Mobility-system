# models/traveller.py
import re, random
from datetime import datetime, date
from typing import Optional
from utils.crypto_utils import encrypt, decrypt
from utils.validation import CITY_CHOICES, ZIP_PATTERN, PHONE_PATTERN, LICENSE_PATTERN, NAME_PATTERN, STREET_PATTERN, BIRTH_PATTERN, EMAIL_PATTERN, HOUSE_PATTERN

# These are now imported from utils/validation.py
# CITY_CHOICES
# ZIP_RE     |ZIP_PATTERN = re.compile(r"^\d{4}[A-Z]{2}$")
# PHONE_RE   |PHONE_PATTERN = re.compile(r"^\+31-6-\d{8}$")
# LICENSE_RE |LICENSE_PATTERN = re.compile(r"^(?:[A-Z]{2}\d{7}|[A-Z]\d{8})$")
# NAME_RE    |NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ]{2,30}$")  # letters only, 2-30 chars
# STREET_RE  |STREET_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ\s]{2,50}$")  # letters and spaces, 2-50 chars
# BIRTH_RE   |BIRTH_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")   # yyyy-mm-dd
# EMAIL_RE   |EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
# HOUSE_RE   |HOUSE_PATTERN = re.compile(r"^\d+$") 

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
        #basic non-empty checks
        for v in (first_name, last_name, birthday, gender, street_name,
                  house_number, zip_code, city, email, mobile_phone,
                  driving_license_no):
            if not v:
                raise ValueError("all fields are mandatory")

        # format checks
        if not NAME_PATTERN.match(first_name):
            raise ValueError("first_name must be 2-30 chars, letters only")
        if not NAME_PATTERN.match(last_name):
            raise ValueError("last_name must be 2-30 chars, letters only")
        if not BIRTH_PATTERN.match(birthday):
            raise ValueError("birthday must be YYYY-MM-DD")
        if not STREET_PATTERN.match(street_name):
            raise ValueError("street_name must be 2-50 chars, letters and spaces only")
        if not HOUSE_PATTERN.match(house_number):
            raise ValueError("house_number may contain digits only")
        if not ZIP_PATTERN.match(zip_code):
            raise ValueError("zip_code must be DDDDXX")
        if city not in CITY_CHOICES:
            raise ValueError("city must be one of the predefined choices")
        if not EMAIL_PATTERN.match(email):
            raise ValueError("invalid email")
        if not PHONE_PATTERN.match(mobile_phone):
            raise ValueError("mobile_phone must be +31-6-DDDDDDDD")
        if not LICENSE_PATTERN.match(driving_license_no):
            raise ValueError("driving_license format invalid")

        # 18+ control
        y, m, d = map(int, birthday.split("-"))
        age = (date.today() - date(y, m, d)).days // 365
        if age < 18:
            raise ValueError("traveller must be at least 18 years old")

        if gender.lower() not in {"male", "female"}:
            raise ValueError("gender must be male or female")

        # store(encrypted)
        self.traveller_id       = traveller_id
        self.registration_date  = datetime.now()
        self.first_name         = encrypt(first_name)
        self.last_name          = encrypt(last_name)
        self.birthday           = encrypt(birthday)
        self.gender             = encrypt(gender.lower())
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
