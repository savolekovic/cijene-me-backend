from enum import Enum

class UserRole(Enum):
    USER = "user"
    MEDIATOR = "mediator"  # Can manage content but not users
    ADMIN = "admin"  # Can manage everything 