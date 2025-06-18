from controllers.session import UserSession
from controllers.backupcontroller import BackupController

def backup_src_flow(session):
    """Flow for creating source code backups"""
    print("\n=== Create Source Code Backup ===")
    user_id = UserSession.get_current_user_id()
    success, message = BackupController.create_source_backup(user_id)
    print(message)
    input("\nPress Enter to continue...") 