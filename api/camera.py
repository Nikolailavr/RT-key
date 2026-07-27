"""
Camera API.
"""

from __future__ import annotations

from .client import RTKeyApiClient
from . import endpoints

from ..exceptions import RTKeyInvalidResponse
from ..models import Camera


class RTKeyCameraApi(RTKeyApiClient):
    """Camera API."""

    async def get_cameras(self) -> list[Camera]:
        """Return all cameras."""

        response = await self.get(endpoints.CAMERA_LIST)

        try:
            items = response["data"]["items"]
        except KeyError as err:
            raise RTKeyInvalidResponse(
                "Invalid camera response"
            ) from err

        return [
            Camera.from_api(item)
            for item in items
        ]