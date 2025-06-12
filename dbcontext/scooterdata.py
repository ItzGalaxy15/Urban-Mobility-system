from typing import List, Optional
import sqlite3
from models.scooter import Scooter
from utils.crypto_utils import decrypt

class ScooterData:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def add_scooter(self, scooter: Scooter) -> bool:
        """Add a new scooter to the database"""
        print(f"[DEBUG] Adding scooter to database: {scooter}")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                print("[DEBUG] Executing INSERT query")
                cursor.execute("""
                    INSERT INTO Scooter (
                        scooter_id, brand, model, serial_number, top_speed,
                        battery_capacity, state_of_charge, target_soc_min,
                        target_soc_max, location_lat, location_lon,
                        out_of_service, mileage, last_maint_date, in_service_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scooter.scooter_id,
                    scooter.brand,  # Already encrypted by model
                    scooter.model,  # Already encrypted by model
                    scooter.serial_number,  # Already encrypted by model
                    scooter.top_speed,
                    scooter.battery_capacity,
                    scooter.state_of_charge,
                    scooter.target_soc_min,
                    scooter.target_soc_max,
                    scooter.location_lat,
                    scooter.location_lon,
                    scooter.out_of_service,
                    scooter.mileage,
                    scooter.last_maint_date,
                    scooter.in_service_date
                ))
                print("[DEBUG] INSERT query executed successfully")
                conn.commit()
                print("[DEBUG] Changes committed to database")
                return True
        except sqlite3.Error as e:
            print(f"[ERROR] Database error: {str(e)}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {str(e)}")
            return False

    def get_scooter_by_id(self, scooter_id: int) -> Optional[Scooter]:
        """Retrieve a scooter by its ID"""
        print(f"[DEBUG] Retrieving scooter with ID: {scooter_id}")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Scooter WHERE scooter_id = ?", (scooter_id,))
                row = cursor.fetchone()
                if row:
                    print("[DEBUG] Found scooter in database")
                    return self._row_to_scooter(row)
                print("[DEBUG] No scooter found with that ID")
                return None
        except sqlite3.Error as e:
            print(f"[ERROR] Database error: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {str(e)}")
            return None

    def _row_to_scooter(self, row: tuple) -> Scooter:
        """Convert a database row to a Scooter object"""
        print("[DEBUG] Converting database row to Scooter object")
        try:
            # Decrypt the encrypted fields from the database
            print("[DEBUG] Decrypting brand")
            brand = decrypt(row[1]).decode()
            print("[DEBUG] Decrypting model")
            model = decrypt(row[2]).decode()
            print("[DEBUG] Decrypting serial_number")
            serial_number = decrypt(row[3]).decode()

            # Create a new Scooter object with the decrypted data
            print("[DEBUG] Creating new Scooter object")
            return Scooter(
                scooter_id=row[0],
                brand=brand,
                model=model,
                serial_number=serial_number,
                top_speed=row[4],
                battery_capacity=row[5],
                state_of_charge=row[6],
                target_soc_min=row[7],
                target_soc_max=row[8],
                location_lat=row[9],
                location_lon=row[10],
                out_of_service=bool(row[11]),
                mileage=row[12],
                last_maint_date=row[13]
            )
        except Exception as e:
            print(f"[ERROR] Failed to convert row to Scooter: {str(e)}")
            raise
