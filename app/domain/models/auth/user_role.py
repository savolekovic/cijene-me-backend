from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"  # Changed from MEDIATOR
    USER = "user"