# um_members.py
from dbcontext.dbcontext import create_db, add_user, get_user_by_id, verify_user_password

print("Urban Mobility System Starting...")

# Create the database and add a user
create_db()
add_user("mike_admin", "StrongPass123!", "Mike", "Jansen", "system_admin")

# Retrieve the user by ID
user = get_user_by_id(1)
if user:
    print("Username:", user["username"])
    print("Full name:", f"{user['first_name']} {user['last_name']}")
    print("Role:", user["role"])
    print("Password check:", verify_user_password(1, "StrongPass123!"))  # Should print True
else:
    print("User not found.")