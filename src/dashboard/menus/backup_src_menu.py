import sys
sys.path.append('../../')
from services.backup_service import backup_service

def backup_src_menu(session):
    user_id = session.get_current_user_id()
    print("\n=== Create Full System (src) Backup ===")
    success, message = backup_service.create_backup(user_id)
    print(message)
    input("\nPress Enter to continue...") 