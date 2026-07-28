"""DataUpdateCoordinator for Ростелеком Ключ."""
from datetime import timedelta
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RostelecomKeyApi, RostelecomKeyApiError, RostelecomKeyAuthError
from .const import DOMAIN, LOGGER, DEFAULT_SCAN_INTERVAL

class RostelecomKeyDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching Rostelecom Key data periodically."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: RostelecomKeyApi,
        update_interval_sec: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize coordinator."""
        self.api = api
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_sec),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from key.rt.ru API."""
        try:
            data = await self.api.async_get_devices()
            LOGGER.debug("Rostelecom Key update payload: %s", data)
            return data
        except RostelecomKeyAuthError as err:
            LOGGER.error("Authentication error during RT-Key update: %s", err)
            raise UpdateFailed(f"Auth error: {err}") from err
        except RostelecomKeyApiError as err:
            LOGGER.warning("API error updating RT-Key data: %s", err)
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            LOGGER.exception("Unexpected exception updating RT-Key data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
