"""Phase 2 — Write enrichment results back to Notion.

Prepends a dated hook line to the contact's Notes field and sets Status to
'Enriched'. Existing notes are preserved below the new hook line.
"""

from datetime import date

from src.contacts.notion_client import NotionContactClient
from src.contacts.schema import Contact

_MAX_NOTES_CHARS = 1950  # Notion rich_text block limit is 2000; leave a small buffer


def write_hook(contact: Contact, hook: str, client: NotionContactClient) -> None:
    """Prepend hook with a date stamp to Notes and mark the contact as Enriched."""
    stamp = date.today().isoformat()
    new_line = f"[enriched {stamp}] {hook}"

    if contact.notes:
        combined = f"{new_line}\n{contact.notes}"
    else:
        combined = new_line

    client.update_notes_and_status(contact.id, combined[:_MAX_NOTES_CHARS])
