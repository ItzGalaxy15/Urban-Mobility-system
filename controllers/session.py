from dbcontext.userdata import verify_user_password, get_user_by_username

class UserSession:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.role = None

    def login(self, username, password):
        # Find user by username (unencrypted search)
        user = get_user_by_username(username)
        if not user:
            print("User not found.")
            return False
        if not verify_user_password(user["user_id"], password):
            print("Incorrect password.")
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
