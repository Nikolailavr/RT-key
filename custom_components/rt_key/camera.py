"""Support for Ростелеком Ключ camera streaming and snapshots."""
import logging
import time
from typing import Any, Dict, Optional

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RostelecomKeyDataUpdateCoordinator
from .const import DOMAIN, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RT-Key cameras from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: RostelecomKeyDataUpdateCoordinator = data["coordinator"]
    api = data["api"]

    entities = []
    seen_camera_ids = set()

    # Intercom built-in cameras
    intercoms = coordinator.data.get("intercoms", [])
    for intercom in intercoms:
        if intercom.get("cameraSnapshotUrl") or intercom.get("has_camera", True):
            cam_id = intercom.get("camera_id") or intercom.get("id")
            if cam_id:
                seen_camera_ids.add(str(cam_id))
            entities.append(RostelecomKeyIntercomCamera(coordinator, api, intercom))

    # Dedicated CCTV cameras from camera_video_data list
    cameras = coordinator.data.get("cameras", [])
    for camera in cameras:
        cam_id = camera.get("camera_id") or camera.get("id")
        if cam_id and str(cam_id) in seen_camera_ids:
            continue
        if cam_id:
            seen_camera_ids.add(str(cam_id))
        entities.append(RostelecomKeyCctvCamera(coordinator, api, camera))

    async_add_entities(entities)


class RostelecomKeyIntercomCamera(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], Camera):
    """Camera entity for Intercom built-in camera."""

    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        intercom_data: Dict[str, Any],
    ) -> None:
        """Initialize intercom camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self.api = api
        self._id = intercom_data["id"]
        self._camera_id = intercom_data.get("camera_id") or intercom_data["id"]
        self._stream_url: Optional[str] = None
        self._stream_url_updated_at: float = 0
        name = (
            intercom_data.get("name_by_user")
            or intercom_data.get("name_by_company")
            or intercom_data.get("name")
            or intercom_data.get("description")
            or "Домофон"
        )
        self._attr_name = f"Камера ({name})"
        self._attr_unique_id = f"rt_key_camera_intercom_{self._id}"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device info linked to parent intercom."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant, pre-fetch stream URL for attributes."""
        await super().async_added_to_hass()
        try:
            self._stream_url = await self.api.async_get_camera_stream_url(self._camera_id)
            self._stream_url_updated_at = time.time()
            self.async_write_ha_state()
        except Exception as err:
            LOGGER.debug("Could not pre-fetch stream URL for intercom camera %s: %s", self._camera_id, err)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinator and invalidate old stream URL daily."""
        now = time.time()
        if now - self._stream_url_updated_at >= 43200:  # 12 hours
            self._stream_url = None
        super()._handle_coordinator_update()

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Return JPEG snapshot from intercom camera."""
        try:
            return await self.api.async_get_camera_snapshot(self._camera_id)
        except Exception as err:
            LOGGER.warning("Failed to fetch image for intercom camera %s: %s", self._camera_id, err)
            return None

    async def stream_source(self) -> Optional[str]:
        """Return RTSP/HLS/HTTPS stream source URL for intercom video."""
        now = time.time()
        if self._stream_url and (now - self._stream_url_updated_at < 43200):
            return self._stream_url
        try:
            url = await self.api.async_get_camera_stream_url(self._camera_id)
            if url:
                self._stream_url = url
                self._stream_url_updated_at = now
            return url
        except Exception as err:
            LOGGER.warning("Failed to fetch stream URL for intercom camera %s: %s", self._camera_id, err)
            return self._stream_url

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes for camera."""
        attrs: Dict[str, Any] = {
            "camera_id": self._camera_id,
        }
        if self._stream_url:
            attrs["stream_url"] = self._stream_url
            attrs["live_stream_url"] = self._stream_url
        return attrs


class RostelecomKeyCctvCamera(CoordinatorEntity[RostelecomKeyDataUpdateCoordinator], Camera):
    """Camera entity for CCTV video surveillance."""

    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: RostelecomKeyDataUpdateCoordinator,
        api: Any,
        camera_data: Dict[str, Any],
    ) -> None:
        """Initialize CCTV camera entity."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self.api = api
        self._id = camera_data["id"]
        self._camera_id = camera_data.get("camera_id") or camera_data["id"]
        self._stream_url: Optional[str] = None
        self._stream_url_updated_at: float = 0
        name = (
            camera_data.get("name_by_user")
            or camera_data.get("name_by_company")
            or camera_data.get("name")
            or camera_data.get("description")
            or f"Видеокамера {self._id}"
        )
        self._attr_name = name
        self._attr_unique_id = f"rt_key_cctv_{self._id}"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, f"cctv_{self._id}")},
            "name": self._attr_name,
            "manufacturer": "Ростелеком Ключ",
            "model": "Видеонаблюдение RT",
            "suggested_area": "Двор",
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant, pre-fetch stream URL for attributes."""
        await super().async_added_to_hass()
        try:
            self._stream_url = await self.api.async_get_camera_stream_url(self._camera_id)
            self._stream_url_updated_at = time.time()
            self.async_write_ha_state()
        except Exception as err:
            LOGGER.debug("Could not pre-fetch stream URL for camera %s: %s", self._camera_id, err)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinator and invalidate old stream URL daily."""
        now = time.time()
        if now - self._stream_url_updated_at >= 43200:  # 12 hours
            self._stream_url = None
        super()._handle_coordinator_update()

    async def async_camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        """Fetch snapshot image."""
        try:
            return await self.api.async_get_camera_snapshot(self._camera_id)
        except Exception as err:
            LOGGER.warning("Failed to fetch snapshot for camera %s: %s", self._camera_id, err)
            return None

    async def stream_source(self) -> Optional[str]:
        """Fetch stream source URL."""
        now = time.time()
        if self._stream_url and (now - self._stream_url_updated_at < 43200):
            return self._stream_url
        try:
            url = await self.api.async_get_camera_stream_url(self._camera_id)
            if url:
                self._stream_url = url
                self._stream_url_updated_at = now
            return url
        except Exception as err:
            LOGGER.warning("Failed to fetch stream URL for camera %s: %s", self._camera_id, err)
            return self._stream_url

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes for camera."""
        attrs: Dict[str, Any] = {
            "camera_id": self._camera_id,
        }
        if self._stream_url:
            attrs["stream_url"] = self._stream_url
            attrs["live_stream_url"] = self._stream_url
        return attrs
