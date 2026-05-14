"""Phase 2 — Summarize search results into a single outreach hook.

Calls the configured open model via OpenRouter (OpenAI-compatible endpoint)
and returns one concise sentence suitable for personalizing an email opener,
or None if the model signals there is no usable hook.

Model is driven by OPENROUTER_MODEL in .env — swap without touching code.
"""

from pathlib import Path

import httpx

import config.settings as settings
from src.contacts.schema import Contact

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "config" / "prompts" / "enrich.txt"
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_NO_HOOK_SENTINEL = "NO_HOOK"


def summarize_contact(contact: Contact, snippets: list[str]) -> str | None:
    """Return a one-sentence hook for this contact, or None if nothing useful found."""
    if not snippets:
        return None

    prompt = _build_prompt(contact, snippets)
    raw = _call_openrouter(prompt)
    if not raw or raw.strip().upper() == _NO_HOOK_SENTINEL:
        return None
    return raw.strip()


def _build_prompt(contact: Contact, snippets: list[str]) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    formatted_snippets = "\n\n".join(
        f"[{i + 1}] {s.strip()}" for i, s in enumerate(snippets)
    )
    return template.format(
        name=contact.name,
        firm=contact.organization_name or contact.role or "their firm",
        location=contact.location or "unknown location",
        snippets=formatted_snippets,
    )


def _call_openrouter(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/outreach-auto",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 80,
        "temperature": 0.2,
    }
    response = httpx.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        return None
    return choices[0].get("message", {}).get("content")
