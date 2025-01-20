import os
import aiofiles
from fastapi import UploadFile
from uuid import uuid4
from app.core.config import settings
from app.core.exceptions import ValidationError
from typing import Optional
from PIL import Image
import io

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_DIMENSION = 1200  # Maximum width or height
JPEG_QUALITY = 85  # JPEG compression quality (0-100)
PNG_COMPRESSION = 6  # PNG compression level (0-9)

def compress_image(image_data: bytes, content_type: str) -> bytes:
    """
    Compress an image while maintaining good quality.
    
    Args:
        image_data (bytes): Original image data
        content_type (str): Image content type
        
    Returns:
        bytes: Compressed image data
    """
    img = Image.open(io.BytesIO(image_data))
    
    # Convert RGBA to RGB if PNG
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    
    # Calculate new dimensions while maintaining aspect ratio
    ratio = min(MAX_IMAGE_DIMENSION / max(img.size[0], img.size[1]), 1.0)
    new_size = tuple(int(dim * ratio) for dim in img.size)
    
    # Resize if needed
    if ratio < 1.0:
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save with compression
    output = io.BytesIO()
    if content_type == "image/jpeg":
        img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
    elif content_type == "image/png":
        img.save(output, format='PNG', optimize=True, compression_level=PNG_COMPRESSION)
    elif content_type == "image/gif":
        img.save(output, format='GIF', optimize=True)
    
    return output.getvalue()

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
    
    # Compress image
    compressed_content = compress_image(content, upload_file.content_type)
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.STATIC_FILES_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1].lower()
    if not file_extension:
        file_extension = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif"
        }[upload_file.content_type]
    
    filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(compressed_content)
    
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