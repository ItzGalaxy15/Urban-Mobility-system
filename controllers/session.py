from dbcontext.userdata import verify_user_password, get_user_by_username
from models.user import User

class UserSession:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.role = None

    def login(self, username, password):
        # Check for hardcoded super admin
        if username == "super_admin" and password == "Admin_123?":
            self.user_id = 0  # Special ID for super admin
            self.username = "super_admin"
            self.role = "super"
            print(f"Logged in as {self.username} ({self.role})")
            return True

        # Regular user login
        user = get_user_by_username(username)
        if not user:
            print("Username or password incorrect.")
            return False
        if not verify_user_password(user["user_id"], password):
            print("Password incorrect.")
            return False
        self.user_id = user["user_id"]
        self.username = user["username"]
        self.role = user["role"]
        print(f"Logged in as {self.username} ({self.role})")
        return True

    def logout(self):
        self.user_id = None
        self.username = None
        self.role = None
        print("Logged out.")

    def is_authenticated(self):
        return self.user_id is not None
