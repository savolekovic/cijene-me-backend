from enum import Enum

class UserRole(Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"

    @classmethod
    def _missing_(cls, value):
        # Handle case-insensitive lookup
        for member in cls:
            if member.value.lower() == value.lower():
                return member