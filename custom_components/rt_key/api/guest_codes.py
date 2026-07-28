"""Guest PIN codes service for Rostelecom Key."""
from typing import Any, Dict, List
from ..const import API_GUEST_CODES_URL, LOGGER
from .base import BaseService


class GuestCodeService(BaseService):
    """Handles generating temporary access PIN codes for visitors and couriers."""

    async def async_get_guest_codes(self) -> List[Dict[str, Any]]:
        """Fetch list of active guest access codes."""
        data = await self._async_get(API_GUEST_CODES_URL)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("guest_codes") or data.get("codes") or []
        return []

    async def async_create_guest_code(
        self,
        intercom_id: str,
        duration_hours: int = 24,
        max_uses: int = 1,
        description: str = "HA Guest Code",
    ) -> Dict[str, Any]:
        """Generate temporary guest PIN code for intercom/barrier entry."""
        payload = {
            "device_id": intercom_id,
            "duration_hours": duration_hours,
            "max_uses": max_uses,
            "description": description,
        }
        LOGGER.info(
            "Generating guest PIN code for intercom %s (valid %sh)", intercom_id, duration_hours
        )
        return await self._async_post(API_GUEST_CODES_URL, payload)

    async def async_revoke_guest_code(self, code_id: str) -> bool:
        """Revoke active guest access code."""
        url = f"{API_GUEST_CODES_URL}/{code_id}/revoke"
        await self._async_post(url)
        return True
