from controllers.usercontroller import UserController
from controllers.session import UserSession
from services.userservice import user_service
CANCEL_KEYWORDS = {"back", "exit"}

def reset_password_flow(session):
    """Flow for system admin to reset a user's password"""
    print("\n=== Reset User Password ===")
    
    # Get user identifier (ID or username)
    while True:
        identifier = input("Enter user ID or username ('back' or 'exit' to cancel): ").strip()
        if identifier.lower() in CANCEL_KEYWORDS:
            print("Operation cancelled.")
            return
            
        # Try to find user by ID first
        try:
            user_id = int(identifier)
            user = user_service.get_user_by_id(user_id)
        except ValueError:
            # If not a valid ID, try username
            user = user_service.get_user_by_username(identifier)
        
        if not user:
            print("User not found")
            continue
        
        current_user_id = UserSession.get_current_user_id()
        # Special-case for hardcoded super admin
        if current_user_id == 0:
            current_role = 'super'
        else:
            current_user = user_service.get_user_by_id(current_user_id)
            current_role = current_user.role_plain if current_user else None

        # Permission logic
        if current_role == 'system_admin':
            if user.role_plain != 'service_engineer':
                print("System admin can only reset passwords for service engineers")
                continue
        elif current_role == 'super':
            if user.role_plain not in ('system_admin', 'service_engineer'):
                print("Super admin can only reset passwords for system admins or service engineers")
                continue
        else:
            print("Only system admin or super admin can reset passwords")
            return
        break
    
    # Debug print
    # print(f"[DEBUG] Generating reset code for user_id: {user.user_id}, username: {user.username_plain}")
    # print(f"[DEBUG] Current admin user_id: {current_user_id}")
    success, reset_code = user_service.generate_temp_code(current_user_id, user.user_id)
    
    if not success:
        print(reset_code)  # The message is returned in the second tuple element
        return
    
    print(f"\nReset code generated: {reset_code}")
    print("Please provide this code to the user")
    
    input("\nPress Enter to continue...")

def use_reset_code_flow(user_id):
    """Flow for service engineer to use reset code (user_id is passed explicitly)"""
    print("\n=== Password Reset Required ===")
    print("A password reset has been requested for your account.")
    
    # Debug print
    # print(f"[DEBUG] Attempting reset for user_id: {user_id}")
    
    # Get reset code
    reset_code = input("Enter the reset code provided by your administrator: ")
    if not reset_code:
        return False
    
    # Verify the code
    if not user_service.verify_temp_code(user_id, reset_code):
        print("Invalid or expired reset code")
        return False
    
    # Get previous password hash (if any)
    conn = user_service._get_connection()
    c = conn.cursor()
    c.execute('SELECT password_hash FROM User WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    prev_hash = row[0] if row else None
    
    # Loop for new password entry/verification
    while True:
        new_password = input("Enter new password (leave blank to cancel): ")
        if not new_password:
            print("Password reset cancelled.")
            return False
        valid, message = user_service.validate_password(new_password)
        if not valid:
            print(message)
            continue
        # Check not same as previous password
        if prev_hash is not None and user_service.verify_user_password(user_id, new_password):
            print("New password cannot be the same as the previous password.")
            continue
        verify_password = input("Verify new password: ")
        if not verify_password:
            print("Password reset cancelled.")
            return False
        if new_password != verify_password:
            print("Passwords do not match")
            continue
        # Try to reset password
        success, msg = user_service.reset_password_with_code(user_id, reset_code, new_password)
        if success:
            print("Password reset successful. You are now logged in with your new password.")
            # Set session for user
            user_data = user_service.get_user_by_id(user_id)
            UserSession._current_user = user_data  # This is now a User object
            UserSession._current_user_id = user_data.user_id
            UserSession._current_username = user_data.username_plain
            UserSession._current_role = user_data.role_plain
            return True
        else:
            print(msg)
            # If code is invalid/expired, break, else loop again
            if "code" in msg.lower():
                return False
            # Otherwise, allow retry 