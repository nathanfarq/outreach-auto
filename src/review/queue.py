"""Phase 4 — Stage email drafts for human review.

Writes assembled drafts to a Notion "Outreach Queue" database with
Status = 'Pending'. The founder reviews and sets Status to Approved,
Rejected, or Edited (body changed in Notion) before any send is triggered.
"""

import datetime
from typing import cast

from notion_client import Client

_STATUSES = ("Pending", "Approved", "Rejected", "Edited", "Sent")
_STYLES = ("general", "direct", "curious")


class NotionQueueClient:
    def __init__(self, api_key: str, queue_db_id: str) -> None:
        if not queue_db_id:
            raise RuntimeError(
                "NOTION_QUEUE_DB_ID is not set. "
                "Run scripts/setup_queue_db.py first, then add the ID to .env.local."
            )
        self._client = Client(auth=api_key)
        self._db_id = queue_db_id

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def stage_draft(self, draft: dict) -> str:
        """Create a Notion page for the draft with Status=Pending.

        Returns the new page ID.
        """
        now = datetime.datetime.now().isoformat(timespec="seconds")
        response = cast(
            dict,
            self._client.pages.create(
                parent={"database_id": self._db_id},
                properties=self._build_properties(draft, now),
            ),
        )
        return response["id"]

    def update_status(self, page_id: str, status: str) -> None:
        if status not in _STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {_STATUSES}.")
        self._client.pages.update(
            page_id=page_id,
            properties={"Status": {"select": {"name": status}}},
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def fetch_by_status(self, status: str) -> list[dict]:
        """Return all queue pages matching the given Status, newest first."""
        results: list[dict] = []
        cursor: str | None = None

        while True:
            kwargs: dict = {
                "database_id": self._db_id,
                "page_size": 100,
                "filter": {"property": "Status", "select": {"equals": status}},
                "sorts": [{"property": "Created", "direction": "descending"}],
            }
            if cursor:
                kwargs["start_cursor"] = cursor

            response = cast(dict, self._client.databases.query(**kwargs))

            for page in response["results"]:
                item = self._parse_page(page)
                if item is not None:
                    results.append(item)

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_properties(draft: dict, created_at: str) -> dict:
        return {
            "Name": {
                "title": [{"type": "text", "text": {"content": draft["contact_name"]}}]
            },
            "Status": {"select": {"name": "Pending"}},
            "Contact ID": {
                "rich_text": [{"type": "text", "text": {"content": draft["contact_id"]}}]
            },
            "Subject": {
                "rich_text": [{"type": "text", "text": {"content": draft["subject"][:2000]}}]
            },
            "Body": {
                "rich_text": [{"type": "text", "text": {"content": draft["body"][:2000]}}]
            },
            "Style": {"select": {"name": draft.get("template_style", "general")}},
            "Hook": {
                "rich_text": [
                    {"type": "text", "text": {"content": draft.get("hook_used", "")[:2000]}}
                ]
            },
            "Created": {"date": {"start": created_at}},
        }

    @staticmethod
    def _rich_text_value(prop: dict | None) -> str:
        if not prop:
            return ""
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", [])).strip()

    @staticmethod
    def _select_value(prop: dict | None) -> str:
        if not prop:
            return ""
        option = prop.get("select")
        return option.get("name", "") if option else ""

    @staticmethod
    def _title_value(prop: dict | None) -> str:
        if not prop:
            return ""
        return "".join(t.get("plain_text", "") for t in prop.get("title", [])).strip()

    def _parse_page(self, page: dict) -> dict | None:
        props = page.get("properties", {})
        contact_id = self._rich_text_value(props.get("Contact ID"))
        if not contact_id:
            return None
        return {
            "queue_page_id": page["id"],
            "contact_id": contact_id,
            "contact_name": self._title_value(props.get("Name")),
            "subject": self._rich_text_value(props.get("Subject")),
            "body": self._rich_text_value(props.get("Body")),
            "template_style": self._select_value(props.get("Style")),
            "hook_used": self._rich_text_value(props.get("Hook")),
            "status": self._select_value(props.get("Status")),
        }
