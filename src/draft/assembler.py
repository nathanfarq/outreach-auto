"""Phase 3 — Assemble the final email draft.

Combines the Claude-generated opener with the template subject and body,
substituting contact fields (name, firm, personalized_opener) into template
placeholders. Returns a ready-to-review dict with all metadata for the
markdown file writer.
"""

from src.contacts.schema import Contact
from src.draft._utils import extract_hook


def assemble_draft(
    contact: Contact,
    style: str,
    opener: str | None,
    templates: dict,
) -> dict:
    """Return a draft dict ready to be serialized as a markdown file."""
    template = templates[style]
    firm = contact.organization_name or contact.role or "your organization"
    hook = extract_hook(contact.notes)

    subject = template["subject"]
    body = template["body"].format(
        personalized_opener=opener or "",
        name=contact.name,
        firm=firm,
    ).strip()

    return {
        "contact_id": contact.id,
        "contact_name": contact.name,
        "template_style": style,
        "hook_used": hook or "",
        "subject": subject,
        "body": body,
    }
