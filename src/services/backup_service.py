import os
import zipfile
import shutil
from datetime import datetime
import sqlite3
from services.userservice import user_service
from services.restore_code_service import restore_code_service
from typing import Tuple

# Get the absolute path to the project root (one level above src/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_FOLDER = os.path.join(PROJECT_ROOT, 'src')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')
DB_FILE = os.path.join(SRC_FOLDER, 'urban_mobility.db')

class BackupService:
    def __init__(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

    def create_backup(self, user_id):
        # Check permissions
        user = user_service.get_user_by_id(user_id) if user_id != 0 else {'role': 'super'}
        if not user or user['role'] not in ('system_admin', 'super'):
            return False, 'Only system admin or super admin can create backups.'

        # Create timestamped backup filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'src_backup_{timestamp}.zip'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        # Zip the src folder, excluding src/backups/, __pycache__, .git
        def exclude_filter(filepath):
            rel = os.path.relpath(filepath, SRC_FOLDER)
            parts = rel.split(os.sep)
            if parts[0] == 'backups':
                return True
            if '__pycache__' in parts or '.git' in parts:
                return True
            return False

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(SRC_FOLDER):
                    # Exclude unwanted dirs
                    dirs[:] = [d for d in dirs if not exclude_filter(os.path.join(root, d))]
                    for file in files:
                        filepath = os.path.join(root, file)
                        if exclude_filter(filepath):
                            continue
                        arcname = os.path.relpath(filepath, SRC_FOLDER)
                        zipf.write(filepath, arcname=arcname)
        except Exception as e:
            return False, f'Failed to create zip: {e}'

        # Record in Backup table (in the src/urban_mobility.db database)
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

        return True, f'Backup created successfully'

    def create_db_backup(self, user_id):
        # Check permissions
        user = user_service.get_user_by_id(user_id) if user_id != 0 else {'role': 'super'}
        if not user or user['role'] not in ('system_admin', 'super'):
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
        if not user or user['role'] != 'system_admin':
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
        # Check if user is a super admin
        user = user_service.get_user_by_id(user_id) if user_id != 0 else {'role': 'super'}
        if not user or user['role'] != 'super':
            return False, "Only super admins can restore backups directly."

        # Perform the restore
        success, message = self._perform_restore(backup_id, user_id)
        if success:
            # Wipe all older backups (super admin behavior)
            self._wipe_older_backups(backup_id)
            return True, f"{message} All older backups have been wiped."
        return success, message

    def _perform_restore(self, backup_id: int, user_id: int) -> Tuple[bool, str]:
        """Internal method to perform the actual restore operation."""
        # Get backup details
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT file_path FROM Backup WHERE backup_id = ?', (backup_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            return False, "Backup not found."

        backup_path = row[0]
        if not os.path.exists(backup_path):
            return False, "Backup file not found on disk."

        try:
            # Determine if this is a database backup or full system backup
            if 'db_backup_' in backup_path:
                return self._restore_database_backup(backup_path)
            else:
                return self._restore_system_backup(backup_path)
        except Exception as e:
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

    def _restore_system_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Restore full system from backup."""
        try:
            # Create a backup of current system before restoring
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            current_system_backup = os.path.join(BACKUP_DIR, f'pre_restore_system_{timestamp}.zip')
            
            with zipfile.ZipFile(current_system_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(SRC_FOLDER):
                    # Exclude backups directory and current backup
                    dirs[:] = [d for d in dirs if d != 'backups']
                    for file in files:
                        filepath = os.path.join(root, file)
                        if 'backups' in filepath or filepath == backup_path:
                            continue
                        arcname = os.path.relpath(filepath, SRC_FOLDER)
                        zipf.write(filepath, arcname=arcname)

            # Extract backup to temporary location
            temp_extract_dir = os.path.join(BACKUP_DIR, 'temp_restore')
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)
            os.makedirs(temp_extract_dir)

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_extract_dir)

            # Copy files from temp location to src folder, excluding the database
            for item in os.listdir(temp_extract_dir):
                src_item = os.path.join(temp_extract_dir, item)
                dst_item = os.path.join(SRC_FOLDER, item)
                
                # Skip the database file to preserve backup records
                if item == 'urban_mobility.db':
                    continue
                
                if os.path.isdir(src_item):
                    if os.path.exists(dst_item):
                        shutil.rmtree(dst_item)
                    shutil.copytree(src_item, dst_item)
                else:
                    shutil.copy2(src_item, dst_item)

            # Clean up temp directory
            shutil.rmtree(temp_extract_dir)

            return True, "System restored successfully (database preserved)"
        except Exception as e:
            return False, f"System restore failed: {str(e)}"

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