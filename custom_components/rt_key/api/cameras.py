"""CCTV Camera service for Rostelecom Key."""
from typing import Any, Dict, List
from urllib.parse import urlparse
import time
import aiohttp

from ..const import API_CAMERAS_URL, API_CAMERA_VIDEO_DATA_LIST_URL, API_VC_CAMERAS_URL, LOGGER
from .base import BaseService
from .exceptions import RostelecomKeyApiError


class CameraService(BaseService):
    """Handles fetching camera lists, video streams, archive intervals, and JPEG snapshots."""

    async def async_get_camera_video_data_list(self) -> List[Dict[str, Any]]:
        """Fetch camera video data list containing tokens, streamer URLs, and screenshot templates."""
        url = API_CAMERA_VIDEO_DATA_LIST_URL
        try:
            res = await self._async_get(url)
            if isinstance(res, dict):
                data = res.get("data")
                if isinstance(data, list):
                    return data
            elif isinstance(res, list):
                return res
        except Exception as err:
            LOGGER.warning("Error fetching camera video data list from %s: %s", url, err)
        return []

    async def async_get_cameras(self) -> List[Dict[str, Any]]:
        """Fetch list of user CCTV and intercom cameras."""
        video_items = await self.async_get_camera_video_data_list()
        cameras = []
        for item in video_items:
            uid = item.get("uid") or item.get("id")
            if not uid:
                continue
            title = item.get("title") or item.get("name") or f"Камера {uid}"
            cat = item.get("category") or {}
            cat_type = cat.get("type") if isinstance(cat, dict) else str(cat)

            cameras.append({
                "id": uid,
                "camera_id": uid,
                "name": title,
                "title": title,
                "category_type": cat_type,
                "ip": item.get("ip"),
                "streamer_url": item.get("streamerUrl"),
                "streamer_token": item.get("streamerToken"),
                "screenshot_token": item.get("screenshotToken"),
                "screenshot_url_template": item.get("screenshotUrlTemplate"),
                "raw_data": item,
            })

        if cameras:
            return cameras

        # Fallback to primary URL /devices/cameras if list was empty
        try:
            data = await self._async_get(API_CAMERAS_URL)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                res = (
                    data.get("data")
                    or data.get("devices")
                    or data.get("cameras")
                    or data.get("items")
                )
                if isinstance(res, list):
                    return res
        except Exception as err:
            LOGGER.debug("Could not fetch cameras from %s: %s", API_CAMERAS_URL, err)

        return []

    async def async_get_camera_archive_intervals(self, camera_id: str) -> List[Any]:
        """Fetch video archive intervals from Video Cloud (vc.key.rt.ru/api/v1/cameras/{id}/archive_intervals)."""
        url = f"{API_CAMERAS_URL}/{camera_id}/archive_intervals"
        try:
            res = await self._async_get(url)
            if isinstance(res, list):
                return res
            if isinstance(res, dict):
                data = res.get("data")
                if isinstance(data, dict):
                    items = data.get("items") or data.get("intervals")
                    if isinstance(items, list):
                        return items
                elif isinstance(data, list):
                    return data

                items = res.get("items") or res.get("intervals")
                if isinstance(items, list):
                    return items
        except Exception as err:
            LOGGER.warning("Failed to fetch archive intervals for camera %s from %s: %s", camera_id, url, err)
        return []

    async def async_get_camera_stream_url(self, camera_id: str) -> str:
        """Fetch live stream URL for camera using camera_video_data list and streamerToken."""
        items = await self.async_get_camera_video_data_list()
        target = None
        for item in items:
            if item.get("uid") == camera_id or item.get("id") == camera_id:
                target = item
                break

        if not target and items:
            target = items[0]

        if target:
            streamer_token = target.get("streamerToken")
            streamer_url = target.get("streamerUrl") or "https://live-vdk4.camera.rt.ru"
            target_uid = target.get("uid") or camera_id

            if streamer_token:
                parsed = urlparse(streamer_url)
                host = parsed.netloc or "live-vdk4.camera.rt.ru"
                return f"https://{host}/stream/{target_uid}/live.mp4?mp4-fragment-length=0.5&mp4-use-speed=0&mp4-afiller=1&token={streamer_token}"

        return f"https://live-vdk4.camera.rt.ru/stream/{camera_id}/live.mp4?mp4-fragment-length=0.5&mp4-use-speed=0&mp4-afiller=1"

    async def async_get_camera_snapshot(self, camera_id: str) -> bytes:
        """Fetch camera JPEG snapshot using screenshotUrlTemplate and screenshotToken."""
        items = await self.async_get_camera_video_data_list()
        target = None
        for item in items:
            if item.get("uid") == camera_id or item.get("id") == camera_id:
                target = item
                break

        if not target and items:
            target = items[0]

        if target:
            template = target.get("screenshotUrlTemplate")
            token = target.get("screenshotToken") or target.get("userToken")
            if template and token:
                ts = int(time.time())
                snap_url = (
                    template.replace("{size}", "large")
                    .replace("{timestamp}", str(ts))
                    .replace("{cdn_token}", token)
                )
                try:
                    async with self._session.get(snap_url, headers=self._headers()) as response:
                        if response.status == 200:
                            return await response.read()
                except Exception as err:
                    LOGGER.debug("Snapshot fetch from template failed: %s", err)

        # Fallback to direct snapshot URLs
        urls = [
            f"{API_CAMERAS_URL}/{camera_id}/snapshot",
            f"{API_VC_CAMERAS_URL}/{camera_id}/snapshot",
        ]
        for url in urls:
            try:
                async with self._session.get(url, headers=self._headers()) as response:
                    if response.status == 200:
                        return await response.read()
            except Exception:
                pass

        raise RostelecomKeyApiError(f"Failed to fetch camera snapshot for {camera_id}")
