import sys
sys.path.append('../../')
from services.backup_service import backup_service
from services.restore_code_service import restore_code_service
from services.userservice import user_service

def request_backup_restore_menu(session):
    """Display list of all backups and allow system admins to request restore codes."""
    user_id = session.get_current_user_id()
    user = session.get_current_user()
    
    if user.role_plain not in ('system_admin', 'super'):
        print("Only system admins and super admins can view backups.")
        input("\nPress Enter to continue...")
        return
    
    print("\n=== Available Backups ===")
    backups = backup_service.get_backup_list()
    
    if not backups:
        print("No backups found.")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Date':<20} {'Type':<15} {'Creator':<30}")
    print("-" * 70)
    
    for backup in backups:
        backup_type = "Database" if "db_backup_" in backup['file_path'] else "System"
        print(f"{backup['backup_id']:<5} {backup['backup_date']:<20} {backup_type:<15} {backup['creator']:<30}")
    
    # If user is a system admin, allow them to request a restore code
    if user.role_plain == 'system_admin':
        print("\n" + "="*70)
        print("REQUEST RESTORE CODE")
        print("="*70)
        print("As a system admin, you can request a restore code for any backup.")
        print("A super admin will need to generate the code for you.")
        
        try:
            backup_id = int(input("\nEnter backup ID to request restore code for (or 0 to skip): "))
            if backup_id == 0:
                print("No backup selected.")
                input("\nPress Enter to continue...")
                return
            
            # Verify backup exists
            backup_exists = any(b['backup_id'] == backup_id for b in backups)
            if not backup_exists:
                print("Backup ID not found.")
                input("\nPress Enter to continue...")
                return
            
            # Create the restore request
            success, message = backup_service.create_restore_request(backup_id, user_id)
            print(f"\n{message}")
            if success:
                print("Your request has been submitted to the super admin.")
                print("You will be notified when your restore code is ready.")
            
        except ValueError:
            print("Invalid backup ID.")
            input("\nPress Enter to continue...")
            return
    
    input("\nPress Enter to continue...")

def list_backups_menu(session):
    """Display list of all backups."""
    print("\n=== Available Backups ===")
    backups = backup_service.get_backup_list()
    
    if not backups:
        print("No backups found.")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Date':<20} {'Type':<15} {'Creator':<30}")
    print("-" * 70)
    
    for backup in backups:
        backup_type = "Database" if "db_backup_" in backup['file_path'] else "System"
        print(f"{backup['backup_id']:<5} {backup['backup_date']:<20} {backup_type:<15} {backup['creator']:<30}")
    
    input("\nPress Enter to continue...")

def generate_restore_code_menu(session):
    """Generate a restore code for a specific backup (super admin only)."""
    user_id = session.get_current_user_id()
    user = session.get_current_user()
    
    if user.role_plain != 'super':
        print("Only super admins can generate restore codes.")
        input("\nPress Enter to continue...")
        return
    
    print("\n=== Generate Restore Code ===")
    
    # Get pending requests
    pending_requests = backup_service.get_pending_requests()
    
    if not pending_requests:
        print("No pending restore code requests found.")
        print("\nSystem admins need to request restore codes first.")
        input("\nPress Enter to continue...")
        return
    
    print("Pending restore code requests:")
    print(f"{'Req ID':<8} {'Backup ID':<10} {'Backup Type':<12} {'Backup Date':<20} {'Requester':<25} {'Request Date':<20}")
    print("-" * 95)
    
    for req in pending_requests:
        print(f"{req['request_id']:<8} {req['backup_id']:<10} {req['backup_type']:<12} {req['backup_date']:<20} {req['requester_name']:<25} {req['request_date']:<20}")
    
    # Get request ID to process
    try:
        request_id = int(input("\nEnter request ID to generate code for: "))
    except ValueError:
        print("Invalid request ID.")
        input("\nPress Enter to continue...")
        return
    
    # Find the request
    selected_request = None
    for req in pending_requests:
        if req['request_id'] == request_id:
            selected_request = req
            break
    
    if not selected_request:
        print("Request ID not found.")
        input("\nPress Enter to continue...")
        return
    
    # Generate code for the selected request
    success, result = backup_service.generate_restore_code(
        selected_request['backup_id'], 
        user_id, 
        selected_request['system_admin_user_id']
    )
    
    if success:
        print(f"\nRestore code generated successfully!")
        print(f"Code: {result}")
        print(f"Generated for: {selected_request['requester_name']}")
        print(f"Backup ID: {selected_request['backup_id']} ({selected_request['backup_type']})")
        print("This code can only be used once by that specific system admin.")
        
        # Mark request as completed
        backup_service.mark_request_completed(request_id)
        print("Request marked as completed.")
    else:
        print(f"Failed to generate code: {result}")
    
    input("\nPress Enter to continue...")

