"""Платформа замков / домофонных дверей для Ростелеком Ключ."""
import logging
import asyncio
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import RTKeyDevice
from .runtime_data import RTKeyRuntimeData

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка замков."""
    runtime_data: RTKeyRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    # coordinator.data содержит список объектов RTKeyDevice
    devices: list[RTKeyDevice] = coordinator.data or []

    entities = [
        RTKeyLock(coordinator, runtime_data.api, device)
        for device in devices
        if device.intercom
    ]
    async_add_entities(entities)


class RTKeyLock(LockEntity):
    """Представление домофонной двери как замка в Home Assistant."""

    def __init__(self, api, door_data: dict) -> None:
        """Инициализация замка."""
        self._api = api
        self._door = door_data
        
        self._door_id = str(door_data.get("id"))
        self._attr_name = door_data.get("name", f"Дверь {self._door_id}")
        self._attr_unique_id = f"rt_key_door_{self._door_id}"
        self._attr_is_locked = True  # Домофон по умолчанию всегда закрыт

    @property
    def device_info(self) -> dict[str, Any]:
        """Привязка сущности к устройству (домофону/адресу) в HA."""
        return {
            "identifiers": {(DOMAIN, self._door_id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком",
            "model": "Домофон Ключ",
        }

    async def async_unlock(self, **kwargs: Any) -> None:
        """Открытие двери (разблокировка)."""
        _LOGGER.debug("Открытие двери %s (%s)", self._attr_name, self._door_id)
        
        try:
            # Вызываем метод открытия из твоего API
            await self._api.open_door(self._door_id)
            
            # Симулируем открытие в интерфейсе на 5 секунд
            self._attr_is_locked = False
            self.async_write_ha_state()

            await asyncio.sleep(5)
            
            # Возвращаем в закрытое состояние
            self._attr_is_locked = True
            self.async_write_ha_state()

        except Exception as err:
            _LOGGER.error("Ошибка при открытии двери %s: %s", self._attr_name, err)
            self._attr_is_locked = True
            self.async_write_ha_state()

    async def async_lock(self, **kwargs: Any) -> None:
        """Запирание (для домофона действие не требуется, так как замок импульсный)."""
        self._attr_is_locked = True
        self.async_write_ha_state()