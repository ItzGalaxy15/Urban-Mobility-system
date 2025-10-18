import re
from datetime import date, datetime
from models.traveller import CITY_CHOICES, ZIP_RE, PHONE_RE, LICENSE_RE, NAME_RE, STREET_RE, BIRTH_RE, EMAIL_RE, HOUSE_RE
from models.user import USERNAME_RE, PWD_ALLOWED_RE
from models.scooter import BRAND_RE, MODEL_RE, SERIAL_RE, DATE_RE, TOP_SPEED_MIN, TOP_SPEED_MAX, BATTERY_CAP_MAX, MILEAGE_MAX

# Define whitelist patterns for consistent validation
NAME_PATTERN = re.compile(r'^[A-Za-zÀ-ÿ\s]{2,30}$')  # Letters, spaces, accented characters
USERNAME_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{7,9}$')  # 8-10 chars, starts with letter/underscore
PASSWORD_PATTERN = re.compile(r'^[A-Za-z0-9~!@#$%&\-_+=`|\\(){}\[\]:;\'<>,.?/]{12,30}$')  # Allowed chars only
EMAIL_PATTERN = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')  # Standard email format
PHONE_PATTERN = re.compile(r'^\+31-6-[0-9]{8}$')  # Dutch mobile format
LICENSE_PATTERN = re.compile(r'^(?:[A-Z]{2}\d{7}|[A-Z]\d{8})$')  # 2 letters + 7 digits OR 1 letter + 8 digits
STREET_PATTERN = re.compile(r'^[A-Za-zÀ-ÿ\s]{2,50}$')  # Letters and spaces only
HOUSE_PATTERN = re.compile(r'^[0-9]+$')  # Digits only
ZIP_PATTERN = re.compile(r'^[0-9]{4}[A-Z]{2}$')  # 4 digits + 2 uppercase letters
BIRTH_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD format
BRAND_PATTERN = re.compile(r'^[A-Za-z0-9\s\-]{2,30}$')  # Alphanumeric, spaces, dashes
MODEL_PATTERN = re.compile(r'^[A-Za-z0-9\s\-]{1,30}$')  # Alphanumeric, spaces, dashes
SERIAL_PATTERN = re.compile(r'^[A-Za-z0-9]{10,17}$')  # Alphanumeric only
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD format

# --- User/Traveller Name Validation ---
def validate_first_name(value: str) -> tuple[bool, str]:
    if not value:
        return False, "First name is required"
    if NAME_PATTERN.fullmatch(value):
        return True, ""
    return False, "First name must be 2-30 characters and contain only letters and spaces"

def validate_last_name(value: str) -> tuple[bool, str]:
    if not value:
        return False, "Last name is required"
    if NAME_PATTERN.fullmatch(value):
        return True, ""
    return False, "Last name must be 2-30 characters and contain only letters and spaces"

# --- Username Validation ---
def validate_username(username: str) -> tuple[bool, str]:
    if not username:
        return False, "Username is required"
    if USERNAME_PATTERN.fullmatch(username):
        return True, ""
    return False, "Username must be 8-10 characters and start with a letter or underscore"

# --- Password Validation ---
def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password is required"
    if PASSWORD_PATTERN.fullmatch(password):
        # Whitelisting approach: ensure password contains at least one of each required character type
        # using positive lookahead assertions to verify all character types are present
        if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&\-_+=`|\\(){}\[\]:;\'<>,.?/])[A-Za-z0-9~!@#$%&\-_+=`|\\(){}\[\]:;\'<>,.?/]{12,30}$', password):
            return True, ""
    return False, "Password must be 12-30 characters and include lowercase, uppercase, digit and special character"

