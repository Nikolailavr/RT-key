"""
Authentication API for RTKey.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .client import RTKeyApiClient
from . import endpoints
from ..exceptions import RTKeyInvalidResponse
from ..models import User


class RTKeyAuthApi(RTKeyApiClient):
    """Authentication API."""

    async def send_code(self, phone: str) -> str:
        """Request SMS code."""

        response = await self.post(
            endpoints.SEND_CODE,
            json={
                "phoneNumber": phone,
            },
            auth=False,
        )

        try:
            return response["data"]["codeId"]
        except KeyError as err:
            raise RTKeyInvalidResponse(
                "codeId not found in response"
            ) from err

    async def login(
        self,
        code: str,
        code_id: str,
    ) -> str:
        """Login using SMS code."""

        response = await self.post(
            endpoints.LOGIN,
            json={
                "code": code,
                "codeId": code_id,
            },
            auth=False,
        )

        try:
            token = response["data"]["accessToken"]

            expires = response["data"].get("expiredAt")

            expires_at = (
                datetime.fromisoformat(
                    expires.replace("Z", "+00:00")
                )
                if expires
                else None
            )

            self._auth.update(
                token=token,
                expires_at=expires_at,
            )

            return token

        except KeyError as err:
            raise RTKeyInvalidResponse(
                "Invalid login response"
            ) from err

async def current_user(self) -> User:

    response = await self.get(
        endpoints.CURRENT_USER,
    )

    return User.from_api(
        response["data"]
    )