"""Binary sensor entities for Ростелеком Ключ integration."""
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RostelecomKeyDataUpdateCoordinator
from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RT-Key binary sensors from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: RostelecomKeyDataUpdateCoordinator = data["coordinator"]

    entities = []

    # Device connectivity online status
    intercoms = coordinator.data.get("intercoms", [])
    for intercom in intercoms:
        entities.append(RostelecomKeyOnlineBinarySensor(coordinator, intercom, "intercom"))

    barriers = coordinator.data.get("barriers", [])
    for barrier in barriers:
        entities.append(RostelecomKeyOnlineBinarySensor(coordinator, barrier, "barrier"))

    async_add_entities(entities)


class RostelecomKeyOnlineBinarySensor(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], BinarySensorEntity):
    """Binary sensor indicating whether device is online."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        device_data: Dict[str, Any],
        dev_type: str,
    ) -> None:
        """Initialize online binary sensor."""
        super().__init__(coordinator)
        self._id = device_data["id"]
        self._dev_type = dev_type
        name = device_data.get("name") or ("Домофон" if dev_type == "intercom" else "Шлагбаум")
        self._attr_name = f"Статус связи ({name})"
        self._attr_unique_id = f"rt_key_online_{dev_type}_{self._id}"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Link sensor to parent device."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": f"{self._dev_type.capitalize()} {self._id}",
            "manufacturer": "Ростелеком Ключ",
        }

    @property
    def is_on(self) -> Optional[bool]:
        """Return True if device is online."""
        key = "intercoms" if self._dev_type == "intercom" else "barriers"
        devices = self.coordinator.data.get(key, [])
        for dev in devices:
            if dev.get("id") == self._id:
                return dev.get("isOnline", True)
        return True
