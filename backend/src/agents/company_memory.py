"""Company memory - stores company context and memory"""
from typing import Dict, Any, Optional

_memory = {}

def init_memory(get_db_fn):
    """Initialize memory with database function"""
    global _memory
    _memory["get_db"] = get_db_fn

async def get_company_memory(company_id: str) -> Dict[str, Any]:
    """Get company memory from database"""
    return _memory.get(company_id, {})

async def update_company_memory(company_id: str, memory_data: Dict[str, Any]) -> bool:
    """Update company memory"""
    _memory[company_id] = memory_data
    return True
"""Minimal company memory helpers for legal_agent compatibility."""

from typing import Any

_get_db = None


def init_memory(get_db_fn: Any) -> None:
    global _get_db
    _get_db = get_db_fn


async def get_company_memory(company_id: str) -> str:
    # Lightweight fallback: no persisted memory yet.
    return ""


async def update_company_memory(company_id: str, note: str) -> dict:
    # Keep API shape compatible with legal_agent expectations.
    return {"success": True, "message": "memory_skipped"}
