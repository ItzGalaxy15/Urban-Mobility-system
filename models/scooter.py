import re, random
from datetime import datetime
from typing import Optional
from utils.crypto_utils import encrypt, decrypt

# Regex & ranges
BRAND_RE   = re.compile(r"^[A-Za-z0-9\- ]{2,30}$")
MODEL_RE   = re.compile(r"^[A-Za-z0-9\- ]{1,30}$")
SERIAL_RE  = re.compile(r"^[A-Za-z0-9]{10,17}$")
DATE_RE    = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TOP_SPEED_MIN, TOP_SPEED_MAX = 5, 50     # km/h
BATTERY_CAP_MAX = 5_000                  # Wh
MILEAGE_MAX     = 1_000_000              # km


class Scooter:
    def __init__(
        self,
        brand: str,
        model: str,
        serial_number: str,
        top_speed: float,
        battery_capacity: float,
        state_of_charge: float,
        target_soc_min: float,
        target_soc_max: float,
        location_lat: float,
        location_lon: float,
        *,
        scooter_id: int = None,
        mileage: float = 0.0,
        out_of_service: bool = False,
        last_maint_date: Optional[str] = None,  # YYYY-MM-DD
    ) -> None:
        # Store ID if provided (for existing scooters)
        # self.scooter_id = scooter_id if scooter_id is not None else random.randint(1_000_000, 9_999_999)
        
        # mandatory text checks
        if not all([brand, model, serial_number]):
            raise ValueError("brand, model and serial_number are mandatory")

        if not BRAND_RE.fullmatch(brand):
            raise ValueError("brand format invalid (2‑30 alphanum/- chars)")
        if not MODEL_RE.fullmatch(model):
            raise ValueError("model format invalid (1‑30 alphanum/‑ chars)")
        if not SERIAL_RE.fullmatch(serial_number):
            raise ValueError("serial_number must be 10‑17 alphanum chars")

        # numeric range checks
        if not (TOP_SPEED_MIN <= top_speed <= TOP_SPEED_MAX):
            raise ValueError(f"top_speed out of range ({TOP_SPEED_MIN}‑{TOP_SPEED_MAX})")
        if not (0 <= battery_capacity <= BATTERY_CAP_MAX):
            raise ValueError(f"battery_capacity out of range (0‑{BATTERY_CAP_MAX} Wh)")
        if not (0 <= state_of_charge <= 100):
            raise ValueError("state_of_charge must be 0‑100")

        if not (0 <= target_soc_min < target_soc_max <= 100):
            raise ValueError("target_soc_min/max invalid (0 ≤ min < max ≤ 100)")

        if not (-90 <= location_lat <= 90):
            raise ValueError("latitude out of range")
        if not (-180 <= location_lon <= 180):
            raise ValueError("longitude out of range")
        if not 0 <= mileage < MILEAGE_MAX:
            raise ValueError("mileage out of range (0‑1 000 000)")

        # date handling
        if last_maint_date is not None:
            if not DATE_RE.fullmatch(last_maint_date):
                raise ValueError("last_maint_date must be YYYY‑MM‑DD")
            last_maint_date_obj = datetime.strptime(last_maint_date, "%Y-%m-%d").date()
        else:
            last_maint_date_obj = None

        in_service_dt = datetime.now()

        # store(encrypted) -------------------------------------------
        try:
            self.brand = encrypt(brand)  # encrypt() handles encoding
            self.model = encrypt(model)  # encrypt() handles encoding
            self.serial_number = encrypt(serial_number)  # encrypt() handles encoding
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

        self.top_speed = float(top_speed)
        self.battery_capacity = float(battery_capacity)
        self.state_of_charge = float(state_of_charge)
        self.target_soc_min = float(target_soc_min)
        self.target_soc_max = float(target_soc_max)
        self.location_lat = float(location_lat)
        self.location_lon = float(location_lon)
        self.out_of_service = int(bool(out_of_service))
        self.mileage = float(mileage)

        self.scooter_id = scooter_id
        self.last_maint_date = last_maint_date_obj  # date or None
        self.in_service_date = in_service_dt        # datetime


    # Getters (plain text)
    @property
    def brand_plain(self) -> str:
        return decrypt(self.brand)

    @property
    def model_plain(self) -> str:
        return decrypt(self.model)

    @property
    def serial_number_plain(self) -> str:
        return decrypt(self.serial_number)

    @property
    def is_out_of_service(self) -> bool:
        return bool(self.out_of_service)

    def __repr__(self) -> str:
        return (
            f"Scooter(brand={self.brand_plain}, "
            f"model={self.model_plain}, serial={self.serial_number_plain})"
        )
