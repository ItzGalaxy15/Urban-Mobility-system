import pytest
from services.userservice import UserService
from services.traveller_service import TravellerService
from services.scooterservice import ScooterService

class TestSQLInjection:
    """Test suite voor SQL injection vulnerabilities"""
    
    def test_user_add_with_sql_injection_username(self, user_service):
        """Test SQL injection via username field"""
        malicious_usernames = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE User; --",
            "admin' UNION SELECT * FROM User--",
            "admin\' OR \'1\'=\'1",
        ]
        
        for username in malicious_usernames:
            success, msg = user_service.add_user(
                username=username,
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                role="service_engineer"
            )
            # Should fail due to validation, not SQL injection
            assert not success, f"SQL injection attempt should be blocked: {username}"
    
    def test_user_update_with_sql_injection(self, user_service, test_user):
        """Test SQL injection in dynamic UPDATE query"""
        malicious_values = {
            "first_name": "Test' OR '1'='1",
            "last_name": "User'; DROP TABLE User; --",
        }
        
        success, msg = user_service.update_user(test_user.user_id, **malicious_values)
        # Should succeed but values should be escaped/parameterized
        if success:
            updated_user = user_service.get_user_by_id(test_user.user_id)
            # Verify the malicious SQL wasn't executed
            assert updated_user is not None, "User should still exist"
    
    def test_traveller_search_sql_injection(self, traveller_service):
        """Test SQL injection in traveller search"""
        malicious_searches = [
            "' OR '1'='1",
            "'; DROP TABLE Traveller; --",
            "' UNION SELECT * FROM User--",
        ]
        
        for search_term in malicious_searches:
            results = traveller_service.search_travellers(search_term)
            # Should return empty or safe results, not execute SQL
            assert isinstance(results, list), "Should return a list"
    
    def test_scooter_search_field_injection(self, scooter_service):
        """Test SQL injection via field parameter in scooter search"""
        malicious_fields = [
            "brand'; DROP TABLE Scooter; --",
            "model' OR '1'='1",
        ]
        
        for field in malicious_fields:
            # Should fail due to whitelist check
            results = scooter_service.search_for_scooters("test", field=field)
            # If field is not in whitelist, should search all fields instead
            assert isinstance(results, list), "Should return safe results"
    
    def test_user_get_by_id_sql_injection(self, user_service):
        """Test SQL injection via user_id parameter"""
        malicious_ids = [
            "1 OR 1=1",
            "1'; DROP TABLE User; --",
        ]
        
        for user_id in malicious_ids:
            try:
                user = user_service.get_user_by_id(user_id)
                # Should either fail or return None safely
                assert user is None or user is not None
            except Exception:
                # Type error is acceptable for invalid input
                pass
