from pydantic import BaseModel, EmailStr, field_validator
from app.core.exceptions import ValidationError

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "StrongP@ss123"
            }
        }

class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValidationError("Enter a valid email address.")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ss123"
            }
        } 