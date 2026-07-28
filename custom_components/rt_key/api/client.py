"""Main client orchestrator for Rostelecom Key (key.rt.ru) API."""
import uuid
from typing import Any, Dict, List, Optional
import aiohttp

from ..const import API_DEVICES_URL, LOGGER
from .auth import AuthService
from .barriers import BarrierService
from .cameras import CameraService
from .exceptions import RostelecomKeyApiError, RostelecomKeyAuthError
from .guest_codes import GuestCodeService
from .intercoms import IntercomService


class RostelecomKeyApi:
    """Modular Client API combining Auth, Intercoms, Barriers, Cameras, and Guest Codes."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        phone: Optional[str] = None,
        password: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> None:
        """Initialize API client and sub-services."""
        self._session = session
        self.token = token
        self.refresh_token = refresh_token
        self.phone = phone
        self.password = password
        self.device_id = device_id or str(uuid.uuid4())

        # Initialize sub-services
        self.auth = AuthService(
            session=session,
            token_getter=lambda: self.token,
            refresh_token_getter=lambda: self.refresh_token,
            token_setter=self._set_tokens,
            device_id_getter=lambda: self.device_id,
            phone=phone,
            password=password,
        )
        self.intercoms = IntercomService(
            session=session,
            token_getter=lambda: self.token,
            refresh_token_getter=lambda: self.refresh_token,
            token_setter=self._set_tokens,
            device_id_getter=lambda: self.device_id,
        )
        self.barriers = BarrierService(
            session=session,
            token_getter=lambda: self.token,
            refresh_token_getter=lambda: self.refresh_token,
            token_setter=self._set_tokens,
            device_id_getter=lambda: self.device_id,
        )
        self.cameras = CameraService(
            session=session,
            token_getter=lambda: self.token,
            refresh_token_getter=lambda: self.refresh_token,
            token_setter=self._set_tokens,
            device_id_getter=lambda: self.device_id,
        )
        self.guest_codes = GuestCodeService(
            session=session,
            token_getter=lambda: self.token,
            refresh_token_getter=lambda: self.refresh_token,
            token_setter=self._set_tokens,
            device_id_getter=lambda: self.device_id,
        )

        # Connect refresh token callback across services
        self.auth._async_refresh_token_callback = self.auth.async_refresh_access_token
        self.intercoms._async_refresh_token_callback = self.auth.async_refresh_access_token
        self.barriers._async_refresh_token_callback = self.auth.async_refresh_access_token
        self.cameras._async_refresh_token_callback = self.auth.async_refresh_access_token
        self.guest_codes._async_refresh_token_callback = self.auth.async_refresh_access_token

    def _set_tokens(self, token: str, refresh_token: str) -> None:
        """Update access and refresh tokens in memory."""
        self.token = token
        if refresh_token:
            self.refresh_token = refresh_token

    # ------------------------------------------------------------------
    # Backward-compatible facade methods for Home Assistant components
    # ------------------------------------------------------------------

    async def async_login_by_password(
        self, phone: Optional[str] = None, password: Optional[str] = None
    ) -> Dict[str, str]:
        """Authenticate using phone number and password."""
        res = await self.auth.async_login_by_password(phone, password)
        if phone:
            self.phone = phone
        if password:
            self.password = password
        return res

    async def async_request_sms(self, phone: str) -> bool:
        """Request SMS verification code."""
        res = await self.auth.async_request_sms(phone)
        self.phone = "".join(filter(str.isdigit, phone))
        return res

    async def async_verify_sms(self, phone: str, code: str, code_id: Optional[str] = None) -> Dict[str, str]:
        """Verify SMS code."""
        return await self.auth.async_verify_sms(phone, code, code_id)

    async def async_get_current_user(self) -> Dict[str, Any]:
        """Fetch current user profile using saved Bearer token."""
        return await self.auth.async_get_current_user()

    async def async_get_vc_id(self) -> Optional[int]:
        """Fetch vc_id of current user for video cloud integration."""
        return await self.auth.async_get_vc_id()

    async def async_refresh_access_token(self) -> str:
        """Refresh JWT access token."""
        return await self.auth.async_refresh_access_token()

    async def async_get_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch devices by querying the intercoms endpoint."""
        intercoms = await self.intercoms.async_get_intercoms()
        return {
            "intercoms": intercoms,
            "barriers": [],
            "cameras": [],
            "guest_codes": [],
        }

    async def async_open_intercom(self, intercom_id: str) -> bool:
        """Open intercom door."""
        return await self.intercoms.async_open_intercom(intercom_id)

    async def async_open_barrier(self, barrier_id: str) -> bool:
        """Open barrier gate."""
        return await self.barriers.async_open_barrier(barrier_id)

    async def async_create_guest_code(
        self,
        intercom_id: str,
        duration_hours: int = 24,
        max_uses: int = 1,
        description: str = "HA Guest Code",
    ) -> Dict[str, Any]:
        """Generate guest PIN code."""
        return await self.guest_codes.async_create_guest_code(
            intercom_id=intercom_id,
            duration_hours=duration_hours,
            max_uses=max_uses,
            description=description,
        )

    async def async_get_camera_snapshot(self, camera_id: str) -> bytes:
        """Fetch camera JPEG snapshot bytes."""
        return await self.cameras.async_get_camera_snapshot(camera_id)

    async def async_get_camera_stream_url(self, camera_id: str) -> str:
        """Fetch RTSP/HLS stream URL."""
        return await self.cameras.async_get_camera_stream_url(camera_id)

    async def async_get_camera_archive_intervals(self, camera_id: str) -> List[Dict[str, Any]]:
        """Fetch camera video archive intervals."""
        return await self.cameras.async_get_camera_archive_intervals(camera_id)

    async def async_get_tags(self) -> List[Dict[str, Any]]:
        """Fetch list of RFID key tags from keyapis.key.rt.ru."""
        from ..const import API_TAGS_LIST_URL
        try:
            data = await self.intercoms._async_get(API_TAGS_LIST_URL)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return (
                    data.get("data")
                    or data.get("tags")
                    or data.get("items")
                    or []
                )
        except Exception as err:
            LOGGER.warning("Could not fetch RFID tags list: %s", err)
        return []
