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
                    scooter.last_maint_date.isoformat() if scooter.last_maint_date else None,  # Convert datetime to ISO string
                    scooter.in_service_date.isoformat() if scooter.in_service_date else None   # Convert datetime to ISO string
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

    def search_for_scooters(self, search_term: str, limit: int = 50) -> list[Scooter]:
        """
        Search (partial, case-insensitive) for Scooters across brand, model, and serial_number.
        Uses intelligent field selection and two-phase minimal decryption strategy.
        
        Two-phase approach:
        PHASE 1 - Lightweight Search (minimal decryption):
          1. Analyze search pattern → detect likely field (serial vs brand/model)
          2. Intelligent SQL filtering → fetch only relevant records
          3. Decrypt ONLY search-relevant fields (1-2 fields, not all 3!)
          4. Find matching IDs with early exit
        
        PHASE 2 - Full Decryption (only for matches):
          5. Second query to fetch ONLY matching records
          6. Decrypt all 3 fields ONLY for actual matches

        Args:
            search_term: piece of text to search for ("Xiaomi", "ABC123", etc.)
            limit: Maximum results to return
        """
        if not search_term:
            return []

        search_term_lower = search_term.lower()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Analyze search term to optimize field selection
                # Serial numbers are typically long alphanumeric strings (10-17 chars)
                is_likely_serial = len(search_term) >= 8 and any(c.isdigit() for c in search_term) and any(c.isalpha() for c in search_term)
                
                # Build intelligent SQL query based on search pattern
                if is_likely_serial:
                    # Long alphanumeric → Likely serial number search
                    # Only fetch records with serial numbers
                    cursor.execute('''
                        SELECT scooter_id, brand, model, serial_number
                        FROM Scooter
                        WHERE serial_number IS NOT NULL
                    ''')
                else:
                    # Short text/numeric → Likely brand or model search
                    # Fetch records with brand or model
                    cursor.execute('''
                        SELECT scooter_id, brand, model, serial_number
                        FROM Scooter
                        WHERE brand IS NOT NULL OR model IS NOT NULL
                    ''')
                
                rows = cursor.fetchall()
                matching_ids = []
                
                # PHASE 1: LIGHTWEIGHT SEARCH - Only decrypt search-relevant fields
                for row in rows:
                    scooter_id = row[0]
                    try:
                        # Decrypt ONLY the fields needed for this search type
                        if is_likely_serial:
                            # Only decrypt serial_number field (1 field instead of 3!)
                            searchable = decrypt(row[3].encode() if isinstance(row[3], str) else row[3]).lower() if row[3] else ""
                        else:
                            # Only decrypt brand and model fields (2 fields instead of 3!)
                            brand_val = decrypt(row[1].encode() if isinstance(row[1], str) else row[1]).lower() if row[1] else ""
                            model_val = decrypt(row[2].encode() if isinstance(row[2], str) else row[2]).lower() if row[2] else ""
                            searchable = f"{brand_val} {model_val}"
                        
                        # Check if this row matches the search
                        if search_term_lower in searchable:
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
                # Fetch complete records for matches only
                placeholders = ','.join(['?'] * len(matching_ids))
                cursor.execute(f'''
                    SELECT * FROM Scooter 
                    WHERE scooter_id IN ({placeholders})
                ''', matching_ids)
                
                matching_rows = cursor.fetchall()
                results = []
                
                # Now decrypt all fields only for matches
                for row in matching_rows:
                    try:
                        scooter = self._row_to_scooter(row)
                        results.append(scooter)
                    except Exception as exc:
                        print(f"Error creating scooter {row[0]}: {exc}")
                        continue
                
                return results
                
        except Exception as e:
            print(f"Error in scooter search: {e}")
            return []

    def _row_to_scooter(self, row: tuple) -> Scooter:
        """Convert a database row to a Scooter object"""
        try:
            # The data in the database is stored as strings, so we need to encode it first
            brand = decrypt(row[1].encode() if isinstance(row[1], str) else row[1])
            model = decrypt(row[2].encode() if isinstance(row[2], str) else row[2])
            serial_number = decrypt(row[3].encode() if isinstance(row[3], str) else row[3])

            # Create a new Scooter object with the decrypted data
            # Convert ISO string back to datetime object (if not None)
            last_maint_date = datetime.fromisoformat(row[13]) if row[13] else None
            
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
                last_maint_date=last_maint_date
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
                    scooter.last_maint_date,  # Convert datetime to ISO string,
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
