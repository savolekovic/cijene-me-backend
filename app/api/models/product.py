from pydantic import BaseModel, Field, field_validator
from app.core.exceptions import ValidationError
from fastapi import UploadFile
import re

class ProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    barcode: str = Field(..., min_length=8, max_length=13)
    category_id: int = Field(..., gt=0)

    @field_validator('barcode')
    def validate_barcode(cls, value: str) -> str:
        # Remove any whitespace
        value = value.strip()
        
        # Check if empty
        if not value:
            raise ValidationError("Barcode cannot be empty")
            
        # Check if it contains only numbers
        if not value.isdigit():
            raise ValidationError("Barcode must contain only numbers")
            
        # Check length (EAN-13 is 13 digits, EAN-8 is 8 digits)
        if len(value) not in [8, 13]:
            raise ValidationError("Barcode must be either 8 or 13 digits long (EAN-8 or EAN-13)")
            
        # Validate EAN checksum
        if not cls.validate_ean_checksum(value):
            raise ValidationError("Invalid barcode checksum")
            
        return value

    @classmethod
    def validate_ean_checksum(cls, barcode: str) -> bool:
        """
        Validates EAN-8 or EAN-13 checksum
        """
        if len(barcode) not in [8, 13]:
            return False

        # Convert to list of integers
        digits = [int(d) for d in barcode]
        
        # Get check digit (last digit)
        check_digit = digits[-1]
        
        # Calculate checksum
        total = 0
        for i in range(len(digits) - 1):
            if i % 2 == 0:
                total += digits[i] * 3
            else:
                total += digits[i] * 1
                
        calculated_check = (10 - (total % 10)) % 10
        
        return check_digit == calculated_check

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jabuka",
                "barcode": "3856892301234",
                "category_id": 1
            }
        }
 