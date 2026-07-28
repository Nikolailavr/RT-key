"""Barrier & gate control service for Rostelecom Key."""
from typing import Any, Dict, List
from ..const import API_BARRIERS_URL, API_DEVICES_URL, LOGGER
from .base import BaseService


class BarrierService(BaseService):
    """Handles barrier/gate opening and auto license plate recognition control."""

    async def async_get_barriers(self) -> List[Dict[str, Any]]:
        """Fetch list of user barriers/gates."""
        try:
            data = await self._async_get(API_BARRIERS_URL)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return (
                    data.get("data")
                    or data.get("devices")
                    or data.get("barriers")
                    or data.get("gates")
                    or data.get("items")
                    or []
                )
        except Exception as err:
            LOGGER.debug("Could not fetch barriers: %s", err)
        return []

    async def async_open_barrier(self, barrier_id: str) -> bool:
        """Send open gate command to barrier device by ID."""
        url = f"{API_DEVICES_URL}/{barrier_id}/open"
        LOGGER.info("Sending open barrier command to device %s: %s", barrier_id, url)
        await self._async_post(url)
        return True

    async def async_toggle_auto_plate_recognition(
        self, barrier_id: str, enabled: bool
    ) -> bool:
        """Enable or disable Automatic License Plate Recognition (ALPR) for barrier."""
        url = f"{API_BARRIERS_URL}/{barrier_id}/alpr"
        payload = {"alpr_enabled": enabled}
        await self._async_post(url, payload)
        return True
