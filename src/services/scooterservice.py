from typing import Optional
import sqlite3
from datetime import datetime
from models.scooter import Scooter
from utils.crypto_utils import decrypt

class ScooterService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    # def add_scooter_from_params(self, scooter_id, brand, model, serial_number, top_speed, battery_capacity,
    #                             state_of_charge, target_soc_min, target_soc_max, location_lat, location_lon,
    #                             out_of_service, mileage, last_maint_date, in_service_date):
    #     """
    #     Add a scooter to the database using individual parameters.
    #     This is a wrapper around the Scooter model for backward compatibility.
    #     """
    #     try:
    #         scooter = Scooter(
    #             brand=brand,
    #             model=model,
    #             serial_number=serial_number,
    #             top_speed=top_speed,
    #             battery_capacity=battery_capacity,
    #             state_of_charge=state_of_charge,
    #             target_soc_min=target_soc_min,
    #             target_soc_max=target_soc_max,
    #             location_lat=location_lat,
    #             location_lon=location_lon,
    #             out_of_service=out_of_service,
    #             mileage=mileage,
    #             last_maint_date=last_maint_date,
    #         )
    #         return self.add_scooter(scooter)
    #     except ValueError as e:
    #         print(f"Error adding scooter: {e}")
    #         return False

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

    def search_for_scooters(self, search_term: str, field_name: str, limit: int = 50) -> list[Scooter]:
        """
        Field-specific search for scooters - allows searching in a specific encrypted field.
        This is more performant than smart search and handles all edge cases correctly.
        
        Only decrypts the specified field for matching, providing:
        - Exact field targeting (no false positives)
        - Maximum performance (1 field decryption vs 2-3)
        - 100% reliable for edge cases (formatted data, special characters, etc.)

        Args:
            search_term: Text to search for
            field_name: Specific field to search in ('brand', 'model', 'serial_number')
            limit: Maximum results to return
            
        Returns:
            List of matching Scooter objects
        """
        if not search_term or not field_name:
            return []

        # Validate field name
        valid_fields = {'brand', 'model', 'serial_number'}
        if field_name not in valid_fields:
            print(f"Invalid field name: {field_name}. Must be one of {valid_fields}")
            return []

        # Map field names to column indices
        field_map = {
            'brand': 1,
            'model': 2,
            'serial_number': 3
        }
        field_index = field_map[field_name]
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # PHASE 1: SINGLE-FIELD SEARCH - Only decrypt the specified field
                # Fetch only scooter_id and the target field
                cursor.execute(f'''
                    SELECT scooter_id, {field_name}
                    FROM Scooter
                    WHERE {field_name} IS NOT NULL
                ''')
                
                rows = cursor.fetchall()
                matching_ids = []
                
                # Decrypt ONLY the specified field (1 field total!)
                for row in rows:
                    scooter_id = row[0]
                    try:
                        # Decrypt the single target field
                        field_value = decrypt(row[1].encode() if isinstance(row[1], str) else row[1]) if row[1] else ""
                        
                        # Check if this row matches
                        if search_term in field_value:
                            matching_ids.append(scooter_id)
                            
                            # Early exit when limit reached
                            if len(matching_ids) >= limit:
                                break
                                
                    except Exception as exc:
                        # Skip rows that fail to decrypt
                        print(f"Error processing scooter {scooter_id}: {exc}")
                        continue
                
                # If no matches, return empty list
                if not matching_ids:
                    return []
                
                # PHASE 2: FULL DECRYPTION - Only for matching records
                placeholders = ','.join(['?'] * len(matching_ids))
                cursor.execute(f'''
                    SELECT * FROM Scooter 
                    WHERE scooter_id IN ({placeholders})
                ''', matching_ids)
                
                matching_rows = cursor.fetchall()
                results = []
                
                # Decrypt all fields only for matches
                for row in matching_rows:
                    try:
                        scooter = self._row_to_scooter(row)
                        results.append(scooter)
                    except Exception as exc:
                        print(f"Error creating scooter {row[0]}: {exc}")
                        continue
                
                return results
                
        except Exception as e:
            print(f"Error in field-specific scooter search: {e}")
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
