from typing import Optional
import sqlite3
from models.scooter import Scooter
from utils.crypto_utils import decrypt

class ScooterService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def add_scooter_from_params(self, scooter_id, brand, model, serial_number, top_speed, battery_capacity,
                                state_of_charge, target_soc_min, target_soc_max, location_lat, location_lon,
                                out_of_service, mileage, last_maint_date, in_service_date):
        """
        Add a scooter to the database using individual parameters.
        This is a wrapper around the Scooter model for backward compatibility.
        """
        try:
            scooter = Scooter(
                brand=brand,
                model=model,
                serial_number=serial_number,
                top_speed=top_speed,
                battery_capacity=battery_capacity,
                state_of_charge=state_of_charge,
                target_soc_min=target_soc_min,
                target_soc_max=target_soc_max,
                location_lat=location_lat,
                location_lon=location_lon,
                out_of_service=out_of_service,
                mileage=mileage,
                last_maint_date=last_maint_date,
                in_service_date=in_service_date
            )
            return self.add_scooter(scooter)
        except ValueError as e:
            print(f"Error adding scooter: {e}")
            return False

    def add_scooter(self, scooter: Scooter) -> bool:
        """Add a new scooter to the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Scooter (
                        brand, model, serial_number, top_speed,
                        battery_capacity, state_of_charge, target_soc_min,
                        target_soc_max, location_lat, location_lon,
                        out_of_service, mileage, last_maint_date, in_service_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
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
                conn.commit()
                return True
        except sqlite3.Error as e:
            return False
        except Exception as e:
            return False

    def get_scooter_by_id(self, scooter_id: int) -> Optional[Scooter]:
        """Retrieve a scooter by its ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Scooter WHERE scooter_id = ?", (scooter_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_scooter(row)
                return None
        except sqlite3.Error as e:
            return None
        except Exception as e:
            return None
    
    def get_all_scooters(self) -> list[Scooter]:
        """Retrieve all scooters from the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Scooter")
                rows = cursor.fetchall()
                return [self._row_to_scooter(row) for row in rows]
        except sqlite3.Error as e:
            return []
        except Exception as e:
            return []

    def _row_to_scooter(self, row: tuple) -> Scooter:
        """Convert a database row to a Scooter object"""
        try:
            # The data in the database is stored as strings, so we need to encode it first
            brand = decrypt(row[1].encode() if isinstance(row[1], str) else row[1])
            model = decrypt(row[2].encode() if isinstance(row[2], str) else row[2])
            serial_number = decrypt(row[3].encode() if isinstance(row[3], str) else row[3])

            # Create a new Scooter object with the decrypted data
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
            raise

    def update_scooter(self, scooter: Scooter) -> bool:
        """Update an existing scooter in the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Scooter SET
                        brand = ?, model = ?, serial_number = ?,
                        top_speed = ?, battery_capacity = ?, state_of_charge = ?,
                        target_soc_min = ?, target_soc_max = ?,
                        location_lat = ?, location_lon = ?,
                        out_of_service = ?, mileage = ?, last_maint_date = ?
                    WHERE scooter_id = ?
                """, (
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
                    scooter.scooter_id
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            return False
        except Exception as e:
            return False
    
    def delete_scooter(self, scooter_id: int) -> bool:
        """Delete a scooter from the database by its ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Scooter WHERE scooter_id = ?", (scooter_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            return False
        except Exception as e:
            return False
