"""Intercom & door lock service for Rostelecom Key."""
from typing import Any, Dict, List
from ..const import API_DEVICES_URL, API_INTERCOMS_URL, LOGGER
from .base import BaseService


class IntercomService(BaseService):
    """Handles intercom door unlocking and intercom state management."""

    async def async_get_intercoms(self) -> List[Dict[str, Any]]:
        """Fetch list of user intercoms/doors."""
        urls = [API_DEVICES_URL, API_INTERCOMS_URL]
        for url in urls:
            try:
                data = await self._async_get(url)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    inner = data.get("data")
                    if isinstance(inner, dict):
                        devs = (
                            inner.get("devices")
                            or inner.get("intercoms")
                            or inner.get("doors")
                            or inner.get("items")
                        )
                        if isinstance(devs, list) and devs:
                            return devs
                    elif isinstance(inner, list) and inner:
                        return inner

                    devs = (
                        data.get("devices")
                        or data.get("intercoms")
                        or data.get("doors")
                        or data.get("items")
                    )
                    if isinstance(devs, list) and devs:
                        return devs
            except Exception as err:
                LOGGER.debug("Could not fetch intercoms from %s: %s", url, err)
        return []

    async def async_open_intercom(self, intercom_id: str) -> bool:
        """Send unlock door command to intercom device by ID (POST /api/v2/app/devices/{id}/open)."""
        url = f"{API_DEVICES_URL}/{intercom_id}/open"
        LOGGER.info("Sending unlock command to intercom device %s: %s", intercom_id, url)
        await self._async_post(url)
        return True

    async def async_get_intercom_details(self, intercom_id: str) -> Dict[str, Any]:
        """Fetch detailed status for specific intercom."""
        url = f"{API_DEVICES_URL}/{intercom_id}"
        try:
            return await self._async_get(url)
        except Exception:
            fallback_url = f"{API_INTERCOMS_URL}/{intercom_id}"
            return await self._async_get(fallback_url)
