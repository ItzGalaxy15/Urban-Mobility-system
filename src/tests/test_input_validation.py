import pytest
from services.userservice import UserService
from services.traveller_service import TravellerService
from models.scooter import Scooter
from utils.validation import validate_email, validate_birthday, validate_city, validate_gender, validate_first_name, validate_last_name

class TestInputValidation:
    """Test suite voor input validatie"""
    
    def test_username_format_validation(self, user_service):
        """Test username regex validatie"""
        invalid_usernames = [
            "short",  # Te kort (< 8 chars)
            "toolongname1",  # Te lang (> 10 chars)
            "123start",  # Mag niet met cijfer beginnen
            "user name",  # Geen spaties
            "user@name",  # Geen @ toegestaan
        ]
        
        for username in invalid_usernames:
            valid, msg = user_service.validate_username(username)
            assert not valid, f"Invalid username should be rejected: {username}"
        
        valid_usernames = [
            "username1",
            "_username",
            "User_Name",
        ]
        
        for username in valid_usernames:
            valid, msg = user_service.validate_username(username)
            assert valid, f"Valid username should be accepted: {username}"
    
    def test_password_complexity_requirements(self, user_service):
        """Test password complexity validatie"""
        invalid_passwords = [
            "short",  # Te kort
            "NoDigits!",  # Geen cijfer
            "nouppercas3!",  # Geen hoofdletter
            "NOLOWERCASE3!",  # Geen kleine letter
            "NoSpecialChar1",  # Geen special char
            "Invalid Spaces1!",  # Spaties niet toegestaan
        ]
        
        for password in invalid_passwords:
            valid, msg = user_service.validate_password(password)
            assert not valid, f"Invalid password should be rejected: {password}"
        
        valid_passwords = [
            "ValidPass123!",
            "Str0ng_Passw0rd",
            "C0mpl3x!Pass",
        ]
        
        for password in valid_passwords:
            valid, msg = user_service.validate_password(password)
            assert valid, f"Valid password should be accepted: {password}"
    
    def test_email_format_validation(self):
        """Test email validatie"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
        ]
        
        for email in invalid_emails:
            valid, msg = validate_email(email)
            assert not valid, f"Invalid email should be rejected: {email}"
        
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
        ]
        
        for email in valid_emails:
            valid, msg = validate_email(email)
            assert valid, f"Valid email should be accepted: {email}"
    
    def test_date_validation_and_age_check(self):
        """Test birthday validatie en 18+ check"""
        from datetime import date, timedelta
        
        # Te jong (< 18)
        today = date.today()
        too_young = (today - timedelta(days=17*365)).strftime("%Y-%m-%d")
        valid, msg = validate_birthday(too_young)
        assert not valid, "Under 18 should be rejected"
        
        # Ongeldige datum
        invalid, msg = validate_birthday("2023-13-45")
        assert not invalid, "Invalid date should be rejected"
        
        # Geldige datum (18+)
        old_enough = (today - timedelta(days=20*365)).strftime("%Y-%m-%d")
        valid, msg = validate_birthday(old_enough)
        assert valid, "18+ should be accepted"
    
    def test_numeric_range_validation(self):
        """Test numeric range validatie voor scooter"""
        # Invalid top_speed
        with pytest.raises(ValueError):
            Scooter(
                brand="TestBrand",
                model="TestModel",
                serial_number="ABC1234567",
                top_speed=100,  # Te hoog
                battery_capacity=3000,
                state_of_charge=50,
                target_soc_min=20,
                target_soc_max=80,
                location_lat=52.0,
                location_lon=4.0
            )
        
        # Invalid battery_capacity
        with pytest.raises(ValueError):
            Scooter(
                brand="TestBrand",
                model="TestModel",
                serial_number="ABC1234567",
                top_speed=25,
                battery_capacity=10000,  # Te hoog
                state_of_charge=50,
                target_soc_min=20,
                target_soc_max=80,
                location_lat=52.0,
                location_lon=4.0
            )
    
    def test_whitelist_validation(self):
        """Test whitelist validatie voor city en gender"""
        # Invalid city
        valid, msg = validate_city("InvalidCity")
        assert not valid, "City not in whitelist should be rejected"
        
        # Valid city
        valid, msg = validate_city("Amsterdam")
        assert valid, "City in whitelist should be accepted"
        
        # Invalid gender
        valid, msg = validate_gender("other")
        assert not valid, "Gender not in whitelist should be rejected"
        
        # Valid gender
        valid, msg = validate_gender("male")
        assert valid, "Valid gender should be accepted"
    
    def test_null_byte_rejection(self, user_service):
        """Test NULL byte handling"""
        username_with_null = "user\x00name"
        valid, msg = user_service.validate_username(username_with_null)
        # Should be rejected by regex (NULL byte not in allowed chars)
        assert not valid, "NULL byte should be rejected"
    
    def test_leading_trailing_spaces_rejection(self):
        """Test leading/trailing spaces rejection"""
        # Names with spaces
        valid, msg = validate_first_name("  John")
        assert not valid, "Leading spaces should be rejected"
        
        valid, msg = validate_first_name("John  ")
        assert not valid, "Trailing spaces should be rejected"
        
        # Valid name
        valid, msg = validate_first_name("John")
        assert valid, "Valid name should be accepted"
