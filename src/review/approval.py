"""Phase 4 — Process approval / rejection decisions.

Reads queue items whose Status was changed to 'Approved', 'Edited', or
'Rejected' by the founder in Notion, and routes approved drafts to the
send queue. No draft is ever sent without an explicit 'Approved' status.
"""

from src.review.queue import NotionQueueClient


def fetch_pending(client: NotionQueueClient) -> list[dict]:
    """Return all drafts still awaiting review."""
    return client.fetch_by_status("Pending")


def fetch_approved(client: NotionQueueClient) -> list[dict]:
    """Return drafts ready to send.

    Includes both 'Approved' (body untouched) and 'Edited' (body updated
    directly in Notion). Body is read from Notion so in-place edits are
    respected.
    """
    return client.fetch_by_status("Approved") + client.fetch_by_status("Edited")


def mark_processed(client: NotionQueueClient, page_id: str) -> None:
    """Set Status=Sent after the email has been dispatched.

    Prevents re-queuing on the next approval run.
    """
    client.update_status(page_id, "Sent")
