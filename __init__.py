"""RTKey integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import RTKeyCoordinator
from .runtime_data import RTKeyRuntimeData

# Указываем загружаемые платформы
PLATFORMS: list[Platform] = [
    Platform.LOCK,
    # Platform.CAMERA,  # добавим позже для видеопотоков
]


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
    """Настройка интеграции из ConfigEntry."""
    
    # Инициализируем координатор
    coordinator = RTKeyCoordinator(
        hass,
        entry.data["access_token"],
    )

    # Делаем первый запрос данных
    await coordinator.async_config_entry_first_refresh()

    # Сохраняем типиизированные данные в runtime_data
    entry.runtime_data = RTKeyRuntimeData(
        api=coordinator.api,
        coordinator=coordinator,
    )

    # Загружаем платформы (lock, etc.)
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