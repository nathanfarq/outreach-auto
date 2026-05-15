"""Shared helpers for the draft module."""

import re

# Matches the dated hook prefix written by Phase 2 writeback:
# "[enriched 2025-05-14] He recently launched a tax credits initiative..."
_HOOK_RE = re.compile(r"\[enriched \d{4}-\d{2}-\d{2}\]\s+(.+?)(?:\n|$)")


def extract_hook(notes: str | None) -> str | None:
    """Return just the hook sentence from a Notes field, or None if absent."""
    if not notes:
        return None
    m = _HOOK_RE.search(notes)
    return m.group(1).strip() if m else None
