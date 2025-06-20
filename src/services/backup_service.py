import os
import zipfile
import shutil
from datetime import datetime
import sqlite3
from services.userservice import user_service
from services.restore_code_service import restore_code_service
from typing import Tuple
from models.user import User

# Get the absolute path to the project root (one level above src/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_FOLDER = os.path.join(PROJECT_ROOT, 'src')
BACKUP_DIR = os.path.join(SRC_FOLDER, 'backups')
DB_FILE = os.path.join(SRC_FOLDER, 'urban_mobility.db')

class BackupService:
    def __init__(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def create_db_backup(self, user_id):
        # Check permissions
        if user_id == 0:
            # Super admin case - create a User object
            user = User(username="super_admin", password_plain="Admin_123?", role="super")
        else:
            user = user_service.get_user_by_id(user_id)
        
        if not user:
            return False, 'User not found.'
        
        if user.role_plain not in ('system_admin', 'super'):
            return False, 'Only system admin or super admin can create database backups.'

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'db_backup_{timestamp}.zip'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                arcname = os.path.basename(DB_FILE)
                zipf.write(DB_FILE, arcname=arcname)
        except Exception as e:
            return False, f'Failed to create DB zip: {e}'

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if user_id == 0:
            c.execute('''
                INSERT INTO Backup (backup_date, file_path, created_by_user_id)
                VALUES (datetime('now'), ?, NULL)
            ''', (backup_path,))
        else:
            c.execute('''
                INSERT INTO Backup (backup_date, file_path, created_by_user_id)
                VALUES (datetime('now'), ?, ?)
            ''', (backup_path, user_id))
        conn.commit()
        conn.close()

        return True, f'Database backup created successfully'

    def restore_backup_with_code(self, code: str, system_admin_user_id: int) -> Tuple[bool, str]:
        """
        Restore a backup using a restore code.
        Only the system admin who requested the code can use it.
        """
        
        # Check if user is a system admin
        user = user_service.get_user_by_id(system_admin_user_id)
        
        if not user:
            return False, "User not found."
        
        if user.role_plain != 'system_admin':
            return False, "Only system admins can restore backups with codes."

        # Verify the code and get backup_id
        success, message, backup_id = restore_code_service.verify_and_use_code(code, system_admin_user_id)
        
        if not success:
            return False, message

        # Perform the restore
        success, message = self._perform_restore(backup_id, system_admin_user_id)
        
        if success:
            # For system admin restore, only delete the specific backup that was restored
            self._delete_specific_backup(backup_id)
            return True, f"{message} The restored backup has been removed from the database."
        return success, message

    def restore_backup_direct(self, backup_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Restore a backup directly (super admin only).
        This will wipe all older backups.
        """
        print(f"[DEBUG] restore_backup_direct called with backup_id={backup_id}, user_id={user_id}")
        
        # Check if user is a super admin
        if user_id == 0:
            # Super admin case - create a User object
            print(f"[DEBUG] Creating super admin User object")
            user = User(username="super_admin", password_plain="Admin_123?", role="super")
            print(f"[DEBUG] Super admin User object created: {user}")
        else:
            print(f"[DEBUG] Getting user from database with user_id={user_id}")
            user = user_service.get_user_by_id(user_id)
            print(f"[DEBUG] User from database: {user}")
        
        if not user:
            print(f"[DEBUG] User is None or empty")
            return False, "User not found."
        
        print(f"[DEBUG] User role: {user.role_plain}")
        if user.role_plain != 'super':
            print(f"[DEBUG] User role is not super")
            return False, "Only super admins can restore backups directly."
        
        print(f"[DEBUG] User validation passed, proceeding with restore")
        # Perform the restore
        success, message = self._perform_restore(backup_id, user_id)
        print(f"[DEBUG] Restore result: success={success}, message={message}")
        if success:
            # Wipe all older backups (super admin behavior)
            self._wipe_older_backups(backup_id)
            return True, f"{message} All older backups have been wiped."
        return success, message

    def _perform_restore(self, backup_id: int, user_id: int) -> Tuple[bool, str]:
        """Internal method to perform the actual restore operation."""
        print(f"[DEBUG] _perform_restore called with backup_id={backup_id}, user_id={user_id}")
        
        # Get backup details
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT file_path FROM Backup WHERE backup_id = ?', (backup_id,))
        row = c.fetchone()
        conn.close()

        print(f"[DEBUG] Backup query result: {row}")
        if not row:
            print(f"[DEBUG] Backup not found in database")
            return False, "Backup not found."

        backup_path = row[0]
        print(f"[DEBUG] Backup path: {backup_path}")
        if not os.path.exists(backup_path):
            print(f"[DEBUG] Backup file not found on disk")
            return False, "Backup file not found on disk."

        try:
            # All backups are now database backups
            print(f"[DEBUG] Attempting to restore database backup")
            return self._restore_database_backup(backup_path)
        except Exception as e:
            print(f"[DEBUG] Exception during restore: {e}")
            return False, f"Restore failed: {str(e)}"

    def _restore_database_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Restore database from backup."""
        try:
            # Create a backup of current database before restoring
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            current_db_backup = os.path.join(BACKUP_DIR, f'pre_restore_db_{timestamp}.db')
            shutil.copy2(DB_FILE, current_db_backup)

            # Extract and restore database
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(SRC_FOLDER)

            return True, "Database restored successfully"
        except Exception as e:
            return False, f"Database restore failed: {str(e)}"

    def _wipe_older_backups(self, current_backup_id: int):
        """Wipe all backups older than the current one."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Get all backup IDs older than the current one
        c.execute('''
            SELECT backup_id, file_path FROM Backup 
            WHERE backup_id < ? 
            ORDER BY backup_id
        ''', (current_backup_id,))
        
        old_backups = c.fetchall()
        
        for backup_id, file_path in old_backups:
            # Delete file from disk
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass  # Continue even if file deletion fails
            
            # Delete from database
            c.execute('DELETE FROM Backup WHERE backup_id = ?', (backup_id,))
            
            # Delete associated restore codes
            c.execute('DELETE FROM RestoreCode WHERE backup_id = ?', (backup_id,))
        
        conn.commit()
        conn.close()

    def get_backup_list(self):
        """Get list of all backups."""
        return restore_code_service.get_backup_list()

    def generate_restore_code(self, backup_id: int, super_admin_user_id: int, system_admin_user_id: int) -> Tuple[bool, str]:
        """Generate a restore code for a specific backup."""
        return restore_code_service.generate_code(backup_id, system_admin_user_id)

    def get_user_restore_codes(self, system_admin_user_id: int):
        """Get all restore codes for a specific system admin."""
        return restore_code_service.get_user_restore_codes(system_admin_user_id)

    def create_restore_request(self, backup_id: int, system_admin_user_id: int) -> Tuple[bool, str]:
        """Create a restore code request from a system admin."""
        return restore_code_service.create_restore_request(backup_id, system_admin_user_id)

    def get_pending_requests(self):
        """Get all pending restore code requests."""
        return restore_code_service.get_pending_requests()

    def get_user_pending_requests(self, system_admin_user_id: int):
        """Get pending restore code requests for a specific system admin."""
        return restore_code_service.get_user_pending_requests(system_admin_user_id)

    def mark_request_completed(self, request_id: int) -> bool:
        """Mark a restore code request as completed."""
        return restore_code_service.mark_request_completed(request_id)

    def _delete_specific_backup(self, backup_id: int):
        """Delete a specific backup and its associated restore codes."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        try:
            # Get backup file path before deletion
            c.execute('SELECT file_path FROM Backup WHERE backup_id = ?', (backup_id,))
            row = c.fetchone()
            if row:
                file_path = row[0]
                
                # Delete file from disk
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Continue even if file deletion fails
            
            # Delete from database
            c.execute('DELETE FROM Backup WHERE backup_id = ?', (backup_id,))
            
            # Delete associated restore codes
            c.execute('DELETE FROM RestoreCode WHERE backup_id = ?', (backup_id,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error deleting backup: {str(e)}")
        finally:
            conn.close()

backup_service = BackupService() 