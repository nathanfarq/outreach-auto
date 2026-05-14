"""Phase 3 — Process approval / rejection decisions.

Reads review queue items whose Status was changed to 'Approved' or 'Rejected'
by the founder in Notion, and routes approved drafts to the send queue.
No draft is ever sent without an explicit 'Approved' status.
"""
