# um_members.py
from dbcontext.dbcontext import create_db
from dbcontext.userdata import add_user
from controllers.usercontroller import change_password
from controllers.session import UserSession

def main():
    print("Urban Mobility System Starting...")
# add_user("mike_admin", "StrongPass123!", "Mike", "Jansen", "system_admin")
    create_db()

    session = UserSession()
    while not session.is_authenticated():
        username = input("Username: ")
        password = input("Password: ")
        session.login(username, password)

    while True:
        print(f"\nWelcome, {session.username} ({session.role})")
        option = input("Choose option: \n 1. Change password\n 2. Logout\n 3. Exit\n")
        if option == "1":
            old_pw = input("Enter your old password: ")
            new_pw = input("Enter your new password: ")
            success, message = change_password(session.user_id, old_pw, new_pw)
            print(message)
        elif option == "2":
            session.logout()
            break
        elif option == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
