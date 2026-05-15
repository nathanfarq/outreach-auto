"""Phase 3 CLI — Draft emails for enriched contacts and stage for review.

Usage:
    python scripts/run_drafting.py [--limit N]

Reads contacts with Status='Enriched' from Notion, runs the style picker,
calls Claude Haiku via OpenRouter for a personalized opener, assembles the
full email, and saves each draft to drafts/pending/{contact_id[:8]}.md.
"""

import argparse
import datetime
import sys
from pathlib import Path

# Allow running from repo root without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config.settings as settings
from src.contacts.notion_client import NotionContactClient
from src.draft.assembler import assemble_draft
from src.draft.personalize import generate_opener
from src.draft.style_picker import pick_style
from src.draft.template_loader import load_templates

DRAFTS_DIR = Path(__file__).resolve().parents[1] / "drafts" / "pending"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate email drafts for enriched contacts.")
    parser.add_argument("--limit", type=int, default=5, help="Max drafts to generate (default 5)")
    args = parser.parse_args()

    client = NotionContactClient(settings.NOTION_API_KEY, settings.NOTION_NETWORK_DB_ID)
    all_contacts = client.fetch_all()
    enriched = [c for c in all_contacts if c.status == "Enriched"]

    if not enriched:
        print("No enriched contacts found. Run scripts/run_enrichment.py first.")
        return

    print(f"Found {len(enriched)} enriched contact(s). Drafting up to {args.limit}.\n")

    templates = load_templates()
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    skipped = 0

    for contact in enriched[: args.limit]:
        style = pick_style(contact)
        opener = generate_opener(contact, style)

        if opener is None:
            print(f"  SKIP  {contact.name} — no opener generated (missing hook?)")
            skipped += 1
            continue

        draft = assemble_draft(contact, style, opener, templates)
        _save_draft(draft)
        saved += 1
        print(f"  DRAFT {contact.name} → {style} style  [{draft['contact_id'][:8]}]")

    print(f"\nDone. {saved} draft(s) saved to {DRAFTS_DIR}  ({skipped} skipped)")


def _save_draft(draft: dict) -> None:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    path = DRAFTS_DIR / f"{draft['contact_id'][:8]}.md"
    content = (
        f"---\n"
        f"contact_id: {draft['contact_id']}\n"
        f"contact_name: {draft['contact_name']}\n"
        f"template_style: {draft['template_style']}\n"
        f"hook_used: {draft['hook_used']}\n"
        f"created_at: {ts}\n"
        f"---\n\n"
        f"Subject: {draft['subject']}\n\n"
        f"---\n\n"
        f"{draft['body']}\n"
    )
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
