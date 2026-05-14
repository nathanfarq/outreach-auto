"""Filter functions that decide which contacts are actionable."""

import config.settings as settings
from src.contacts.schema import Contact


def ready_for_outreach(contacts: list[Contact]) -> list[Contact]:
    """Return contacts that are ready for a first cold email.

    A contact qualifies when ALL three hold:
      1. Status is blank or in settings.READY_STATUSES
      2. LinkedIn URL is set
      3. At least one Organization relation is set
    """
    results = []
    for c in contacts:
        status_key = c.status if c.status is not None else ""
        if (
            status_key in settings.READY_STATUSES
            and c.linkedin
            and c.organization_ids
        ):
            results.append(c)
    return results
