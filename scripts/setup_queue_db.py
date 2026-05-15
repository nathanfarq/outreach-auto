"""One-time setup: create the Notion "Outreach Queue" review database.

Usage:
    python scripts/setup_queue_db.py --parent-page-id <NOTION_PAGE_ID>

The parent page must already exist and the integration must have access to it.
After running, copy the printed NOTION_QUEUE_DB_ID line into .env.local.
"""

import argparse
import sys
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from notion_client import Client

import config.settings as settings

_STYLE_OPTIONS = [{"name": s} for s in ("general", "direct", "curious")]
_STATUS_OPTIONS = [
    {"name": "Pending", "color": "yellow"},
    {"name": "Approved", "color": "green"},
    {"name": "Rejected", "color": "red"},
    {"name": "Edited", "color": "blue"},
    {"name": "Sent", "color": "gray"},
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the Outreach Queue Notion DB.")
    parser.add_argument(
        "--parent-page-id",
        required=True,
        help="Notion page ID that will contain the new database.",
    )
    args = parser.parse_args()

    if settings.NOTION_QUEUE_DB_ID:
        print(f"NOTION_QUEUE_DB_ID is already set: {settings.NOTION_QUEUE_DB_ID}")
        print("Remove it from .env.local first if you want to create a new database.")
        sys.exit(1)

    client = Client(auth=settings.NOTION_API_KEY)

    response = cast(
        dict,
        client.databases.create(
            parent={"type": "page_id", "page_id": args.parent_page_id},
            title=[{"type": "text", "text": {"content": "Outreach Queue"}}],
            properties={
                "Name": {"title": {}},
                "Status": {"select": {"options": _STATUS_OPTIONS}},
                "Contact ID": {"rich_text": {}},
                "Subject": {"rich_text": {}},
                "Body": {"rich_text": {}},
                "Style": {"select": {"options": _STYLE_OPTIONS}},
                "Hook": {"rich_text": {}},
                "Created": {"date": {}},
            },
        ),
    )

    db_id = response["id"]
    print(f"\nOutreach Queue database created successfully.")
    print(f"\nAdd this line to .env.local:\n")
    print(f"    NOTION_QUEUE_DB_ID={db_id}\n")
    print("Then create a filtered view in Notion (filter: Status = Pending)")
    print("to use as your mobile review board.")


if __name__ == "__main__":
    main()
