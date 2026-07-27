"""
RTKey authentication API.
"""

from __future__ import annotations

from datetime import UTC, datetime

import jwt

from ..const import (
    API_URL,
    AUTH_URL,
)
from ..exceptions import RTKeyInvalidResponse
from .client import RTKeyApiClient


class RTKeyAuthApi(RTKeyApiClient):
    """Authentication API."""

    async def send_code(
        self,
        phone: str,
    ) -> str:
        """Request SMS code."""

        result = await self.post(
            f"{AUTH_URL}/identity/api/v1/authorization/send_code",
            json={
                "phoneNumber": phone,
            },
            auth=False,
        )
        try:
            return result["data"]["codeId"]
        except KeyError as err:
            raise RTKeyInvalidResponse() from err

    async def login(
        self,
        code: str,
        code_id: str,
    ) -> str:
        """Login using SMS code."""

        result = await self.post(
            f"{AUTH_URL}/identity/api/v1/authorization/login",
            json={
                "code": code,
                "codeId": code_id,
            },
            auth=False,
        )

        try:
            token = result["data"]["accessToken"]
        except KeyError as err:
            raise RTKeyInvalidResponse() from err

        expires_at = None

        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["RS256"],
            )

            if "exp" in payload:
                expires_at = datetime.fromtimestamp(
                    payload["exp"],
                    UTC,
                )

        except Exception:
            pass

        self._auth.update(
            token=token,
            expires_at=expires_at,
        )
        return token

    async def current_user(self) -> dict:
        """Return current user."""

        result = await self.get(
            f"{API_URL}/api/v3/app/users/current",
        )

        try:
            return result["data"]
        except KeyError as err:
            raise RTKeyInvalidResponse() from err

    async def authenticate(
        self,
        phone: str,
        code: str,
        code_id: str,
    ) -> dict:
        """Authenticate user."""

        await self.send_code(phone)
        await self.login(code, code_id)

        return await self.current_user()