"""Context builder - builds user and company context"""
from typing import Dict, Any, Optional

_context = {}

def init_context(get_db_fn):
    """Initialize context with database function"""
    global _context
    _context["get_db"] = get_db_fn

async def build_user_context(user_id: str, company_id: str) -> Dict[str, Any]:
    """Build context for a user"""
    return {
        "user_id": user_id,
        "company_id": company_id,
        "role": "user",
        "permissions": ["read", "write"]
    }
"""Minimal context builder for legal_agent compatibility."""

from typing import Any

_get_db = None


def init_context(get_db_fn: Any) -> None:
    global _get_db
    _get_db = get_db_fn


async def build_user_context(company_id: str, user_id: str | None) -> str:
    # Lightweight fallback context; extend later when DB schema is finalized.
    return ""
