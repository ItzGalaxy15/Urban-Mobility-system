import pytest
import sqlite3
from utils.crypto_utils import encrypt, decrypt, hash_password, check_password
from services.userservice import UserService
from services.traveller_service import TravellerService
from services.scooterservice import ScooterService
from models.scooter import Scooter


class TestEncryption:
    """Test suite voor encryptie en password hashing"""
    
    def test_encryption_roundtrip(self):
        """Test dat encrypt -> decrypt de originele waarde teruggeeft"""
        test_values = [
            "testuser",
            "Amsterdam",
            "test@example.com",
            "TestBrand123",
            "12345",
        ]
        
        for value in test_values:
            encrypted = encrypt(value)
            decrypted = decrypt(encrypted)
            assert decrypted == value, f"Roundtrip failed for: {value}"
            assert encrypted != value, f"Value should be encrypted: {value}"
    
    def test_encryption_consistency(self):
        """Test dat dezelfde input verschillende encrypted waarden geeft (door IV/nonce)"""
        test_value = "consistent_test"
        encrypted1 = encrypt(test_value)
        encrypted2 = encrypt(test_value)
        
        # Encrypted waarden zouden verschillend moeten zijn (door random IV)
        assert encrypted1 != encrypted2, "Encrypted values should differ due to IV"
        
        # Maar beide moeten decrypten naar de originele waarde
        assert decrypt(encrypted1) == test_value
        assert decrypt(encrypted2) == test_value
    
    def test_password_hashing(self):
        """Test bcrypt password hashing"""
        password = "SecurePass123!"
        hashed = hash_password(password)
        
        # Hash should be different from password
        assert hashed != password, "Hashed password should differ from plaintext"
        
        # Hash should be bcrypt format (starts with $2b$) - can be bytes or string
        if isinstance(hashed, bytes):
            assert hashed.startswith(b"$2b$"), "Should use bcrypt format"
        else:
            assert hashed.startswith("$2b$"), "Should use bcrypt format"
        
        # Check should succeed with correct password
        assert check_password(password, hashed), "Password check should succeed"
        
        # Check should fail with wrong password
        assert not check_password("WrongPass123!", hashed), "Wrong password should fail"
    
    def test_password_hashing_uniqueness(self):
        """Test dat dezelfde password verschillende hashes geeft (door salt)"""
        password = "SamePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should differ due to salt
        assert hash1 != hash2, "Password hashes should differ due to salt"
        
        # Both should verify correctly
        assert check_password(password, hash1)
        assert check_password(password, hash2)
    
    def test_user_field_encryption(self, user_service, test_db_path):
        """Test dat user fields encrypted zijn in de database"""
        # Voeg een user toe
        success, msg = user_service.add_user(
            username="enctest1",
            password="TestPass123!",
            first_name="Encrypted",
            last_name="User",
            role="service_engineer"
        )
        assert success, f"Failed to add user: {msg}"
        
        # Haal de user op via service (decrypted)
        user = user_service.get_user_by_username("enctest1")
        assert user is not None
        assert user.username_plain == "enctest1"
        assert user.first_name_plain == "Encrypted"
        assert user.last_name_plain == "User"
        
        # Check database directly - data should be encrypted
        conn = sqlite3.connect(test_db_path)
        c = conn.cursor()
        c.execute("SELECT username, first_name, last_name FROM User WHERE user_id = ?", (user.user_id,))
        row = c.fetchone()
        conn.close()
        
        # Raw DB values should NOT equal plaintext
        assert row[0] != "enctest1", "Username should be encrypted in DB"
        assert row[1] != "Encrypted", "First name should be encrypted in DB"
        assert row[2] != "User", "Last name should be encrypted in DB"
        
        # Raw DB values should decrypt correctly
        assert decrypt(row[0]) == "enctest1"
        assert decrypt(row[1]) == "Encrypted"
        assert decrypt(row[2]) == "User"
    
    def test_traveller_field_encryption(self, traveller_service, test_db_path):
        """Test dat traveller fields encrypted zijn in de database"""
        from datetime import date, timedelta
        
        # Maak een traveller aan
        birthday = (date.today() - timedelta(days=20*365)).strftime("%Y-%m-%d")
        success, msg = traveller_service.add_traveller(
            first_name="John",
            last_name="Doe",
            birthday=birthday,
            zip_code="1234AB",
            city="Amsterdam",
            email="john@example.com",
            mobile_phone="+31-6-12345678",
            house_number="42",
            driving_license_no="AB1234567",
            gender="male",
            street_name="TestStreet"
        )
        assert success, f"Failed to add traveller: {msg}"
        
        # Haal de traveller op via email (we don't get ID back)
        traveller = traveller_service.search_travellers("john@example.com")[0] if traveller_service.search_travellers("john@example.com") else None
        assert traveller is not None
        assert traveller.first_name_plain == "John"
        assert traveller.email_plain == "john@example.com"
        
        # Check database directly - data should be encrypted
        conn = sqlite3.connect(test_db_path)
        c = conn.cursor()
        c.execute("SELECT first_name, email FROM Traveller WHERE traveller_id = ?", (traveller.traveller_id,))
        row = c.fetchone()
        conn.close()
        
        # Raw DB values should NOT equal plaintext
        assert row[0] != "John", "First name should be encrypted in DB"
        assert row[1] != "john@example.com", "Email should be encrypted in DB"
        
        # Raw DB values should decrypt correctly
        assert decrypt(row[0]) == "John"
        assert decrypt(row[1]) == "john@example.com"
    
    def test_scooter_field_encryption(self, scooter_service, test_db_path):
        """Test dat scooter fields encrypted zijn in de database"""
        from models.scooter import Scooter
        
        # Maak een scooter aan
        scooter = Scooter(
            brand="TestBrand",
            model="TestModel",
            serial_number="ABC1234567",
            top_speed=25,
            battery_capacity=3000,
            state_of_charge=80,
            target_soc_min=20,
            target_soc_max=90,
            location_lat=52.3676,
            location_lon=4.9041
        )
        success = scooter_service.add_scooter(scooter)
        assert success, "Failed to add scooter"
        
        # Haal alle scooters op en vind onze scooter
        scooters = scooter_service.get_all_scooters()
        assert len(scooters) > 0, "Should find at least one scooter"
        found_scooter = [s for s in scooters if s.serial_number_plain == "ABC1234567"][0]
        assert found_scooter.brand_plain == "TestBrand"
        assert found_scooter.model_plain == "TestModel"
        assert found_scooter.serial_number_plain == "ABC1234567"
        
        # Check database directly - data should be encrypted
        conn = sqlite3.connect(test_db_path)
        c = conn.cursor()
        c.execute("SELECT brand, model, serial_number FROM Scooter WHERE scooter_id = ?", (found_scooter.scooter_id,))
        row = c.fetchone()
        conn.close()
        
        # Raw DB values should NOT equal plaintext
        assert row[0] != "TestBrand", "Brand should be encrypted in DB"
        assert row[1] != "TestModel", "Model should be encrypted in DB"
        assert row[2] != "ABC1234567", "Serial number should be encrypted in DB"
        
        # Raw DB values should decrypt correctly
        assert decrypt(row[0]) == "TestBrand"
        assert decrypt(row[1]) == "TestModel"
        assert decrypt(row[2]) == "ABC1234567"
    
    def test_encryption_with_special_characters(self):
        """Test encryption met speciale karakters"""
        special_values = [
            "user@domain.com",
            "Test's Name",
            "Street-Name 123",
            "City (Amsterdam)",
            "Value with \"quotes\"",
        ]
        
        for value in special_values:
            encrypted = encrypt(value)
            decrypted = decrypt(encrypted)
            assert decrypted == value, f"Special chars failed for: {value}"
    
    def test_encryption_with_unicode(self):
        """Test encryption met unicode karakters"""
        unicode_values = [
            "Amélie",
            "München",
            "José",
            "北京",  # Beijing in Chinese
            "Москва",  # Moscow in Russian
        ]
        
        for value in unicode_values:
            encrypted = encrypt(value)
            decrypted = decrypt(encrypted)
            assert decrypted == value, f"Unicode failed for: {value}"
    
    def test_encryption_with_empty_string(self):
        """Test encryption met lege string"""
        encrypted = encrypt("")
        decrypted = decrypt(encrypted)
        assert decrypted == "", "Empty string should roundtrip"
    
    def test_password_verification_timing(self):
        """Test dat password verificatie consistent tijd neemt (timing attack protection)"""
        import time
        
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Measure time for correct password
        start = time.time()
        check_password(password, hashed)
        correct_time = time.time() - start
        
        # Measure time for incorrect password
        start = time.time()
        check_password("WrongPassword123!", hashed)
        incorrect_time = time.time() - start
        
        # Times should be similar (bcrypt is designed to be constant-time)
        # We allow some variance, but not orders of magnitude
        time_ratio = max(correct_time, incorrect_time) / min(correct_time, incorrect_time)
        assert time_ratio < 10, "Password check timing should be consistent"
    
    def test_user_password_storage(self, user_service, test_db_path):
        """Test dat passwords gehashed zijn in de database, niet encrypted"""
        password = "StoredPass123!"
        success, msg = user_service.add_user(
            username="pwdtest1",
            password=password,
            first_name="Test",
            last_name="User",
            role="service_engineer"
        )
        assert success, f"Failed to add user: {msg}"
        
        # Get user
        user = user_service.get_user_by_username("pwdtest1")
        
        # Check database directly
        conn = sqlite3.connect(test_db_path)
        c = conn.cursor()
        c.execute("SELECT password_hash FROM User WHERE user_id = ?", (user.user_id,))
        row = c.fetchone()
        conn.close()
        
        stored_hash = row[0]
        
        # Hash should not be the plaintext password (handle bytes or str)
        if isinstance(stored_hash, bytes):
            assert stored_hash != password.encode(), "Password should not be stored in plaintext"
            # Hash should be bcrypt format
            assert stored_hash.startswith(b"$2b$"), "Password should be bcrypt hashed"
        else:
            assert stored_hash != password, "Password should not be stored in plaintext"
            # Hash should be bcrypt format
            assert stored_hash.startswith("$2b$"), "Password should be bcrypt hashed"
        
        # Should verify correctly
        assert check_password(password, stored_hash), "Password should verify"
        
    def test_encryption_key_consistency(self):
        """Test dat encryption key consistent is across calls"""
        # Encrypt een waarde
        value = "consistency_test"
        encrypted = encrypt(value)
        
        # Decrypt should work
        decrypted = decrypt(encrypted)
        assert decrypted == value
        
        # Encrypt een andere waarde
        value2 = "another_value"
        encrypted2 = encrypt(value2)
        decrypted2 = decrypt(encrypted2)
        assert decrypted2 == value2
        
        # Eerste encrypted value should still decrypt correctly
        assert decrypt(encrypted) == value
    
    def test_encrypted_data_not_readable(self, user_service, test_db_path):
        """Test dat encrypted data in DB niet leesbaar is zonder decryptie"""
        # Voeg user toe met bekende data
        success, msg = user_service.add_user(
            username="readable1",
            password="TestPass123!",
            first_name="Readable",
            last_name="Test",
            role="service_engineer"
        )
        assert success
        
        user = user_service.get_user_by_username("readable1")
        
        # Lees raw data uit DB
        conn = sqlite3.connect(test_db_path)
        c = conn.cursor()
        c.execute("SELECT username, first_name, last_name FROM User WHERE user_id = ?", (user.user_id,))
        row = c.fetchone()
        conn.close()
        
        # Raw data should not contain readable plaintext
        raw_username = row[0]
        raw_firstname = row[1]
        raw_lastname = row[2]
        
        # Convert bytes to str for comparison if needed
        username_str = raw_username.decode() if isinstance(raw_username, bytes) else raw_username
        firstname_str = raw_firstname.decode() if isinstance(raw_firstname, bytes) else raw_firstname
        
        # Should not be readable as plaintext
        assert "readable1" not in username_str.lower(), "Username should not be readable in DB"
        assert "readable" not in firstname_str.lower(), "First name should not be readable in DB"
        
        # Should be base64-like or binary data
        assert len(username_str) > len("readable1"), "Encrypted data should be longer"
