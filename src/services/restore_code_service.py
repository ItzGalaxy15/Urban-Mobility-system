import sqlite3
import secrets
import string
from datetime import datetime
from typing import Tuple, List, Optional
from models.restore_code import RestoreCode
from services.userservice import user_service
from utils.crypto_utils import check_password, decrypt, hash_password
import uuid

class RestoreCodeService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Return a new SQLite connection (caller closes it)."""
        return sqlite3.connect(self.db_path)

    def generate_code(self, backup_id: int, system_admin_user_id: int) -> Tuple[bool, str]:
        """
        Generate a restore code for a specific backup and system admin.
        Only super admins can generate codes.
        """
        # Note: This method is called by super admins, so we don't need to check permissions here
        # The permission check is done in the menu function

        # Verify the backup exists
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT backup_id FROM Backup WHERE backup_id = ?', (backup_id,))
        if not c.fetchone():
            conn.close()
            return False, "Backup not found."

        # Check if there's a pending request for this backup and system admin
        c.execute('''
            SELECT code_id FROM RestoreCode 
            WHERE backup_id = ? AND system_admin_user_id = ? AND code LIKE 'PENDING_%'
        ''', (backup_id, system_admin_user_id))
        
        pending_request = c.fetchone()
        if not pending_request:
            conn.close()
            return False, "No pending request found for this backup and system admin."

        # Generate a secure random code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # Hash the code for storage
        code_hash = hash_password(code)
        
        try:
            # Update the pending request with the actual code
            c.execute('''
                UPDATE RestoreCode 
                SET code = ?, is_used = 0
                WHERE code_id = ?
            ''', (code_hash, pending_request[0]))
            conn.commit()
            conn.close()
            return True, code
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Failed to generate restore code: {str(e)}"

    def verify_and_use_code(self, code: str, system_admin_user_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        Verify a restore code and return the backup_id if valid.
        Only the system admin who requested the code can use it.
        """
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            # Get all restore codes for this system admin (excluding pending requests)
            c.execute('''
                SELECT code, backup_id, is_used FROM RestoreCode 
                WHERE system_admin_user_id = ? AND code NOT LIKE 'PENDING_%'
            ''', (system_admin_user_id,))
            
            rows = c.fetchall()
            for row in rows:
                stored_code, backup_id, is_used = row
                
                # Check if code is already used
                if is_used:
                    continue
                
                # Verify the code using bcrypt
                try:
                    if check_password(code, stored_code):
                        # Mark as used
                        c.execute('''
                            UPDATE RestoreCode SET is_used = 1 
                            WHERE code = ? AND system_admin_user_id = ?
                        ''', (stored_code, system_admin_user_id))
                        conn.commit()
                        conn.close()
                        return True, "Code verified successfully", backup_id
                except Exception as e:
                    # If bcrypt verification fails, continue to next code
                    continue
            
            conn.close()
            return False, "Invalid or already used code", None
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Error verifying code: {str(e)}", None

    def get_backup_list(self) -> List[dict]:
        """Get a list of all backups with their details."""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT b.backup_id, b.backup_date, b.file_path, b.created_by_user_id,
                   u.first_name, u.last_name, u.role
            FROM Backup b
            LEFT JOIN User u ON b.created_by_user_id = u.user_id
            ORDER BY b.backup_date DESC
        ''')
        
        rows = c.fetchall()
        conn.close()
        
        backups = []
        for row in rows:
            backup_id, backup_date, file_path, created_by_user_id, first_name, last_name, role = row
            
            # Decrypt user data if available
            if first_name and last_name and role:
                try:
                    first_name = decrypt(first_name)
                    last_name = decrypt(last_name)
                    role = decrypt(role)
                    creator_name = f"{first_name} {last_name} ({role})"
                except:
                    creator_name = f"User ID: {created_by_user_id}"
            elif created_by_user_id is None:
                creator_name = "Super Admin"
            else:
                creator_name = f"User ID: {created_by_user_id}"
            
            backups.append({
                'backup_id': backup_id,
                'backup_date': backup_date,
                'file_path': file_path,
                'creator': creator_name
            })
        
        return backups

    def get_user_restore_codes(self, system_admin_user_id: int) -> List[dict]:
        """Get all restore codes for a specific system admin."""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT rc.code_id, rc.code, rc.backup_id, rc.is_used, rc.generated_date,
                   b.backup_date, b.file_path
            FROM RestoreCode rc
            JOIN Backup b ON rc.backup_id = b.backup_id
            WHERE rc.system_admin_user_id = ?
            ORDER BY rc.generated_date DESC
        ''', (system_admin_user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        codes = []
        for row in rows:
            code_id, code_hash, backup_id, is_used, generated_date, backup_date, file_path = row
            
            codes.append({
                'code_id': code_id,
                'backup_id': backup_id,
                'is_used': bool(is_used),
                'generated_date': generated_date,
                'backup_date': backup_date,
                'file_path': file_path
            })
        
        return codes

    def create_restore_request(self, backup_id: int, system_admin_user_id: int) -> Tuple[bool, str]:
        """Create a restore code request from a system admin."""
        # Verify the backup exists
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT backup_id FROM Backup WHERE backup_id = ?', (backup_id,))
        if not c.fetchone():
            conn.close()
            return False, "Backup not found."

        # Check if a restore code already exists for this backup and system admin
        c.execute('''
            SELECT code_id FROM RestoreCode 
            WHERE backup_id = ? AND system_admin_user_id = ?
        ''', (backup_id, system_admin_user_id))
        
        if c.fetchone():
            conn.close()
            return False, "A restore code for this backup already exists for you."

        try:
            # Create a unique pending request code to avoid UNIQUE constraint violation
            pending_code = f"PENDING_{uuid.uuid4().hex[:8].upper()}"
            
            # Create a placeholder entry to indicate the request
            c.execute('''
                INSERT INTO RestoreCode (code, backup_id, system_admin_user_id, is_used, generated_date)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (
                pending_code,  # Unique pending request code
                backup_id,
                system_admin_user_id,
                0  # is_used = False
            ))
            conn.commit()
            conn.close()
            return True, "Restore code request created successfully."
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Failed to create request: {str(e)}"

    def get_pending_requests(self) -> List[dict]:
        """Get all pending restore code requests."""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT rc.code_id, rc.backup_id, rc.system_admin_user_id, rc.generated_date,
                   b.backup_date, b.file_path, b.created_by_user_id,
                   u.first_name, u.last_name, u.role
            FROM RestoreCode rc
            JOIN Backup b ON rc.backup_id = b.backup_id
            JOIN User u ON rc.system_admin_user_id = u.user_id
            WHERE rc.code LIKE 'PENDING_%' AND rc.is_used = 0
            ORDER BY rc.generated_date ASC
        ''')
        
        rows = c.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            code_id, backup_id, system_admin_user_id, generated_date, backup_date, file_path, created_by_user_id, first_name, last_name, role = row
            
            # Decrypt user data
            try:
                first_name = decrypt(first_name)
                last_name = decrypt(last_name)
                role = decrypt(role)
                requester_name = f"{first_name} {last_name} ({role})"
            except:
                requester_name = f"User ID: {system_admin_user_id}"
            
            backup_type = "Database" if "db_backup_" in file_path else "System"
            
            requests.append({
                'request_id': code_id,  # Use code_id as request_id
                'backup_id': backup_id,
                'system_admin_user_id': system_admin_user_id,
                'request_date': generated_date,
                'backup_date': backup_date,
                'backup_type': backup_type,
                'requester_name': requester_name
            })
        
        return requests

    def get_user_pending_requests(self, system_admin_user_id: int) -> List[dict]:
        """Get pending restore code requests for a specific system admin."""
        conn = self._get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT rc.code_id, rc.backup_id, rc.generated_date,
                   b.backup_date, b.file_path
            FROM RestoreCode rc
            JOIN Backup b ON rc.backup_id = b.backup_id
            WHERE rc.system_admin_user_id = ? AND rc.code LIKE 'PENDING_%' AND rc.is_used = 0
            ORDER BY rc.generated_date ASC
        ''', (system_admin_user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            code_id, backup_id, generated_date, backup_date, file_path = row
            
            backup_type = "Database" if "db_backup_" in file_path else "System"
            
            requests.append({
                'request_id': code_id,
                'backup_id': backup_id,
                'request_date': generated_date,
                'backup_date': backup_date,
                'backup_type': backup_type
            })
        
        return requests

    def mark_request_completed(self, request_id: int) -> bool:
        """Mark a restore code request as completed by deleting the pending entry."""
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                DELETE FROM RestoreCode 
                WHERE code_id = ? AND code LIKE 'PENDING_%'
            ''', (request_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            return False

# Create a singleton instance
restore_code_service = RestoreCodeService('urban_mobility.db') 