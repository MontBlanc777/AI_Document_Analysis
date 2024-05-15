import os
import mimetypes
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pathlib

def get_file_mime_type(filename: str) -> str:
    """Determine MIME type based on file extension"""
    extension = pathlib.Path(filename).suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".eml": "message/rfc822",
        ".msg": "application/vnd.ms-outlook",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    return mime_types.get(extension, "application/octet-stream")

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure that a directory exists, creating it if necessary"""
    os.makedirs(directory_path, exist_ok=True)

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get basic file information"""
    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        mime_type = get_file_mime_type(file_name)
        created_time = os.path.getctime(file_path)
        modified_time = os.path.getmtime(file_path)
        
        return {
            "file_path": file_path,
            "file_name": file_name,
            "mime_type": mime_type,
            "file_size": file_size,
            "created_time": datetime.fromtimestamp(created_time).isoformat(),
            "modified_time": datetime.fromtimestamp(modified_time).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "file_path": file_path}

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename based on the original filename"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{original_filename}"