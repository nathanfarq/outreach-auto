"""Phase 3 — Generate a personalized 1-2 sentence opener via Claude Haiku.

This is the only LLM call in the drafting layer. It takes the enrichment hook
from Notes and produces a short, natural-sounding opening that will be prepended
to the chosen template body.

Uses OpenRouter (same httpx pattern as Phase 2 summarize.py).
Model is controlled by DRAFTING_MODEL in .env — defaults to Claude Haiku.
"""

from pathlib import Path

import httpx

import config.settings as settings
from src.contacts.schema import Contact
from src.draft._utils import extract_hook

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "config" / "prompts" / "personalize.txt"
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_opener(contact: Contact, style: str) -> str | None:
    """Return a 1-2 sentence opener, or None if no hook is available."""
    hook = extract_hook(contact.notes)
    if not hook:
        return None
    prompt = _build_prompt(contact, hook, style)
    return _call_openrouter(prompt)


def _build_prompt(contact: Contact, hook: str, style: str) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(
        name=contact.name,
        firm=contact.organization_name or contact.role or "their organization",
        hook=hook,
        style=style,
    )


def _call_openrouter(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/outreach-auto",
    }
    payload = {
        "model": settings.DRAFTING_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.7,
    }
    response = httpx.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    choices = response.json().get("choices", [])
    if not choices:
        return None
    text = choices[0].get("message", {}).get("content", "").strip()
    return text or None