def restore_with_code_menu(session):
    """Restore a backup using a restore code (system admin only)."""
    user_id = session.get_current_user_id()
    user = session.get_current_user()
    
    if user.role_plain != 'system_admin':
        print("Only system admins can restore backups with codes.")
        input("\nPress Enter to continue...")
        return
    
    print("\n=== Restore Backup with Code ===")
    
    # Show user's available restore codes
    codes = backup_service.get_user_restore_codes(user_id)
    if codes:
        print("Your available restore codes:")
        print(f"{'Code ID':<8} {'Backup ID':<10} {'Backup Date':<20} {'Used':<5}")
        print("-" * 45)
        
        for code in codes:
            used_status = "Yes" if code['is_used'] else "No"
            print(f"{code['code_id']:<8} {code['backup_id']:<10} {code['backup_date']:<20} {used_status:<5}")
    
    # Get restore code
    code = input("\nEnter your restore code: ").strip()
    if not code:
        print("No code entered.")
        input("\nPress Enter to continue...")
        return
    
    # Confirm restore
    print("\nWARNING: This will restore the system/database to the backup state.")
    print("All current data may be lost!")
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
    
    if confirm != 'yes':
        print("Restore cancelled.")
        input("\nPress Enter to continue...")
        return
    
    # Perform restore
    success, message = backup_service.restore_backup_with_code(code, user_id)
    print(f"\n{message}")
    
    input("\nPress Enter to continue...")

def restore_direct_menu(session):
    """Restore a backup directly (super admin only)."""
    user_id = session.get_current_user_id()
    user = session.get_current_user()
    
    if user.role_plain != 'super':
        print("Only super admins can restore backups directly.")
        input("\nPress Enter to continue...")
        return
    
    print("\n=== Direct Backup Restore (Super Admin) ===")
    
    # List available backups
    backups = backup_service.get_backup_list()
    if not backups:
        print("No backups found.")
        input("\nPress Enter to continue...")
        return
    
    print("Available backups:")
    print(f"{'ID':<5} {'Date':<20} {'Type':<15}")
    print("-" * 40)
    
    for backup in backups:
        backup_type = "Database" if "db_backup_" in backup['file_path'] else "System"
        print(f"{backup['backup_id']:<5} {backup['backup_date']:<20} {backup_type:<15}")
    
    # Get backup ID
    try:
        backup_id = int(input("\nEnter backup ID to restore: "))
    except ValueError:
        print("Invalid backup ID.")
        input("\nPress Enter to continue...")
        return
    
    # Verify backup exists
    backup_exists = any(b['backup_id'] == backup_id for b in backups)
    if not backup_exists:
        print("Backup ID not found.")
        input("\nPress Enter to continue...")
        return
    
    # Confirm restore
    print("\nWARNING: This will restore the system/database to the backup state.")
    print("All current data may be lost!")
    print("All older backups will be wiped!")
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
    
    if confirm != 'yes':
        print("Restore cancelled.")
        input("\nPress Enter to continue...")
        return
    
    # Perform restore
    success, message = backup_service.restore_backup_direct(backup_id, user_id)
    print(f"\n{message}")
    
    input("\nPress Enter to continue...")

def view_my_codes_menu(session):
    """View restore codes for the current user (system admin only)."""
    user_id = session.get_current_user_id()
    user = session.get_current_user()
    
    if user.role_plain != 'system_admin':
        print("Only system admins have restore codes.")
        input("\nPress Enter to continue...")
        return
    
    print("\n=== My Restore Codes ===")
    
    codes = backup_service.get_user_restore_codes(user_id)
    if not codes:
        print("You have no restore codes.")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'Code ID':<8} {'Backup ID':<10} {'Backup Date':<20} {'Generated':<20} {'Used':<5}")
    print("-" * 65)
    
    for code in codes:
        used_status = "Yes" if code['is_used'] else "No"
        print(f"{code['code_id']:<8} {code['backup_id']:<10} {code['backup_date']:<20} {code['generated_date']:<20} {used_status:<5}")
    
    input("\nPress Enter to continue...") 