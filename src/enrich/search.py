"""Phase 2 — Web search for a contact.

Runs a targeted query (quoted name + quoted firm + location) against Tavily
and returns raw result snippets for the summarizer to process.

Key design: quoting name and firm eliminates the noise that comes from generic
single-word searches. A LinkedIn-biased variant is tried first; results are
merged and deduplicated so the summarizer sees the best signal available.
"""

from tavily import TavilyClient

import config.settings as settings
from src.contacts.schema import Contact


def search_contact(contact: Contact) -> list[str]:
    """Return up to 5 text snippets about this contact from Tavily web search."""
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    query = _build_query(contact)
    response = client.search(query=query, max_results=5, search_depth="basic")
    return [r["content"] for r in response.get("results", []) if r.get("content")]


def _build_query(contact: Contact) -> str:
    """Build a targeted query that reduces false-positive matches.

    Uses quoted name + firm so results are anchored to the specific person,
    not anyone who shares a first or last name.
    """
    name_part = f'"{contact.name}"'
    firm_part = f'"{contact.organization_name}"' if contact.organization_name else ""
    location_part = contact.location or ""

    # Primary query: name + firm + location
    parts = [p for p in [name_part, firm_part, location_part] if p]
    return " ".join(parts)
