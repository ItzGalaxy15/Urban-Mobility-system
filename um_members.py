# um_members.py
from models.user import User

print("Urban Mobility System Starting...")

# Demo: create a user and show their full name
user = User("mike_admin", "StrongPass123!", "system_admin", "Mike", "Jansen")

print("Username:", user.get_username())
print("Full name:", user.get_full_name())
print("Role:", user.role)
print("Password check:", user.verify_password("StrongPass123!"))  # True