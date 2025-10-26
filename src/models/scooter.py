import re, random
from datetime import datetime
from typing import Optional
from utils.crypto_utils import encrypt, decrypt
from utils.validation import validate_brand, validate_model, validate_serial_number, validate_scooter_date, TOP_SPEED_MIN, TOP_SPEED_MAX, BATTERY_CAP_MAX, MILEAGE_MAX


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
        
        # mandatory text checks
        if not all([brand, model, serial_number]):
            raise ValueError("brand, model and serial_number are mandatory")

        validations = [
            validate_brand(brand),
            validate_model(model),
            validate_serial_number(serial_number),
        ]

        for ok, msg in validations:
            if not ok:
                raise ValueError(msg)

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
            raise ValueError(f"mileage out of range (0-{MILEAGE_MAX})")

        # date handling
        if last_maint_date is not None:
            ok, msg = validate_scooter_date(last_maint_date, "last_maint_date")
            if not ok:
                raise ValueError(msg)
            try:
                datetime.strptime(last_maint_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date: Please enter a valid date (e.g., 2023-01-15)")

        # Store date as string for SQLite compatibility (Python 3.12+ deprecates datetime adapters)
        in_service_date_str = datetime.now().strftime("%Y-%m-%d")

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
        self.last_maint_date = last_maint_date  # string YYYY-MM-DD or None
        self.in_service_date = in_service_date_str  # string YYYY-MM-DD


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
