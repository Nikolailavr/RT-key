"""
Base RTKey HTTP client.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from ..exceptions import (
    RTKeyApiError,
    RTKeyAuthError,
    RTKeyConnectionError,
)
from .session import RTKeySession

_LOGGER = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=30)


class RTKeyApiClient:
    """Base HTTP client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        auth: RTKeySession,
    ) -> None:
        """Initialize client."""

        self._session = session
        self._auth = auth

    def _headers(
        self,
        auth: bool = True,
    ) -> dict[str, str]:
        """Build request headers."""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-device-id": self._auth.device_id,
        }

        if auth and self._auth.access_token:
            headers["Authorization"] = self._auth.authorization

        return headers

    async def _request(
        self,
        method: str,
        url: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Perform HTTP request."""

        _LOGGER.debug("%s %s", method, url)

        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers(auth),
                timeout=_TIMEOUT,
                **kwargs,
            ) as response:

                if response.status == 401:
                    raise RTKeyAuthError()

                if response.status >= 400:
                    raise RTKeyApiError(
                        f"{response.status}: {await response.text()}"
                    )

                content_type = response.headers.get(
                    "Content-Type",
                    "",
                )

                if "application/json" in content_type:
                    try:
                        return await response.json()
                    except aiohttp.ContentTypeError as err:
                        raise RTKeyApiError(
                            "Invalid JSON response"
                        ) from err

                return await response.read()

        except aiohttp.ClientError as err:
            raise RTKeyConnectionError(str(err)) from err

    async def get(
        self,
        url: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """HTTP GET."""

        result = await self._request(
            "GET",
            url,
            auth=auth,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise RTKeyApiError("Expected JSON response")

        return result

    async def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """HTTP POST."""

        result = await self._request(
            "POST",
            url,
            json=json,
            auth=auth,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise RTKeyApiError("Expected JSON response")

        return result

    async def put(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """HTTP PUT."""

        result = await self._request(
            "PUT",
            url,
            json=json,
            auth=auth,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise RTKeyApiError("Expected JSON response")

        return result

    async def delete(
        self,
        url: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """HTTP DELETE."""

        result = await self._request(
            "DELETE",
            url,
            auth=auth,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise RTKeyApiError("Expected JSON response")

        return result

    async def get_bytes(
        self,
        url: str,
        *,
        auth: bool = True,
    ) -> bytes:
        """Download binary data."""

        result = await self._request(
            "GET",
            url,
            auth=auth,
        )

        if not isinstance(result, bytes):
            raise RTKeyApiError("Expected binary response")

        return result