"""RTKey integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .coordinator import RTKeyCoordinator
from .runtime_data import RTKeyRuntimeData

PLATFORMS = (
    "camera",
    "image",
    "button",
    "sensor",
)


entry.runtime_data = RTKeyRuntimeData(
    api=coordinator.api,
    coordinator=coordinator,
)

async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up integration."""

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    coordinator = RTKeyCoordinator(
        hass,
        entry.data["access_token"],
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload config entry."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )