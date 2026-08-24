import os
import uuid
import base64
import json
import urllib.request
from typing import Optional
from fastapi import HTTPException, status

from app.core.config import settings

# Make sure local uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 5MB limit
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/jpg"
}

class StorageService:
    """Service to abstract image storage backends."""
    
    def __init__(self):
        self.public_key = settings.IMAGEKIT_PUBLIC_KEY
        self.private_key = settings.IMAGEKIT_PRIVATE_KEY
        self.url_endpoint = settings.IMAGEKIT_URL_ENDPOINT

    def validate_file(self, content_type: str, file_size: int) -> None:
        """Validate content type and size of the file."""
        if content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {content_type}. Only JPEG, PNG, GIF, and WEBP are allowed."
            )
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds limit of 5MB. Provided: {file_size / (1024*1024):.2f}MB"
            )

    def upload_image(self, file_data: bytes, file_name: str, content_type: str) -> str:
        """
        Uploads image. If ImageKit configuration is available, uses ImageKit HTTP API via urllib.
        Otherwise, falls back to saving locally in the uploads/ directory.
        """
        # Validate first
        self.validate_file(content_type, len(file_data))

        # Check if ImageKit is configured
        if self.private_key and self.public_key and self.url_endpoint:
            try:
                # Convert file bytes to base64
                base64_data = base64.b64encode(file_data).decode("utf-8")
                payload = {
                    "file": f"data:{content_type};base64,{base64_data}",
                    "fileName": file_name,
                    "useUniqueFileName": "true",
                    "folder": "/complaints/"
                }
                
                auth_str = base64.b64encode(f"{self.private_key}:".encode("utf-8")).decode("utf-8")
                req = urllib.request.Request(
                    "https://upload.imagekit.io/api/v1/files/upload",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Basic {auth_str}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=30.0) as response:
                    body = response.read().decode("utf-8")
                    data = json.loads(body)
                    return data.get("url", "")
            except Exception as e:
                # Log error and fallback to local storage
                print(f"ImageKit urlopen upload failed or error occured: {e}")

        # Fallback: Save locally
        extension = os.path.splitext(file_name)[1]
        if not extension:
            # guess extension from mime type
            extension = "." + content_type.split("/")[-1]
            if extension == ".jpeg":
                extension = ".jpg"
        
        unique_name = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        # Return local path identifier
        return f"/uploads/{unique_name}"

    def delete_image(self, image_url: str) -> bool:
        """Delete image. Only supports local cleanup for now."""
        if image_url.startswith("/uploads/"):
            filename = image_url.replace("/uploads/", "")
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            except Exception as e:
                print(f"Failed to delete local file {file_path}: {e}")
        return False

# Singleton instance
storage_service = StorageService()