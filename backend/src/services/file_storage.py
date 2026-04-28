"""File storage service - handles file uploads, downloads, and management"""
import os
import uuid
import tempfile
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

def ensure_upload_dir():
    """Ensure upload directory exists"""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

async def upload_file(file_data: bytes, filename: str, file_type: str = "document") -> str:
    """Upload file and return file ID"""
    ensure_upload_dir()
    
    file_id = str(uuid.uuid4())
    file_ext = Path(filename).suffix
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    return file_id

async def download_file(file_id: str) -> Optional[bytes]:
    """Download file by ID"""
    ensure_upload_dir()
    
    for file_path in Path(UPLOAD_DIR).glob(f"{file_id}.*"):
        with open(file_path, "rb") as f:
            return f.read()
    
    return None

def delete_file(file_id: str) -> bool:
    """Delete file by ID"""
    ensure_upload_dir()
    
    for file_path in Path(UPLOAD_DIR).glob(f"{file_id}.*"):
        file_path.unlink()
        return True
    
    return False
