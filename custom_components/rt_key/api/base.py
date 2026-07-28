"""Base HTTP client service for Rostelecom Key API."""
import logging
import uuid
from typing import Any, Dict, Optional
import aiohttp

from ..const import LOGGER
from .exceptions import RostelecomKeyApiError, RostelecomKeyAuthError, RostelecomKeyNetworkError


class BaseService:
    """Base class for API services sharing HTTP session and token state."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token_getter: Any,
        refresh_token_getter: Any,
        token_setter: Any,
        device_id_getter: Any = None,
    ) -> None:
        """Initialize base service with shared session state."""
        self._session = session
        self._get_token = token_getter
        self._get_refresh_token = refresh_token_getter
        self._set_token = token_setter
        self._get_device_id = device_id_getter or (lambda: str(uuid.uuid4()))

    @property
    def token(self) -> Optional[str]:
        """Return current access token."""
        return self._get_token()

    @property
    def refresh_token(self) -> Optional[str]:
        """Return current refresh token."""
        return self._get_refresh_token()

    @property
    def device_id(self) -> str:
        """Return device ID."""
        return self._get_device_id()

    def _headers(self) -> Dict[str, str]:
        """Build HTTP request headers with JWT authorization."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru",
            "Content-Type": "application/json",
            "Origin": "https://key.rt.ru",
            "Referer": "https://key.rt.ru/",
            "X-Device-Id": self.device_id,
            "X-Request-Id": str(uuid.uuid4()),
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _async_get(self, url: str) -> Any:
        """Execute GET request with automatic token refresh on HTTP 401."""
        try:
            async with self._session.get(url, headers=self._headers()) as response:
                if response.status == 401 and self.refresh_token:
                    LOGGER.info("Token expired during GET %s. Attempting refresh...", url)
                    await self._async_refresh_token_callback()
                    async with self._session.get(url, headers=self._headers()) as retry_resp:
                        if retry_resp.status == 200:
                            return await retry_resp.json()
                        raise RostelecomKeyAuthError(
                            f"GET failed after token refresh (HTTP {retry_resp.status})"
                        )

                if response.status == 200:
                    return await response.json()
                if response.status == 401:
                    raise RostelecomKeyAuthError("Unauthorized access. Token invalid or expired.")

                text = await response.text()
                raise RostelecomKeyApiError(f"GET {url} failed with status {response.status}: {text}")

        except aiohttp.ClientError as err:
            raise RostelecomKeyNetworkError(f"Network error executing GET {url}: {err}") from err

    async def _async_post(self, url: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        """Execute POST request with automatic token refresh on HTTP 401."""
        try:
            kwargs: Dict[str, Any] = {"headers": self._headers()}
            if payload is not None:
                kwargs["json"] = payload

            async with self._session.post(url, **kwargs) as response:
                if response.status == 401 and self.refresh_token:
                    LOGGER.info("Token expired during POST %s. Attempting refresh...", url)
                    await self._async_refresh_token_callback()
                    kwargs["headers"] = self._headers()
                    async with self._session.post(url, **kwargs) as retry_resp:
                        if retry_resp.status in (200, 201, 204):
                            try:
                                return await retry_resp.json()
                            except Exception:
                                return {}
                        text = await retry_resp.text()
                        raise RostelecomKeyAuthError(f"POST failed after token refresh with status {retry_resp.status}: {text}")

                if response.status in (200, 201, 204):
                    try:
                        return await response.json()
                    except Exception:
                        return {}

                text = await response.text()
                raise RostelecomKeyApiError(f"POST {url} failed with status {response.status}: {text}")

        except aiohttp.ClientError as err:
            raise RostelecomKeyNetworkError(f"Network error executing POST {url}: {err}") from err

    async def _async_refresh_token_callback(self) -> None:
        """Override in child or main client if refresh callback required."""
        pass
