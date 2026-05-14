"""Fetches contacts from the Notion Network database and returns typed Contact objects."""

from typing import cast

from notion_client import Client

from src.contacts.schema import Contact


class NotionContactClient:
    def __init__(self, api_key: str, db_id: str) -> None:
        self._client = Client(auth=api_key)
        self._db_id = db_id

    def fetch_all(self) -> list[Contact]:
        contacts: list[Contact] = []
        cursor: str | None = None

        while True:
            kwargs: dict = {"database_id": self._db_id, "page_size": 100}
            if cursor:
                kwargs["start_cursor"] = cursor

            response: dict = cast(dict, self._client.databases.query(**kwargs))

            for page in response["results"]:
                contact = self._parse_page(page)
                if contact is not None:
                    contacts.append(contact)

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return contacts

    def _parse_page(self, page: dict) -> Contact | None:
        props = page.get("properties", {})
        name = self._title(props.get("Name"))
        if not name:
            return None  # skip nameless pages

        return Contact(
            id=page["id"],
            name=name,
            email=self._email(props.get("Email")),
            linkedin=self._url(props.get("LinkedIn")),
            location=self._rich_text(props.get("Location")),
            role=self._role(props.get("Role")),
            tags=self._multi_select(props.get("Tags")),
            notes=self._rich_text(props.get("Notes")),
            status=self._select(props.get("Status")),
            organization_ids=self._relation(props.get("Organizations")),
        )

    # --- property parsers ---

    @staticmethod
    def _title(prop: dict | None) -> str:
        if not prop:
            return ""
        parts = prop.get("title", [])
        return "".join(t.get("plain_text", "") for t in parts).strip()

    @staticmethod
    def _email(prop: dict | None) -> str | None:
        if not prop:
            return None
        return prop.get("email") or None

    @staticmethod
    def _url(prop: dict | None) -> str | None:
        if not prop:
            return None
        return prop.get("url") or None

    @staticmethod
    def _rich_text(prop: dict | None) -> str | None:
        if not prop:
            return None
        parts = prop.get("rich_text", [])
        text = "".join(t.get("plain_text", "") for t in parts).strip()
        return text or None

    @staticmethod
    def _select(prop: dict | None) -> str | None:
        if not prop:
            return None
        option = prop.get("select")
        return option.get("name") if option else None

    @staticmethod
    def _multi_select(prop: dict | None) -> list[str]:
        if not prop:
            return []
        return [o["name"] for o in prop.get("multi_select", []) if "name" in o]

    @staticmethod
    def _relation(prop: dict | None) -> list[str]:
        if not prop:
            return []
        return [r["id"] for r in prop.get("relation", []) if "id" in r]

    def _role(self, prop: dict | None) -> str | None:
        """Role can be either a select or rich_text property depending on DB setup."""
        if not prop:
            return None
        ptype = prop.get("type")
        if ptype == "select":
            return self._select(prop)
        if ptype == "rich_text":
            return self._rich_text(prop)
        return None

    # --- write / resolve helpers ---

    def resolve_organization_name(self, page_id: str) -> str | None:
        """Fetch an org page by ID and return its title. Returns None on any error."""
        try:
            page: dict = cast(dict, self._client.pages.retrieve(page_id=page_id))
            props = page.get("properties", {})
            for key in ("Name", "Title", "Company"):
                if key in props:
                    title = self._title(props[key])
                    if title:
                        return title
            return None
        except Exception:
            return None

    def update_notes_and_status(self, page_id: str, notes: str) -> None:
        """Overwrite the Notes field and set Status to 'Enriched'."""
        self._client.pages.update(
            page_id=page_id,
            properties={
                "Notes": {
                    "rich_text": [{"type": "text", "text": {"content": notes[:2000]}}]
                },
                "Status": {"select": {"name": "Enriched"}},
            },
        )
