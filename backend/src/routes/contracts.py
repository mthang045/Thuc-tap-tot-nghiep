"""Contract routes - contract management endpoints"""
from typing import Optional

async def extract_file_text(file_path: str) -> str:
    """Extract text from a contract file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
