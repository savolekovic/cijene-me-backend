import os
import aiofiles
from fastapi import UploadFile
from uuid import uuid4
from app.core.config import settings
from app.core.exceptions import ValidationError
from typing import Optional
from PIL import Image
import io
import cloudinary
import cloudinary.uploader
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

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
    """Save file to Cloudinary and return the URL"""
    if not upload_file.content_type in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")
    
    content = await upload_file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise ValidationError(f"File too large. Maximum size: {MAX_IMAGE_SIZE/1024/1024}MB")
    
    compressed_content = compress_image(content, upload_file.content_type)
    
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )
    
    try:
        result = cloudinary.uploader.upload(
            compressed_content,
            folder=folder,
            resource_type="auto"
        )
        return result['secure_url']
    except Exception as e:
        raise ValidationError(f"Failed to upload image: {str(e)}")

async def delete_upload_file(file_path: Optional[str]) -> None:
    """Delete file from Cloudinary"""
    if not file_path:
        return
        
    try:
        # Extract public_id from URL
        if "cloudinary.com" in file_path:
            # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234/folder/filename.jpg
            parts = file_path.split("/upload/")
            if len(parts) > 1:
                public_id = parts[1].split("/", 1)[1].rsplit(".", 1)[0]
                
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET
                )
                
                cloudinary.uploader.destroy(public_id)
    except Exception as e:
        logger.error(f"Failed to delete image from Cloudinary: {str(e)}") 