"""Typed representation of a contact row from the Notion Network database."""

from pydantic import BaseModel


class Contact(BaseModel):
    id: str                           # Notion page ID
    name: str
    email: str | None = None
    linkedin: str | None = None       # Notion URL property
    location: str | None = None
    role: str | None = None
    tags: list[str] = []              # Notion multi-select
    notes: str | None = None
    status: str | None = None         # Notion select value
    organization_ids: list[str] = []  # raw Notion relation page IDs
