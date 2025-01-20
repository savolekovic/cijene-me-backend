import os
import aiofiles
from fastapi import UploadFile
from uuid import uuid4
from app.core.config import settings
from app.core.exceptions import ValidationError
from typing import Optional

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

async def save_upload_file(upload_file: UploadFile, folder: str = "products") -> str:
    """
    Save an uploaded file to the specified folder and return the file path.
    
    Args:
        upload_file (UploadFile): The uploaded file
        folder (str): The subfolder to save the file in (default: "products")
        
    Returns:
        str: The relative path to the saved file
        
    Raises:
        ValidationError: If the file type is not allowed or file is too large
    """
    if not upload_file.content_type in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")
    
    # Read file content to check size
    content = await upload_file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise ValidationError(f"File too large. Maximum size: {MAX_IMAGE_SIZE/1024/1024}MB")
    
    # Reset file pointer
    await upload_file.seek(0)
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.STATIC_FILES_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(content)
    
    return os.path.join(folder, filename)

async def delete_upload_file(file_path: Optional[str]) -> None:
    """
    Delete an uploaded file.
    
    Args:
        file_path (Optional[str]): The relative path to the file to delete
    """
    if not file_path:
        return
        
    full_path = os.path.join(settings.STATIC_FILES_DIR, file_path)
    if os.path.exists(full_path):
        os.remove(full_path) 