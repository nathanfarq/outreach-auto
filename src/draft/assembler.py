"""Phase 3 — Assemble the final email draft.

Combines the Claude-generated opener with the template subject and body,
substituting contact fields (name, firm, etc.) into template placeholders.
Returns a ready-to-review dict with 'subject', 'body', and 'contact_id'.
"""
