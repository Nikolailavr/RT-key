"""
Base RTKey HTTP client.
"""

from __future__ import annotations

from typing import Any

import aiohttp

from ..exceptions import (
    RTKeyApiError,
    RTKeyAuthError,
    RTKeyConnectionError,
)

from .session import RTKeySession


class RTKeyApiClient:
    """Base HTTP client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        auth: RTKeySession,
    ) -> None:

        self._session = session
        self._auth = auth

    def _headers(
        self,
        auth: bool = True,
    ) -> dict[str, str]:

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-device-id": self._auth.device_id,
        }

        if auth and self._auth.authenticated:
            headers["Authorization"] = self._auth.authorization

        return headers

    async def get(
        self,
        url: str,
        **kwargs,
    ) -> dict[str, Any]:

        try:

            async with self._session.get(
                url,
                headers=self._headers(),
                **kwargs,
            ) as response:

                if response.status == 401:
                    raise RTKeyAuthError()

                if response.status >= 400:
                    raise RTKeyApiError(await response.text())

                return await response.json()

        except aiohttp.ClientError as err:

            raise RTKeyConnectionError(str(err)) from err

    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:

        try:

            async with self._session.post(
                url,
                json=json,
                headers=self._headers(auth),
            ) as response:

                if response.status == 401:
                    raise RTKeyAuthError()

                if response.status >= 400:
                    raise RTKeyApiError(await response.text())

                return await response.json()

        except aiohttp.ClientError as err:

            raise RTKeyConnectionError(str(err)) from err


    async def get_bytes(
        self,
        url: str,
    ) -> bytes:
        """Download binary data."""

        try:
            async with self._session.get(
                url,
                headers=self._headers(),
            ) as response:

                if response.status == 401:
                    raise RTKeyAuthError()

                if response.status >= 400:
                    raise RTKeyApiError(await response.text())

                return await response.read()

        except aiohttp.ClientError as err:
            raise RTKeyConnectionError(str(err)) from err