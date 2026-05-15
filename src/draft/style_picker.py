"""Phase 3 — Rule-based template selection.

Picks which email style (general / direct / curious) best fits a contact
based on their role, tags, and organization type. No LLM call — pure rules.

Rules (edit freely):
  1. DIRECT   — contact shows founder/builder/operator signals in role, tags,
                or the enrichment hook text. Keywords: see _FOUNDER_KEYWORDS.
  2. CURIOUS  — enrichment hook is absent or very short (< 30 chars), meaning
                we don't have enough context for a specific opener.
  3. GENERAL  — default fallback for everyone else.
"""

from src.contacts.schema import Contact
from src.draft._utils import extract_hook

# Keywords that suggest a founder/builder/operator profile.
# Check is case-insensitive. Add terms here to widen the direct-style net.
_FOUNDER_KEYWORDS: frozenset[str] = frozenset({
    "founder",
    "co-founder",
    "cofounder",
    "ceo",
    "builder",
    "operator",
    "entrepreneur",
    "started",
    "building",
    "launched",
})

# Hook shorter than this (in chars) → treat as sparse → curious style.
_SPARSE_HOOK_THRESHOLD = 30


def pick_style(contact: Contact) -> str:
    """Return 'direct', 'curious', or 'general' for this contact."""
    if _is_founder_signal(contact):
        return "direct"
    if _is_sparse(contact):
        return "curious"
    return "general"


def _is_founder_signal(contact: Contact) -> bool:
    # Check role field
    if contact.role and _contains_keyword(contact.role):
        return True
    # Check each tag
    if any(_contains_keyword(tag) for tag in contact.tags):
        return True
    # Check the hook text itself (e.g., "He launched a startup...")
    hook = extract_hook(contact.notes)
    if hook and _contains_keyword(hook):
        return True
    return False


def _is_sparse(contact: Contact) -> bool:
    hook = extract_hook(contact.notes)
    return hook is None or len(hook.strip()) < _SPARSE_HOOK_THRESHOLD


def _contains_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in _FOUNDER_KEYWORDS)
