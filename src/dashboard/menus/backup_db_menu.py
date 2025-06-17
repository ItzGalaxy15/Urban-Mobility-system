import sys
sys.path.append('../../')
from services.backup_service import backup_service

def backup_db_menu(session):
    user_id = session.get_current_user_id()
    print("\n=== Create Database Backup ===")
    success, message = backup_service.create_db_backup(user_id)
    print(message)
    input("\nPress Enter to continue...") 