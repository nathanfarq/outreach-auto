"""Phase 4 CLI — Stage pending email drafts to the Notion review queue.

Usage:
    python scripts/run_staging.py [--dry-run]

Reads every .md file from drafts/pending/, creates a Notion page in the
Outreach Queue database with Status=Pending, then moves the file to
drafts/staged/ so it won't be re-staged on the next run.

Requires NOTION_QUEUE_DB_ID to be set in .env.local. Run
scripts/setup_queue_db.py first if the database doesn't exist yet.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config.settings as settings
from src.review.queue import NotionQueueClient

PENDING_DIR = Path(__file__).resolve().parents[1] / "drafts" / "pending"
STAGED_DIR = Path(__file__).resolve().parents[1] / "drafts" / "staged"

_FRONTMATTER_RE = re.compile(
    r"^---\n(?P<front>.+?)\n---\n\nSubject:\s*(?P<subject>.+?)\n\n---\n\n(?P<body>.+)$",
    re.DOTALL,
)
_FIELD_RE = re.compile(r"^(?P<key>\w+):\s*(?P<value>.+)$", re.MULTILINE)


def _parse_draft_file(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8").strip()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None

    front = {f.group("key"): f.group("value").strip() for f in _FIELD_RE.finditer(m.group("front"))}
    return {
        "contact_id": front.get("contact_id", ""),
        "contact_name": front.get("contact_name", ""),
        "template_style": front.get("template_style", "general"),
        "hook_used": front.get("hook_used", ""),
        "subject": m.group("subject").strip(),
        "body": m.group("body").strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage pending drafts to Notion.")
    parser.add_argument("--dry-run", action="store_true", help="Parse files without writing to Notion.")
    args = parser.parse_args()

    draft_files = [f for f in PENDING_DIR.glob("*.md") if f.name != ".gitkeep"]

    if not draft_files:
        print("No pending drafts found in drafts/pending/.")
        return

    print(f"Found {len(draft_files)} pending draft(s).\n")

    if not args.dry_run:
        client = NotionQueueClient(settings.NOTION_API_KEY, settings.NOTION_QUEUE_DB_ID)
        STAGED_DIR.mkdir(parents=True, exist_ok=True)

    staged = 0
    skipped = 0

    for path in sorted(draft_files):
        draft = _parse_draft_file(path)
        if not draft or not draft["contact_id"]:
            print(f"  SKIP  {path.name} — could not parse")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  DRY   {draft['contact_name']} ({path.name})")
            staged += 1
            continue

        page_id = client.stage_draft(draft)
        dest = STAGED_DIR / path.name
        path.rename(dest)
        staged += 1
        print(f"  STAGED {draft['contact_name']} → {page_id[:8]}  [{path.name}]")

    suffix = " (dry run)" if args.dry_run else ""
    print(f"\nDone. {staged} staged{suffix}, {skipped} skipped.")


if __name__ == "__main__":
    main()
