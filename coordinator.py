"""
DataUpdateCoordinator for RTKey.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import RTKeyApi
from .api.session import RTKeySession

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
)

from .models import (
    Camera,
    Intercom,
    RTKeyDevice,
)

_LOGGER = logging.getLogger(__name__)


class RTKeyCoordinator(
    DataUpdateCoordinator[list[RTKeyDevice]]
):
    """RTKey coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        token: str,
    ) -> None:

        self.session = RTKeySession(
            access_token=token,
        )

        self.api = RTKeyApi(
            async_get_clientsession(hass),
            self.session,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(
        self,
    ) -> list[RTKeyDevice]:

        try:
            intercoms = await self.api.intercom.get_intercoms()
            cameras = await self.api.camera.get_cameras()
        except Exception as err:

            raise UpdateFailed(
                str(err)
            ) from err

        devices = self._merge(
            intercoms,
            cameras,
        )

        self.devices = {
            device.intercom.id: device
            for device in devices
        }

        return devices

    @staticmethod
    def _merge(
        intercoms: list[Intercom],
        cameras: list[Camera],
    ) -> list[RTKeyDevice]:

        camera_index = {
            camera.camera_id: camera
            for camera in cameras
        }

        devices: list[RTKeyDevice] = []

        for intercom in intercoms:

            camera = None

            if intercom.camera_id:

                camera = camera_index.get(
                    intercom.camera_id
                )

            devices.append(
                RTKeyDevice(
                    intercom=intercom,
                    camera=camera,
                )
            )

        return devices