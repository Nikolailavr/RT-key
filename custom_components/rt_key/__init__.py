"""The Ростелеком Ключ integration."""
import asyncio
from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RostelecomKeyApi
from .coordinator import RostelecomKeyDataUpdateCoordinator
from .const import (
    DOMAIN,
    LOGGER,
    PLATFORMS,
    CONF_PHONE,
    CONF_PASSWORD,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    SERVICE_CREATE_GUEST_CODE,
    SERVICE_OPEN_DOOR,
    SERVICE_OPEN_BARRIER,
    ATTR_DURATION_HOURS,
    ATTR_MAX_USES,
    ATTR_DESCRIPTION,
    CONF_DEVICE_ID,
)

CREATE_GUEST_CODE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Optional(ATTR_DURATION_HOURS, default=24): cv.positive_int,
        vol.Optional(ATTR_MAX_USES, default=1): cv.positive_int,
        vol.Optional(ATTR_DESCRIPTION, default="HA Guest PIN"): cv.string,
    }
)

OPEN_DOOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ростелеком Ключ from a config entry."""
    session = async_get_clientsession(hass)

    phone = entry.data.get(CONF_PHONE)
    password = entry.data.get(CONF_PASSWORD)
    token = entry.data.get(CONF_TOKEN)
    refresh_token = entry.data.get(CONF_REFRESH_TOKEN)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    api = RostelecomKeyApi(
        session=session,
        token=token,
        refresh_token=refresh_token,
        phone=phone,
        password=password,
    )

    coordinator = RostelecomKeyDataUpdateCoordinator(
        hass, api=api, update_interval_sec=scan_interval
    )

    # Initial data refresh
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    # Setup platforms (lock, camera, sensor, binary_sensor, button)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register Custom Services
    async def handle_create_guest_code(call: ServiceCall) -> None:
        """Handle service call to create guest code."""
        device_id = call.data[CONF_DEVICE_ID]
        duration = call.data[ATTR_DURATION_HOURS]
        max_uses = call.data[ATTR_MAX_USES]
        description = call.data[ATTR_DESCRIPTION]

        result = await api.async_create_guest_code(
            intercom_id=device_id,
            duration_hours=duration,
            max_uses=max_uses,
            description=description,
        )
        LOGGER.info("Guest code generated successfully for %s: %s", device_id, result)
        # Fire event so automations can send code via Telegram / SMS
        hass.bus.async_fire(
            f"{DOMAIN}_guest_code_created",
            {
                "device_id": device_id,
                "code": result.get("code"),
                "expires_at": result.get("expires_at"),
                "description": description,
            },
        )

    async def handle_open_door(call: ServiceCall) -> None:
        """Handle open door service call."""
        device_id = call.data[CONF_DEVICE_ID]
        await api.async_open_intercom(device_id)

    async def handle_open_barrier(call: ServiceCall) -> None:
        """Handle open barrier service call."""
        device_id = call.data[CONF_DEVICE_ID]
        await api.async_open_barrier(device_id)

    if not hass.services.has_service(DOMAIN, SERVICE_CREATE_GUEST_CODE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CREATE_GUEST_CODE,
            handle_create_guest_code,
            schema=CREATE_GUEST_CODE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_OPEN_DOOR):
        hass.services.async_register(
            DOMAIN, SERVICE_OPEN_DOOR, handle_open_door, schema=OPEN_DOOR_SCHEMA
        )

    if not hass.services.has_service(DOMAIN, SERVICE_OPEN_BARRIER):
        hass.services.async_register(
            DOMAIN, SERVICE_OPEN_BARRIER, handle_open_barrier, schema=OPEN_DOOR_SCHEMA
        )

    # Add update listener for option flow updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
