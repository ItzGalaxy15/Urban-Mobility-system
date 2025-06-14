from controllers.usercontroller import UserController

def change_password_flow(session):
    while True:
        old_pw = input("Enter your old password: ")
        new_pw = input("Enter your new password (or leave blank to cancel): ")
        if not new_pw:
            print("Password change cancelled.")
            break
        success, message = UserController.change_password(session.user_id, old_pw, new_pw)
        print(message)
        if success:
            break 