"""
Base RTKey entity.
"""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
)

from .coordinator import RTKeyCoordinator
from .models import RTKeyDevice


class RTKeyEntity(CoordinatorEntity[RTKeyCoordinator]):

    _attr_has_entity_name = True

    def __init__(self, coordinator, device):

        super().__init__(coordinator)

        self.rt_device = device

    @property
    def intercom(self):
        return self.rt_device.intercom

    @property
    def camera(self):
        return self.rt_device.camera

    @property
    def api(self):
        return self.coordinator.api

    @property
    def available(self):

        if self.camera:
            return self.camera.online

        return self.intercom.online

    @property
    def device_info(self):

        return DeviceInfo(
            identifiers={(DOMAIN, str(self.intercom.id))},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=self.intercom.name,
            suggested_area=self.intercom.address,
            configuration_url="https://key.rt.ru",
        )