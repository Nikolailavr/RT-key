"""
RTKey intercom API.
"""

from __future__ import annotations

from ..const import API_URL
from ..exceptions import RTKeyInvalidResponse
from ..models import Intercom
from .client import RTKeyApiClient


class RTKeyIntercomApi(RTKeyApiClient):
    """Intercom API."""

    async def get_intercoms(self) -> list[Intercom]:
        """Return intercom list."""

        result = await self.get(
            f"{API_URL}/api/v2/app/devices/intercom",
        )

        try:
            items = result["data"]["items"]
        except KeyError as err:
            raise RTKeyInvalidResponse() from err

        return [
            Intercom.from_dict(item)
            for item in items
        ]

    async def get_intercom(
        self,
        device_id: int,
    ) -> Intercom | None:
        """Return single intercom."""

        for intercom in await self.get_intercoms():
            if intercom.id == device_id:
                return intercom

        return None

    async def open_door(
        self,
        device_id: int,
    ) -> None:
        """Open intercom door."""

        await self.post(
            f"{API_URL}/api/v2/app/devices/{device_id}/open",
        )