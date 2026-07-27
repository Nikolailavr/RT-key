"""
Button platform.
"""

from __future__ import annotations

from homeassistant.components.button import (
    ButtonEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import RTKeyEntity
from .runtime_data import RTKeyRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup buttons."""

    runtime: RTKeyRuntimeData = entry.runtime_data

    entities = [
        RTKeyDoorButton(
            runtime,
            device,
        )
        for device in runtime.coordinator.data
    ]

    async_add_entities(entities)


class RTKeyDoorButton(
    RTKeyEntity,
    ButtonEntity,
):
    """Open door button."""

    _attr_icon = "mdi:door-open"

    _attr_translation_key = "open_door"

    def __init__(
        self,
        runtime: RTKeyRuntimeData,
        device,
    ) -> None:

        super().__init__(
            runtime.coordinator,
            device,
        )

        self.runtime = runtime

        self._attr_unique_id = (
            f"{DOMAIN}_{device.unique_id}_open"
        )

        self._attr_name = "Открыть дверь"

    async def async_press(self) -> None:
        """Open door."""

        await self.runtime.api.open_door(
            self.device.intercom.id,
        )