"""
RTKey API session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import uuid


@dataclass(slots=True)
class RTKeySession:
    """RTKey session."""

    access_token: str | None = None

    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    expires_at: datetime | None = None

    @property
    def authenticated(self) -> bool:
        """Return True if authenticated."""

        return self.access_token is not None

    @property
    def authorization(self) -> str:
        """Authorization header."""

        if not self.access_token:
            return ""

        return f"Bearer {self.access_token}"

    @property
    def expired(self) -> bool:
        """Check token expiration."""

        if self.expires_at is None:
            return False

        return datetime.now(UTC) >= self.expires_at

    @property
    def headers(self) -> dict[str, str]:
        """Common authorization headers."""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-device-id": self.device_id,
        }

        if self.access_token:
            headers["Authorization"] = self.authorization

        return headers

    def update(
        self,
        token: str,
        expires_at: datetime | None,
    ) -> None:
        """Update session."""

        self.access_token = token
        self.expires_at = expires_at

    def clear(self) -> None:
        """Logout."""

        self.access_token = None
        self.expires_at = None