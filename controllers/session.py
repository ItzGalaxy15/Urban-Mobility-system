from dbcontext.userdata import verify_user_password, get_user_by_username
from models.user import User

class UserSession:
    def __init__(self):
        self.user = None
        self.user_id = None
        self.username = None
        self.role = None

    def login(self, username, password):
        # Check for hardcoded super admin
        if username == "super_admin" and password == "Admin_123?":
            # Create a proper User object for super admin
            self.user = User(
                username="super_admin",
                password_plain="Admin_123?",
                role="super"
            )
            self.user_id = 0  # Special ID for super admin
            self.username = "super_admin"
            self.role = "super"
            print(f"Logged in as {self.username} ({self.role})")
            return True

        # Regular user login
        user_data = get_user_by_username(username)
        if not user_data:
            print("Username or password incorrect.")
            return False
        if not verify_user_password(user_data["user_id"], password):
            print("Password incorrect.")
            return False
            
        # Create User object for regular users
        self.user = User(
            username=user_data["username"],
            password_plain=password,  # We already verified it's correct
            role=user_data["role"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        self.user_id = user_data["user_id"]
        self.username = user_data["username"]
        self.role = user_data["role"]
        print(f"Logged in as {self.username} ({self.role})")
        return True

    def logout(self):
        self.user = None
        self.user_id = None
        self.username = None
        self.role = None
        print("Logged out.")

    def is_authenticated(self):
        return self.user is not None
