"""Sensor entities for Ростелеком Ключ integration."""
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
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
    """Set up RT-Key sensors from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: RostelecomKeyDataUpdateCoordinator = data["coordinator"]

    entities = []

    # Guest Code count sensor
    # entities.append(RostelecomKeyActiveGuestCodesSensor(coordinator, entry.entry_id))

    # Last opening log sensor per intercom
    # intercoms = coordinator.data.get("intercoms", [])
    # for intercom in intercoms:
    #     entities.append(RostelecomKeyLastOpenedSensor(coordinator, intercom))

    async_add_entities(entities)


class RostelecomKeyActiveGuestCodesSensor(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], SensorEntity):
    """Sensor tracking active guest PIN codes count."""

    _attr_icon = "mdi:key-wireless"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize active guest code sensor."""
        super().__init__(coordinator)
        self._attr_name = "Ростелеком Ключ: Активные Гостевые Коды"
        self._attr_unique_id = f"rt_key_active_guest_codes_{entry_id}"

    @property
    def native_value(self) -> int:
        """Return total active guest codes count."""
        codes = self.coordinator.data.get("guest_codes", [])
        return len(codes)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return details of active guest codes."""
        codes = self.coordinator.data.get("guest_codes", [])
        return {
            "codes_list": codes,
            "total_count": len(codes),
        }


class RostelecomKeyLastOpenedSensor(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], SensorEntity):
    """Sensor showing last opened timestamp for an intercom door."""

    _attr_icon = "mdi:history"

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        intercom_data: Dict[str, Any],
    ) -> None:
        """Initialize last opened sensor."""
        super().__init__(coordinator)
        self._id = intercom_data["id"]
        self._attr_name = f"Последнее открытие ({intercom_data.get('name', 'Домофон')})"
        self._attr_unique_id = f"rt_key_last_opened_{self._id}"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Link sensor to intercom device."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": f"Домофон {self._id}",
            "manufacturer": "Ростелеком Ключ",
        }

    @property
    def native_value(self) -> Optional[str]:
        """Return timestamp or status of last door opening."""
        intercoms = self.coordinator.data.get("intercoms", [])
        for dev in intercoms:
            if dev.get("id") == self._id:
                return dev.get("lastOpenedAt") or dev.get("last_opened") or "Не открывалось"
        return "Неизвестно"
