"""Phase 5 — Send emails via Gmail OAuth2.

Uses the school Gmail account for initial outreach and the work account for
reply handling (future phase). Authenticated via OAuth2 refresh token stored
in environment variables — no passwords, no service account JSON files.
"""

import base64
from email.mime.text import MIMEText

import httpx

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class GmailClient:
    def __init__(
        self,
        sender_address: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> None:
        self._sender = sender_address
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token

    def send(self, to: str, subject: str, body: str) -> str:
        """Send a plain-text email. Returns the Gmail message ID on success.

        Raises httpx.HTTPStatusError on API failure.
        """
        token = self._refresh_access_token()
        raw = self._build_raw_message(to, subject, body)
        response = httpx.post(
            _SEND_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"raw": raw},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["id"]

    def _refresh_access_token(self) -> str:
        response = httpx.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _build_raw_message(self, to: str, subject: str, body: str) -> str:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self._sender
        msg["To"] = to
        msg["Subject"] = subject
        return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
