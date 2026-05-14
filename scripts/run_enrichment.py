"""Phase 2 CLI — Enrich N contacts and write hooks back to Notion.

Usage:
    python scripts/run_enrichment.py [--limit N]

For each ready contact (up to --limit):
  1. Resolve organization name via Notion API
  2. Web-search the contact via Tavily
  3. Summarize to one hook sentence via OpenRouter
  4. Write hook + date stamp back to Notion Notes; set Status = Enriched

Exit criteria: Notes field populated with one usable hook per contact.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config.settings as settings
from src.contacts.filters import ready_for_outreach
from src.contacts.notion_client import NotionContactClient
from src.enrich.search import search_contact
from src.enrich.summarize import summarize_contact
from src.enrich.writeback import write_hook


def main(limit: int) -> None:
    notion = NotionContactClient(settings.NOTION_API_KEY, settings.NOTION_NETWORK_DB_ID)

    print("Fetching contacts from Notion…")
    all_contacts = notion.fetch_all()
    ready = ready_for_outreach(all_contacts)
    print(f"Fetched {len(all_contacts)} total | {len(ready)} ready for outreach")

    batch = ready[:limit]
    print(f"Enriching {len(batch)} contact(s).\n")

    skipped = 0
    enriched = 0

    for contact in batch:
        print(f"  {contact.name}")

        # Resolve org name for targeted search query
        org_name = None
        if contact.organization_ids:
            org_name = notion.resolve_organization_name(contact.organization_ids[0])
        contact = contact.model_copy(update={"organization_name": org_name})

        print(f"    org: {org_name or '—'}")

        # Web search
        snippets = search_contact(contact)
        print(f"    snippets: {len(snippets)}")

        if not snippets:
            print("    → no search results, skipping\n")
            skipped += 1
            continue

        # Summarize
        hook = summarize_contact(contact, snippets)
        if not hook:
            print("    → no usable hook found, skipping\n")
            skipped += 1
            continue

        print(f"    hook: {hook}")

        # Write back to Notion
        write_hook(contact, hook, notion)
        print("    → written to Notion\n")
        enriched += 1

    print(f"Done. Enriched: {enriched} | Skipped: {skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich contacts with web search hooks.")
    parser.add_argument("--limit", type=int, default=5, help="Max contacts to process (default: 5)")
    args = parser.parse_args()
    main(args.limit)
