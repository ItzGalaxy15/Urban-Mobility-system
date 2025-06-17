import os
import zipfile
from datetime import datetime
import sqlite3
from services.userservice import user_service

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

backup_service = BackupService() 