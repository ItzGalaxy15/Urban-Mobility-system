from services.session_service import session_service
from controllers.backupcontroller import BackupController

def backup_db_flow(session):
    """Flow for creating database backups"""
    print("\n=== Create Database Backup ===")
    user_id = UserSession.get_current_user_id()
    success, message = BackupController.create_database_backup(user_id)
    print(message)
    input("\nPress Enter to continue...") 