"""Phase 5 CLI — Send approved drafts via Gmail.

Usage:
    python scripts/run_sending.py [--dry-run] [--limit N]

Fetches all Approved/Edited drafts from the Notion Queue, sends each one via
the school Gmail account, then marks the queue item as Sent and the contact
as Contacted in the Network DB.

--dry-run  Print what would be sent without touching Gmail or Notion.
--limit N  Max emails this run (default: MAX_SENDS_PER_DAY from settings).
"""

import argparse
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config.settings as settings
from src.contacts.notion_client import NotionContactClient
from src.review.approval import fetch_approved
from src.review.queue import NotionQueueClient
from src.send import tracker
from src.send.gmail_client import GmailClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Send approved outreach drafts via Gmail.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without sending.")
    parser.add_argument("--limit", type=int, default=None, help="Max emails this run.")
    args = parser.parse_args()

    limit = args.limit if args.limit is not None else settings.MAX_SENDS_PER_DAY

    queue_client = NotionQueueClient(settings.NOTION_API_KEY, settings.NOTION_QUEUE_DB_ID)
    contact_client = NotionContactClient(settings.NOTION_API_KEY, settings.NOTION_NETWORK_DB_ID)

    if not args.dry_run:
        gmail_client = GmailClient(
            sender_address=settings.GMAIL_SCHOOL_ADDRESS,
            client_id=settings.GMAIL_SCHOOL_CLIENT_ID,
            client_secret=settings.GMAIL_SCHOOL_CLIENT_SECRET,
            refresh_token=settings.GMAIL_SCHOOL_REFRESH_TOKEN,
        )

    approved = fetch_approved(queue_client)

    if not approved:
        print("No approved drafts found in the queue.")
        return

    batch = approved[:limit]
    skipped_rate = len(approved) - len(batch)

    print(f"Found {len(approved)} approved draft(s); processing {len(batch)} (limit={limit}).\n")

    sent = 0
    skipped_email = 0
    failed = 0

    for item in batch:
        name = item["contact_name"]

        contact = contact_client.fetch_contact_by_id(item["contact_id"])
        if not contact or not contact.email:
            print(f"  SKIP  {name} — no email address")
            skipped_email += 1
            continue

        if args.dry_run:
            print(f"  DRY   {name} → {contact.email}  [{item['subject']}]")
            sent += 1
            continue

        try:
            msg_id = gmail_client.send(contact.email, item["subject"], item["body"])
        except httpx.HTTPStatusError as exc:
            print(f"  FAIL  {name} — Gmail error {exc.response.status_code}: {exc.response.text[:120]}")
            failed += 1
            continue

        tracker.mark_contacted(item, queue_client, contact_client)
        sent += 1
        print(f"  SENT  {name} → {contact.email}  [msg:{msg_id[:12]}]")

    suffix = " (dry run)" if args.dry_run else ""
    parts = [f"{sent} sent{suffix}"]
    if skipped_email:
        parts.append(f"{skipped_email} skipped (no email)")
    if failed:
        parts.append(f"{failed} failed")
    if skipped_rate:
        parts.append(f"{skipped_rate} skipped (rate limit)")
    print(f"\nDone. {', '.join(parts)}.")


if __name__ == "__main__":
    main()
