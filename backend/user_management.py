from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    role: str

# Define user roles
class UserRole:
    SUPER_ADMIN = "Super Admin"
    OFFICE_ADMIN = "Office Admin"
    DISPATCHER = "Dispatcher"
    EMPLOYEE = "Employee"

# Function to check user permissions based on their role
def check_permission(user_role: str, required_role: str) -> bool:
    role_hierarchy = {
        UserRole.SUPER_ADMIN: 4,
        UserRole.OFFICE_ADMIN: 3,
        UserRole.DISPATCHER: 2,
        UserRole.EMPLOYEE: 1
    }
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
