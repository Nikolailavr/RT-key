"""
Intercom API.
"""

from __future__ import annotations

from .client import RTKeyApiClient
from . import endpoints

from ..exceptions import RTKeyInvalidResponse
from ..models import Intercom


class RTKeyIntercomApi(RTKeyApiClient):
    """Intercom API."""

    async def get_intercoms(self) -> list[Intercom]:
        """Return all intercoms."""

        response = await self.get(endpoints.INTERCOMS)

        try:
            items = response["data"]["items"]
        except KeyError as err:
            raise RTKeyInvalidResponse(
                "Invalid intercom response"
            ) from err

        return [
            Intercom.from_api(item)
            for item in items
        ]

    async def open_door(
        self,
        device_id: int,
    ) -> None:
        """Open intercom door."""

        await self.post(
            endpoints.OPEN_DOOR.format(
                device_id=device_id,
            )
        )