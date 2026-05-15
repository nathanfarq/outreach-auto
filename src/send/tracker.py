"""Phase 5 — Log send results back to Notion.

After a successful Gmail send, updates the contact's Status to 'Contacted'
and records the send timestamp in the Notes field (or a dedicated Sent At
date property if one is added to the schema later).
"""

from datetime import date

from src.contacts.notion_client import NotionContactClient
from src.review.queue import NotionQueueClient


def mark_contacted(
    queue_item: dict,
    queue_client: NotionQueueClient,
    contact_client: NotionContactClient,
) -> None:
    """Update Network DB (Status=Contacted + dated note) and Queue DB (Status=Sent).

    Logs on Notion failure but does not raise — the email was already sent.
    """
    contact = contact_client.fetch_contact_by_id(queue_item["contact_id"])
    if contact is None:
        print(
            f"  WARN  contact {queue_item['contact_id'][:8]} not found in Network DB"
            " — Notion not updated"
        )
        return

    new_notes = _build_contacted_notes(contact.notes, queue_item["subject"])

    try:
        contact_client.mark_contacted(queue_item["contact_id"], new_notes)
    except Exception as exc:
        print(f"  WARN  failed to update Network DB for {queue_item['contact_name']}: {exc}")

    try:
        queue_client.update_status(queue_item["queue_page_id"], "Sent")
    except Exception as exc:
        print(f"  WARN  failed to mark queue item Sent for {queue_item['contact_name']}: {exc}")


def _build_contacted_notes(existing_notes: str | None, subject: str) -> str:
    stamp = date.today().isoformat()
    new_line = f"[contacted {stamp}] Sent: {subject}"
    combined = f"{new_line}\n{existing_notes}" if existing_notes else new_line
    return combined[:1950]
