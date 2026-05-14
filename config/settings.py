"""Central settings module. Load once at startup; import from anywhere."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env.local")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


# Notion
NOTION_API_KEY: str = _require("NOTION_API_KEY")
NOTION_NETWORK_DB_ID: str = _require("NOTION_NETWORK_DB_ID")

# Tavily (Phase 2 — web search)
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# OpenRouter (Phase 2)
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

# Anthropic (Phase 3)
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

# Gmail — school (initial outreach)
GMAIL_SCHOOL_ADDRESS: str = os.getenv("GMAIL_SCHOOL_ADDRESS", "")
GMAIL_SCHOOL_CLIENT_ID: str = os.getenv("GMAIL_SCHOOL_CLIENT_ID", "")
GMAIL_SCHOOL_CLIENT_SECRET: str = os.getenv("GMAIL_SCHOOL_CLIENT_SECRET", "")
GMAIL_SCHOOL_REFRESH_TOKEN: str = os.getenv("GMAIL_SCHOOL_REFRESH_TOKEN", "")

# Gmail — work (reply handling, Phase 4+)
GMAIL_WORK_ADDRESS: str = os.getenv("GMAIL_WORK_ADDRESS", "")
GMAIL_WORK_CLIENT_ID: str = os.getenv("GMAIL_WORK_CLIENT_ID", "")
GMAIL_WORK_CLIENT_SECRET: str = os.getenv("GMAIL_WORK_CLIENT_SECRET", "")
GMAIL_WORK_REFRESH_TOKEN: str = os.getenv("GMAIL_WORK_REFRESH_TOKEN", "")

# Outreach filter — statuses that mean "this contact is ready to be emailed".
# Add "To reconnect" here when you want warm re-engagement in the same pipeline.
READY_STATUSES: frozenset[str] = frozenset({"", "No contact", "To contact", "To reconnect"})
