from services.backup_service import backup_service
from services.restore_code_service import restore_code_service
from services.userservice import user_service
from utils.log_decorator import log_action
from utils.role_utils import require_role
from typing import Tuple, List, Optional, Dict, Any

class BackupController:
    
    @staticmethod
    @log_action("Create database backup -> {msg}")
    @require_role("system_admin", "super")
    def create_database_backup(user_id: int) -> Tuple[bool, str]:
        """Create a backup of the database."""
        return backup_service.create_db_backup(user_id)
    
    @staticmethod
    @log_action("Get backup list -> {msg}")
    @require_role("system_admin", "super")
    def get_backup_list(user_id: int) -> List[Dict[str, Any]]:
        """Get a list of all backups."""
        return backup_service.get_backup_list()
    
    @staticmethod
    @log_action("Create restore request -> {msg}")
    @require_role("system_admin")
    def create_restore_request(user_id: int, backup_id: int) -> Tuple[bool, str]:
        """Create a restore request for a system admin."""
        return backup_service.create_restore_request(backup_id, user_id)
    
    @staticmethod
    @log_action("Get pending requests -> {msg}")
    @require_role("super")
    def get_pending_requests(user_id: int) -> List[Dict[str, Any]]:
        """Get all pending restore requests (super admin only)."""
        return backup_service.get_pending_requests()
    
    @staticmethod
    @log_action("Generate restore code -> {msg}")
    @require_role("super")
    def generate_restore_code(user_id: int, backup_id: int, system_admin_user_id: int) -> Tuple[bool, str]:
        """Generate a restore code for a system admin (super admin only)."""
        return backup_service.generate_restore_code(backup_id, user_id, system_admin_user_id)
    
    @staticmethod
    @log_action("Mark request completed -> {msg}")
    @require_role("super")
    def mark_request_completed(request_id: int, user_id: int) -> bool:
        """Mark a restore request as completed (super admin only)."""
        return backup_service.mark_request_completed(request_id)
    
    @staticmethod
    @log_action("Get user restore codes -> {msg}")
    @require_role("system_admin")
    def get_user_restore_codes(system_admin_user_id: int) -> List[Dict[str, Any]]:
        """Get all restore codes for a specific system admin."""
        return backup_service.get_user_restore_codes(system_admin_user_id)
    
    @staticmethod
    @log_action("Restore backup with code -> {msg}")
    @require_role("system_admin")
    def restore_backup_with_code(user_id: int, code: str) -> Tuple[bool, str]:
        """Restore a backup using a restore code (system admin only)."""
        return backup_service.restore_backup_with_code(code, user_id)
    
    @staticmethod
    @log_action("Restore backup direct -> {msg}")
    @require_role("super")
    def restore_backup_direct(backup_id: int, user_id: int) -> Tuple[bool, str]:
        """Restore a backup directly (super admin only)."""
        return backup_service.restore_backup_direct(backup_id, user_id)
    
    @staticmethod
    @log_action("Get user pending requests -> {msg}")
    @require_role("system_admin")
    def get_user_pending_requests(system_admin_user_id: int) -> List[Dict[str, Any]]:
        """Get pending restore requests for a specific system admin."""
        return backup_service.get_user_pending_requests(system_admin_user_id) 