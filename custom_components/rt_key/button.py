"""Button entities for Ростелеком Ключ integration."""
from typing import Any, Dict

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RostelecomKeyDataUpdateCoordinator
from .const import DOMAIN, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RT-Key buttons from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: RostelecomKeyDataUpdateCoordinator = data["coordinator"]
    api = data["api"]

    entities = []

    # Quick Open Door Buttons
    intercoms = coordinator.data.get("intercoms", [])
    for intercom in intercoms:
        entities.append(RostelecomKeyOpenDoorButton(coordinator, api, intercom))

    # Quick Open Barrier Buttons
    barriers = coordinator.data.get("barriers", [])
    for barrier in barriers:
        entities.append(RostelecomKeyOpenBarrierButton(coordinator, api, barrier))

    async_add_entities(entities)


class RostelecomKeyOpenDoorButton(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], ButtonEntity):
    """Button entity to trigger opening intercom door."""

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        intercom_data: Dict[str, Any],
    ) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)
        self.api = api
        self._id = intercom_data["id"]
        name = (
            intercom_data.get("name_by_user")
            or intercom_data.get("name_by_company")
            or intercom_data.get("name")
            or intercom_data.get("description")
            or "Домофон"
        )
        self._attr_name = f"Открыть дверь ({name})"
        self._attr_unique_id = f"rt_key_btn_open_door_{self._id}"
        self._attr_icon = "mdi:door-open"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Link button to parent intercom device."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
        }

    async def async_press(self) -> None:
        """Handle button press to open door."""
        LOGGER.info("Opening door via button press for device %s", self._id)
        await self.api.async_open_intercom(self._id)


class RostelecomKeyOpenBarrierButton(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], ButtonEntity):
    """Button entity to trigger opening barrier gate."""

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        barrier_data: Dict[str, Any],
    ) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)
        self.api = api
        self._id = barrier_data["id"]
        name = (
            barrier_data.get("name_by_user")
            or barrier_data.get("name_by_company")
            or barrier_data.get("name")
            or barrier_data.get("description")
            or "Шлагбаум"
        )
        self._attr_name = f"Открыть шлагбаум ({name})"
        self._attr_unique_id = f"rt_key_btn_open_barrier_{self._id}"
        self._attr_icon = "mdi:gate"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Link button to parent barrier device."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
        }

    async def async_press(self) -> None:
        """Handle button press to open barrier."""
        LOGGER.info("Opening barrier via button press for device %s", self._id)
        await self.api.async_open_barrier(self._id)
