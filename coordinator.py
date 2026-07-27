"""DataUpdateCoordinator for RTKey."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import RTKeyApi
from .api.session import RTKeySession
from .const import DOMAIN, SCAN_INTERVAL
from .models import Camera, Intercom, RTKeyDevice

_LOGGER = logging.getLogger(__name__)


class RTKeyCoordinator(DataUpdateCoordinator[list[RTKeyDevice]]):
    """RTKey coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        token: str,
    ) -> None:
        """Initialize RTKey coordinator."""
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

        self.devices: dict[int | str, RTKeyDevice] = {}

    async def _async_update_data(self) -> list[RTKeyDevice]:
        """Fetch data from RTKey API."""
        try:
            intercoms = await self.api.intercom.get_intercoms()
            cameras = await self.api.camera.get_cameras()
        except Exception as err:
            # Если API возвращает 401/403 или ошибку авторизации
            err_str = str(err).lower()
            if "unauthorized" in err_str or "401" in err_str or "token" in err_str:
                _LOGGER.error("Ошибка авторизации RTKey: %s", err)
                raise ConfigEntryAuthFailed("Сессия истекла. Требуется повторная авторизация.") from err

            _LOGGER.error("Ошибка обновления данных RTKey: %s", err)
            raise UpdateFailed(f"Не удалось получить данные с сервера: {err}") from err

        devices = self._merge(
            intercoms,
            cameras,
        )

        # Безопасно формируем словарь устройств по ID домофона
        self.devices = {
            device.intercom.id: device
            for device in devices
            if device.intercom and getattr(device.intercom, "id", None) is not None
        }

        return devices

    @staticmethod
    def _merge(
        intercoms: list[Intercom],
        cameras: list[Camera],
    ) -> list[RTKeyDevice]:
        """Merge cameras into intercom devices where applicable."""
        camera_index = {
            camera.camera_id: camera
            for camera in cameras
            if getattr(camera, "camera_id", None) is not None
        }

        devices: list[RTKeyDevice] = []

        for intercom in intercoms:
            camera = None
            if getattr(intercom, "camera_id", None):
                camera = camera_index.get(intercom.camera_id)

            devices.append(
                RTKeyDevice(
                    intercom=intercom,
                    camera=camera,
                )
            )

        return devices