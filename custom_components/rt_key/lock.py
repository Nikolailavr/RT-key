"""Support for Ростелеком Ключ locks (Intercoms and Barriers)."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.lock import LockEntity, LockEntityFeature
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
    """Set up RT-Key locks from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: RostelecomKeyDataUpdateCoordinator = data["coordinator"]
    api = data["api"]

    entities = []

    # Intercom doors
    intercoms = coordinator.data.get("intercoms", [])
    for intercom in intercoms:
        entities.append(RostelecomKeyIntercomLock(coordinator, api, intercom))

    # Barrier gates
    barriers = coordinator.data.get("barriers", [])
    for barrier in barriers:
        entities.append(RostelecomKeyBarrierLock(coordinator, api, barrier))

    async_add_entities(entities)


class RostelecomKeyIntercomLock(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], LockEntity):
    """Representation of a Rostelecom Key Intercom door lock."""

    _attr_supported_features = LockEntityFeature.OPEN

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        intercom_data: Dict[str, Any],
    ) -> None:
        """Initialize intercom lock entity."""
        super().__init__(coordinator)
        self.api = api
        self._id = intercom_data["id"]
        self._attr_name = (
            intercom_data.get("name_by_user")
            or intercom_data.get("name_by_company")
            or intercom_data.get("name")
            or intercom_data.get("description")
            or f"Домофон {self._id}"
        )
        self._attr_unique_id = f"rt_key_intercom_{self._id}"
        self._attr_is_locked = True
        self._address = intercom_data.get("address", "")
        self._flat = intercom_data.get("flat", "")

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information for HA device registry."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
            "model": "Умный Домофон",
            "suggested_area": f"Квартира {self._flat}" if self._flat else "Подъезд",
        }

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return device attributes."""
        return {
            "device_id": self._id,
            "address": self._address,
            "flat": self._flat,
            "integration": "rt_key",
        }

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock/open intercom door."""
        LOGGER.info("Unlocking/opening intercom door %s", self._id)
        await self.api.async_open_intercom(self._id)
        self._attr_is_locked = False
        self.async_write_ha_state()

        # Automatically restore locked state after 5 seconds
        self.hass.loop.call_later(5.0, self._restore_locked_state)

    async def async_open(self, **kwargs: Any) -> None:
        """Open intercom door."""
        await self.async_unlock(**kwargs)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock intercom door."""
        self._attr_is_locked = True
        self.async_write_ha_state()

    def _restore_locked_state(self) -> None:
        """Set lock state back to locked after door timer."""
        self._attr_is_locked = True
        self.async_write_ha_state()


class RostelecomKeyBarrierLock(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], LockEntity):
    """Representation of a Rostelecom Key Barrier gate lock."""

    _attr_supported_features = LockEntityFeature.OPEN

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        barrier_data: Dict[str, Any],
    ) -> None:
        """Initialize barrier lock entity."""
        super().__init__(coordinator)
        self.api = api
        self._id = barrier_data["id"]
        self._attr_name = (
            barrier_data.get("name_by_user")
            or barrier_data.get("name_by_company")
            or barrier_data.get("name")
            or barrier_data.get("description")
            or f"Шлагбаум {self._id}"
        )
        self._attr_unique_id = f"rt_key_barrier_{self._id}"
        self._attr_is_locked = True
        self._address = barrier_data.get("address", "")

    @property
    def device_info(self) -> Dict[str, Any]:
        """Device info for HA registry."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
            "model": "Умный Шлагбаум / Ворота",
            "suggested_area": "Двор",
        }

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return barrier attributes."""
        return {
            "device_id": self._id,
            "address": self._address,
            "type": "barrier",
        }

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock/open barrier gate."""
        LOGGER.info("Unlocking/opening barrier gate %s", self._id)
        await self.api.async_open_barrier(self._id)
        self._attr_is_locked = False
        self.async_write_ha_state()

        # Auto relock after 15 seconds
        self.hass.loop.call_later(15.0, self._restore_locked_state)

    async def async_open(self, **kwargs: Any) -> None:
        """Open barrier."""
        await self.async_unlock(**kwargs)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock barrier."""
        self._attr_is_locked = True
        self.async_write_ha_state()

    def _restore_locked_state(self) -> None:
        """Reset lock state."""
        self._attr_is_locked = True
        self.async_write_ha_state()
