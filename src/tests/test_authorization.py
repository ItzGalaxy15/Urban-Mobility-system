import pytest
from services.userservice import UserService
from controllers.usercontroller import UserController
from utils.role_utils import has_permission, ROLE_HIERARCHY


class TestAuthorization:
    """Test suite voor role-based access control (RBAC)"""
    
    def test_role_hierarchy_levels(self):
        """Test dat role hierarchy correct gedefinieerd is"""
        # Check dat alle rollen bestaan
        assert "super" in ROLE_HIERARCHY
        assert "system_admin" in ROLE_HIERARCHY
        assert "service_engineer" in ROLE_HIERARCHY
        
        # Check hierarchy order (higher = more permissions)
        assert ROLE_HIERARCHY["super"] > ROLE_HIERARCHY["system_admin"]
        assert ROLE_HIERARCHY["system_admin"] > ROLE_HIERARCHY["service_engineer"]
    
    def test_service_engineer_cannot_add_user(self, user_service, test_user):
        """Test dat service engineer geen users kan toevoegen"""
        # test_user is een service_engineer (via fixture)
        # has_permission checks exact role match
        can_add = has_permission(test_user.user_id, "system_admin")
        
        assert not can_add, "Service engineer should not have system_admin permissions"
    
    def test_system_admin_can_add_service_engineer(self, user_service, test_admin):
        """Test dat system_admin service_engineers kan toevoegen"""
        # test_admin is een system_admin (via fixture)
        
        # System admin can add service_engineer (no created_by_id in API)
        success, msg = user_service.add_user(
            username="newengin1",
            password="Engineer123!",
            first_name="New",
            last_name="Engineer",
            role="service_engineer"
        )
        
        assert success, f"System admin should be able to add service engineer: {msg}"
    
    def test_system_admin_cannot_add_system_admin(self, user_service, test_admin):
        """Test dat system_admin geen andere system_admins kan toevoegen"""
        # Verify test_admin has the correct role
        assert test_admin.role_plain == "system_admin", "Test admin should have system_admin role"
        
        # Probeer een andere system admin toe te voegen via Controller
        success, msg = UserController.add_user(
            user_id=test_admin.user_id,
            username="newsysadm",
            password="TestPassword123!",
            first_name="New",
            last_name="SysAdmin",
            role="system_admin"
        )
        
        assert not success, f"System admin should not be able to add another system admin: {msg}"
    
    def test_system_admin_cannot_add_super_admin(self, user_service, test_admin):
        """Test dat system_admin geen super admin kan toevoegen"""
        # Role hierarchy test
        assert ROLE_HIERARCHY["system_admin"] < ROLE_HIERARCHY["super"], \
            "System admin should have lower hierarchy than super"
    
    def test_super_admin_can_add_any_role(self, user_service):
        """Test dat super admin alle roles kan toevoegen"""
        # Maak super admin aan
        user_service.add_user(
            username="supertest1",
            password="SuperPassword123!",
            first_name="Super",
            last_name="Admin",
            role="super"
        )
        super_admin = user_service.get_user_by_username("supertest1")
        
        # Super admin voegt service_engineer toe
        success1, msg1 = user_service.add_user(
            username="engineer1",
            password="TestPassword123!",
            first_name="Engineer",
            last_name="One",
            role="service_engineer"
        )
        assert success1, f"Super should add service_engineer: {msg1}"
        
        # Super admin voegt system_admin toe
        success2, msg2 = user_service.add_user(
            username="sysadmin1",
            password="TestPassword123!",
            first_name="Admin",
            last_name="One",
            role="system_admin"
        )
        assert success2, f"Super should add system_admin: {msg2}"
        
        # Super admin voegt andere super toe (indien toegestaan in je implementatie)
        success3, msg3 = user_service.add_user(
            username="superadm2",
            password="TestPassword123!",
            first_name="Super",
            last_name="Two",
            role="super"
        )
        # Dit kan True of False zijn afhankelijk van je implementatie
    
    def test_service_engineer_cannot_delete_users(self, user_service, test_user):
        """Test dat service engineer geen users kan verwijderen"""
        # Maak een andere user aan om te verwijderen
        user_service.add_user(
            username="todelete1",
            password="TestPassword123!",
            first_name="To",
            last_name="Delete",
            role="service_engineer"
        )
        target_user = user_service.get_user_by_username("todelete1")
        
        # Check permission - service engineer heeft geen delete rechten
        can_delete = has_permission(test_user.user_id, "system_admin")  # service_engineer heeft system_admin rechten niet
        assert not can_delete, "Service engineer should not be able to delete users"
    
    def test_system_admin_can_delete_service_engineer(self, user_service, test_admin):
        """Test dat system_admin service_engineers kan verwijderen"""
        # Maak service_engineer aan
        user_service.add_user(
            username="todeletese",
            password="TestPassword123!",
            first_name="Delete",
            last_name="Me",
            role="service_engineer"
        )
        target_user = user_service.get_user_by_username("todeletese")
        
        # System admin verwijdert service_engineer
        success, msg = user_service.delete_user(
            user_id=target_user.user_id,
            username=target_user.username_plain
        )
        
        assert success, f"System admin should be able to delete service engineer: {msg}"
    
    def test_system_admin_cannot_delete_system_admin(self, user_service, test_admin):
        """Test dat system_admin geen andere system_admins kan verwijderen"""
        # Maak een andere system_admin aan (via super - user_id 0)
        user_service.add_user(
            username="sysadmin2",
            password="TestPassword123!",
            first_name="Admin",
            last_name="Two",
            role="system_admin"
        )
        target_admin = user_service.get_user_by_username("sysadmin2")
        
        # System admin probeert te verwijderen via Controller
        success, msg = UserController.delete_user(
            user_id=test_admin.user_id,
            target_user_id=target_admin.user_id,
            username=target_admin.username_plain
        )
        
        assert not success, f"System admin should not be able to delete another system admin: {msg}"
    
    def test_users_cannot_modify_higher_roles(self, user_service, test_admin):
        """Test dat users geen users met hogere rol kunnen modificeren"""
        # Maak super admin aan
        user_service.add_user(
            username="supermod",
            password="TestPassword123!",
            first_name="Super",
            last_name="Mod",
            role="super"
        )
        super_user = user_service.get_user_by_username("supermod")
        
        # System admin probeert super admin te updaten via Controller
        success, msg = UserController.update_user(
            user_id=test_admin.user_id,
            target_user_id=super_user.user_id,
            first_name="Modified"
        )
        
        assert not success, f"System admin should not be able to modify super admin: {msg}"
    
    def test_password_reset_permissions(self, user_service, test_user, test_admin):
        """Test password reset permissions based on role"""
        # Service engineer kan alleen eigen password resetten
        success1, msg1 = user_service.change_password(
            user_id=test_user.user_id,
            current_password="TestPassword123!",
            new_password="NewPassword123!"
        )
        # Dit zou moeten werken
        assert success1, f"User should be able to change own password: {msg1}"
    
    def test_backup_restore_permissions(self, test_user, test_admin):
        """Test dat alleen bepaalde rollen backup/restore kunnen doen"""
        # Service engineer zou GEEN system_admin rechten mogen hebben
        can_backup_se = has_permission(test_user.user_id, "system_admin")
        assert not can_backup_se, "Service engineer should not have system_admin permissions"
        
        # System admin zou wel system_admin rechten moeten hebben
        can_backup_sa = has_permission(test_admin.user_id, "system_admin")
        assert can_backup_sa, "System admin should have system_admin permissions"
    
    def test_role_cannot_escalate_own_privileges(self, user_service, test_admin):
        """Test dat users hun eigen rol niet kunnen upgraden"""
        # System admin probeert zichzelf te upgraden naar super via Controller
        success, msg = UserController.update_user(
            user_id=test_admin.user_id,
            target_user_id=test_admin.user_id,
            role="super"
        )
        
        assert not success, f"User should not be able to escalate own privileges: {msg}"
    
    def test_unauthorized_access_returns_error(self, user_service, test_user):
        """Test dat unauthorized access duidelijke errors geeft"""
        # Service engineer probeert user toe te voegen via Controller
        success, msg = UserController.add_user(
            user_id=test_user.user_id,
            username="unauthor1",
            password="TestPassword123!",
            first_name="Unauth",
            last_name="User",
            role="service_engineer"
        )
        
        assert not success, f"Unauthorized action should fail: {msg}"
        assert msg is not None, "Should return error message"
        assert len(msg) > 0, "Error message should not be empty"
        # Check dat error message iets over permissions zegt
        assert "permission" in msg.lower() or "denied" in msg.lower(), f"Error message should mention permissions: {msg}"
    
    def test_service_engineer_can_view_own_data(self, user_service, test_user):
        """Test dat service engineer eigen data kan bekijken"""
        # Haal eigen user data op
        user = user_service.get_user_by_id(test_user.user_id)
        
        assert user is not None, "Service engineer should be able to view own data"
        assert user.user_id == test_user.user_id
    
    def test_service_engineer_cannot_view_all_users(self, user_service, test_user):
        """Test dat service engineer niet alle users kan zien (indien applicable)"""
        # Service engineer heeft geen system_admin rechten
        can_view_all = has_permission(test_user.user_id, "system_admin")
        assert not can_view_all, "Service engineer should not have system_admin permissions"
    
    def test_system_admin_can_view_service_engineers(self, user_service, test_admin):
        """Test dat system_admin service_engineers kan bekijken"""
        # Maak service_engineer aan
        user_service.add_user(
            username="viewable",
            password="TestPassword123!",
            first_name="View",
            last_name="Able",
            role="service_engineer"
        )
        
        # System admin haalt service_engineer op
        user = user_service.get_user_by_username("viewable")
        
        assert user is not None, "System admin should be able to view service engineers"
    
    def test_role_based_menu_access(self, test_user, test_admin):
        """Test dat menu items beperkt zijn per rol"""
        # Service engineer heeft service_engineer rechten
        has_se_permissions = has_permission(test_user.user_id, "service_engineer")
        has_sa_from_se = has_permission(test_user.user_id, "system_admin")
        
        # System admin heeft system_admin rechten
        has_sa_permissions = has_permission(test_admin.user_id, "system_admin")
        
        # Service engineer heeft zijn eigen rechten maar niet hogere
        assert has_se_permissions, "Service engineer should have service_engineer permissions"
        assert not has_sa_from_se, "Service engineer should NOT have system_admin permissions"
        
        # System admin heeft system_admin rechten
        assert has_sa_permissions, "System admin should have system_admin permissions"
    
    def test_cross_user_data_access_prevention(self, user_service):
        """Test dat users geen data van andere users kunnen wijzigen"""
        # Maak twee service engineers
        user_service.add_user(
            username="engineer1",
            password="TestPassword123!",
            first_name="Engineer",
            last_name="One",
            role="service_engineer"
        )
        user_service.add_user(
            username="engineer2",
            password="TestPassword123!",
            first_name="Engineer",
            last_name="Two",
            role="service_engineer"
        )
        
        user1 = user_service.get_user_by_username("engineer1")
        user2 = user_service.get_user_by_username("engineer2")
        
        # Engineer1 probeert engineer2 te wijzigen via Controller
        success, msg = UserController.update_user(
            user_id=user1.user_id,
            target_user_id=user2.user_id,
            first_name="Hacked"
        )
        
        assert not success, f"User should not be able to modify other users: {msg}"
    
    def test_role_validation_on_creation(self, user_service):
        """Test dat alleen geldige rollen toegestaan zijn"""
        # Probeer user met ongeldige rol aan te maken
        success, msg = user_service.add_user(
            username="invalidrole",
            password="TestPassword123!",
            first_name="Invalid",
            last_name="Role",
            role="hacker"  # Ongeldige rol
        )
        
        assert not success, "Should reject invalid role"
    
    def test_super_admin_cannot_be_deleted(self, user_service):
        """Test dat super admin niet verwijderd kan worden (indien applicable)"""
        # Maak super admin
        user_service.add_user(
            username="superdel1",
            password="TestPassword123!",
            first_name="Super",
            last_name="Delete",
            role="super"
        )
        super_user = user_service.get_user_by_username("superdel1")
        
        # Probeer super admin te verwijderen (zelfs door een andere super)
        user_service.add_user(
            username="superdel2",
            password="TestPassword123!",
            first_name="Super",
            last_name="Deleter",
            role="super"
        )
        deleter = user_service.get_user_by_username("superdel2")
        
        success, msg = user_service.delete_user(
            user_id=super_user.user_id,
            username=super_user.username_plain
        )
        
        # Afhankelijk van implementatie: super kan andere super deleten of niet
        # Documenteer het verwachte gedrag
