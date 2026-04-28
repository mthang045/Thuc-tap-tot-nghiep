"""Diff utilities - generate inline diffs for text comparison"""
from typing import List, Tuple

def generate_inline_diff(text1: str, text2: str) -> str:
    """Generate inline diff showing changes between two texts"""
    return f"<diff>{text1}</diff> -> <diff>{text2}</diff>"

def highlight_changes(text: str) -> str:
    """Highlight changes in text"""
    return text
"""Minimal diff helper for legal_agent compatibility."""

from difflib import SequenceMatcher


def generate_inline_diff(original: str, edited: str) -> dict:
    matcher = SequenceMatcher(None, original or "", edited or "")
    additions = 0
    deletions = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("insert", "replace"):
            additions += max(0, j2 - j1)
        if tag in ("delete", "replace"):
            deletions += max(0, i2 - i1)

    return {
        "inline_html": edited or "",
        "additions": additions,
        "deletions": deletions,
        "changes_count": additions + deletions,
        "summary": "Diff generated",
    }