# --- Birthday Validation ---
def validate_birthday(birthday: str) -> tuple[bool, str]:
    if not birthday:
        return False, "Birthday is required"
    if BIRTH_PATTERN.fullmatch(birthday):
        try:
            y, m, d = map(int, birthday.split("-"))
            birth_date = date(y, m, d)
            age = (date.today() - birth_date).days // 365
            if age >= 18:
                return True, ""
            return False, "Traveller must be at least 18 years old"
        except ValueError:
            return False, "Invalid date: Please enter a valid date (e.g., 1990-01-15)"
    return False, "Birthday must be YYYY‑MM‑DD"

# --- Gender Validation ---
def validate_gender(gender: str) -> tuple[bool, str]:
    if not gender:
        return False, "Gender is required"
    if gender.lower() in {"male", "female"}:
        return True, ""
    return False, "Gender must be 'male' or 'female'"

# --- Street Name Validation ---
def validate_street_name(street: str) -> tuple[bool, str]:
    if not street:
        return False, "Street name is required"
    if STREET_PATTERN.fullmatch(street):
        return True, ""
    return False, "Street name must be 2-50 characters and contain only letters and spaces"

# --- House Number Validation ---
def validate_house_number(house_number: str) -> tuple[bool, str]:
    if not house_number:
        return False, "House number is required"
    if HOUSE_PATTERN.fullmatch(house_number):
        return True, ""
    return False, "House number must contain digits only"

# --- ZIP Code Validation ---
def validate_zip(zip_code: str) -> tuple[bool, str]:
    if not zip_code:
        return False, "Zip code is required"
    if ZIP_PATTERN.fullmatch(zip_code):
        return True, ""
    return False, "Zip code must be 4 digits + 2 uppercase letters"

# --- City Validation ---
def validate_city(city: str) -> tuple[bool, str]:
    if not city:
        return False, "City is required"
    if city in CITY_CHOICES:
        return True, ""
    return False, f"City must be one of: {', '.join(sorted(CITY_CHOICES))}"

# --- Email Validation ---
def validate_email(email: str) -> tuple[bool, str]:
    if not email:
        return False, "Email is required"
    if EMAIL_PATTERN.fullmatch(email):
        return True, ""
    return False, "Invalid email format"

# --- Phone Validation ---
def validate_phone(phone: str) -> tuple[bool, str]:
    if not phone:
        return False, "Mobile phone is required"
    if PHONE_PATTERN.fullmatch(phone):
        return True, ""
    return False, "Phone must be +31-6-DDDDDDDD"

# --- License Validation ---
def validate_license(license_no: str) -> tuple[bool, str]:
    if not license_no:
        return False, "Driving licence number is required"
    if LICENSE_PATTERN.fullmatch(license_no):
        return True, ""
    return False, "Driving licence format invalid"

# --- Scooter Brand/Model Validation ---
def validate_brand(brand: str) -> tuple[bool, str]:
    if not brand:
        return False, "Brand is required"
    if BRAND_PATTERN.fullmatch(brand):
        return True, ""
    return False, "Brand must be 2-30 alphanumeric characters, spaces, or dashes"

def validate_model(model: str) -> tuple[bool, str]:
    if not model:
        return False, "Model is required"
    if MODEL_PATTERN.fullmatch(model):
        return True, ""
    return False, "Model must be 1-30 alphanumeric characters, spaces, or dashes"

# --- Scooter Serial Number Validation ---
def validate_serial_number(serial_number: str) -> tuple[bool, str]:
    if not serial_number:
        return False, "Serial number is required"
    if SERIAL_PATTERN.fullmatch(serial_number):
        return True, ""
    return False, "Serial number must be 10-17 alphanumeric"

# --- Scooter Date Validation ---
def validate_scooter_date(date_str: str, field_name: str = "Date") -> tuple[bool, str]:
    if not date_str:
        return False, f"{field_name} is required"
    if DATE_PATTERN.fullmatch(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d").date()
            return True, ""
        except ValueError:
            return False, f"Invalid {field_name}: Please enter a valid date (e.g., 2023-01-15)"
    return False, f"{field_name} must be YYYY-MM-DD" 