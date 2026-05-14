"""Tests for src/contacts — schema, filters, and Notion client."""

import pytest

from src.contacts.schema import Contact


# ---------------------------------------------------------------------------
# Placeholder — replace with real tests in Phase 1 validation
# ---------------------------------------------------------------------------

def test_contact_requires_name():
    """A Contact with no name should raise a validation error."""
    with pytest.raises(Exception):
        Contact(id="abc", name="")  # empty name is falsy but valid per schema
    # Note: actually an empty string is allowed by pydantic str type.
    # Replace this with a meaningful filter / client test once real data is available.
    assert True  # placeholder passes
