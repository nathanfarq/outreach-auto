"""Dry-run script: fetch contacts from Notion, apply filter, print results.

No emails are sent. No Notion writes. Read-only.

Usage:
    python scripts/dry_run.py
"""

import sys
from pathlib import Path

# Allow imports from repo root without an editable install
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config.settings as settings
from src.contacts.filters import ready_for_outreach
from src.contacts.notion_client import NotionContactClient

COL_WIDTHS = (28, 12, 22, 18, 8, 6)
HEADERS = ("NAME", "STATUS", "ROLE", "LOCATION", "LINKEDIN", "ORGS")


def _row(*cells: str) -> str:
    return "  ".join(str(c).ljust(w) for c, w in zip(cells, COL_WIDTHS))


def main() -> None:
    client = NotionContactClient(settings.NOTION_API_KEY, settings.NOTION_NETWORK_DB_ID)

    print("Fetching contacts from Notion…")
    all_contacts = client.fetch_all()
    print(f"Fetched {len(all_contacts)} contacts.")

    ready = ready_for_outreach(all_contacts)
    print(f"Ready for outreach: {len(ready)}")

    if not ready:
        print(
            "\nNo contacts matched. Check that Status is blank / 'No contact' / 'To contact',"
            " LinkedIn is set, and Organizations is populated."
        )
        return

    print()
    print(_row(*HEADERS))
    print("-" * (sum(COL_WIDTHS) + 2 * (len(COL_WIDTHS) - 1)))

    for c in ready:
        print(
            _row(
                c.name[:26],
                c.status or "",
                (c.role or "")[:20],
                (c.location or "")[:16],
                "set" if c.linkedin else "—",
                str(len(c.organization_ids)),
            )
        )


if __name__ == "__main__":
    main()
