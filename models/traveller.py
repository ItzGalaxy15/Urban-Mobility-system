# models/traveller.py
import re, random
from datetime import datetime, date
from utils.crypto_utils import fernet

CITY_CHOICES = {
    "Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven",
    "Groningen", "Maastricht", "Arnhem", "Leiden", "Zwolle",
}

ZIP_RE      = re.compile(r"^\d{4}[A-Z]{2}$")
PHONE_RE    = re.compile(r"^\+31-6-\d{8}$")
LICENSE_RE  = re.compile(r"^[A-Z]{1,2}\d{8}$")
BIRTH_RE    = re.compile(r"^\d{4}-\d{2}-\d{2}$")   # yyyy-mm-dd
EMAIL_RE    = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
HOUSE_RE    = re.compile(r"^\d+$") 

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
    ):
        #basic non-empty checks
        for v in (first_name, last_name, birthday, gender, street_name,
                  house_number, zip_code, city, email, mobile_phone,
                  driving_license_no):
            if not v:
                raise ValueError("all fields are mandatory")

        # format checks 
        if not BIRTH_RE.match(birthday):
            raise ValueError("birthday must be YYYY-MM-DD")
        if not HOUSE_RE.match(house_number):
            raise ValueError("house_number may contain digits only")
        if not ZIP_RE.match(zip_code):
            raise ValueError("zip_code must be DDDDXX")
        if city not in CITY_CHOICES:
            raise ValueError("city must be one of the predefined choices")
        if not EMAIL_RE.match(email):
            raise ValueError("invalid email")
        if not PHONE_RE.match(mobile_phone):
            raise ValueError("mobile_phone must be +31-6-DDDDDDDD")
        if not LICENSE_RE.match(driving_license_no):
            raise ValueError("driving_license format invalid")

        # 18+ control
        y, m, d = map(int, birthday.split("-"))
        age = (date.today() - date(y, m, d)).days // 365
        if age < 18:
            raise ValueError("traveller must be at least 18 years old")

        if gender.lower() not in {"male", "female"}:
            raise ValueError("gender must be male or female")

        # store(encrypted)
        # self.customer_id        = random.randint(1_000_000, 9_999_999)       # properly unique ID
        self.registration_date  = datetime.now()
        self.first_name         = self._encrypt(first_name)
        self.last_name          = self._encrypt(last_name)
        #  self.birthday           = self._encrypt(birthday)
        self.birthday           = datetime.strptime(birthday, "%Y-%m-%d").date()
        self.gender             = self._encrypt(gender.lower())
        self.street_name        = self._encrypt(street_name)
        self.house_number       = self._encrypt(house_number)
        self.zip_code           = self._encrypt(zip_code)
        self.city               = self._encrypt(city)
        self.email              = self._encrypt(email)
        self.mobile_phone       = self._encrypt(mobile_phone)
        self.driving_license_no = self._encrypt(driving_license_no)

    @staticmethod
    def _encrypt(value: str) -> bytes:
        return fernet.encrypt(value.encode())

    @staticmethod
    def _decrypt(value: bytes) -> str:
        return fernet.decrypt(value).decode()

    @property
    def first_name_plain(self) -> str:
        return self._decrypt(self.first_name)

    @property
    def last_name_plain(self) -> str:
        return self._decrypt(self.last_name)

    @property
    def birthday_plain(self) -> str:
        return self.birthday.strftime("%Y-%m-%d")

    @property
    def gender_plain(self) -> str:
        return self._decrypt(self.gender)

    @property
    def street_name_plain(self) -> str:
        return self._decrypt(self.street_name)

    @property
    def house_number_plain(self) -> str:
        return self._decrypt(self.house_number)

    @property
    def zip_code_plain(self) -> str:
        return self._decrypt(self.zip_code)

    @property
    def city_plain(self) -> str:
        return self._decrypt(self.city)

    @property
    def email_plain(self) -> str:
        return self._decrypt(self.email)

    @property
    def mobile_phone_plain(self) -> str:
        return self._decrypt(self.mobile_phone)

    @property
    def driving_license_no_plain(self) -> str:
        return self._decrypt(self.driving_license_no)

    @property
    def full_name(self) -> str:
        return f"{self.first_name_plain} {self.last_name_plain}"

    def __repr__(self):
        return f"Traveller(name={self.full_name})"
