"""Authentication service for Rostelecom Key (key.rt.ru)."""
import json
from typing import Any, Dict, Optional
import aiohttp

from ..const import API_AUTH_LOGIN_BY_PASSWORD, API_AUTH_REFRESH, API_AUTH_SEND_SMS, API_AUTH_VERIFY_SMS, LOGGER
from .base import BaseService
from .exceptions import RostelecomKeyApiError, RostelecomKeyAuthError, RostelecomKeyNetworkError


class AuthService(BaseService):
    """Handles phone/password login, SMS request, code verification, and JWT token refreshing."""

    def __init__(self, *args, phone: Optional[str] = None, password: Optional[str] = None, **kwargs) -> None:
        """Initialize AuthService with credentials holder."""
        super().__init__(*args, **kwargs)
        self.last_code_id: Optional[str] = None
        self.phone = phone
        self.password = password

    async def async_login_by_password(
        self, phone: Optional[str] = None, password: Optional[str] = None
    ) -> Dict[str, str]:
        """Authenticate using phone number and password via login_by_password endpoint."""
        eff_phone = phone or self.phone
        eff_password = password or self.password

        if not eff_phone or not eff_password:
            raise RostelecomKeyAuthError("Phone number and password are required for login")

        digits = "".join(filter(str.isdigit, eff_phone))
        if digits.startswith("8") and len(digits) == 11:
            digits = "7" + digits[1:]
        clean_phone = digits

        url = API_AUTH_LOGIN_BY_PASSWORD
        payload = {
            "phoneNumber": clean_phone,
            "password": eff_password,
        }

        headers = self._headers()
        headers["Content-Type"] = "text/plain;charset=UTF-8"

        try:
            json_body = json.dumps(payload)
            async with self._session.post(url, data=json_body, headers=headers) as response:
                if response.status in (200, 201):
                    res_json = await response.json()
                    data_obj = res_json.get("data") if isinstance(res_json, dict) and isinstance(res_json.get("data"), dict) else (res_json or {})
                    token = (
                        data_obj.get("accessToken")
                        or data_obj.get("access_token")
                        or data_obj.get("token")
                        or res_json.get("accessToken")
                        or res_json.get("access_token")
                        or res_json.get("token")
                    )
                    if not token:
                        raise RostelecomKeyAuthError("No access token returned in login_by_password response")

                    self.phone = clean_phone
                    self.password = eff_password
                    self._set_token(token, "")
                    LOGGER.info("Successfully logged in with phone %s via password", clean_phone)
                    return {
                        "token": token,
                        "expired_at": data_obj.get("expiredAt", ""),
                    }

                resp_text = await response.text()
                LOGGER.error("Failed password login for %s (Status %s): %s", clean_phone, response.status, resp_text)
                raise RostelecomKeyAuthError(f"Password login failed ({response.status}): {resp_text}")

        except aiohttp.ClientError as err:
            raise RostelecomKeyNetworkError(f"Network error during password login: {err}") from err

    async def async_request_sms(self, phone: str) -> bool:
        """Request SMS verification code for phone number."""
        digits = "".join(filter(str.isdigit, phone))
        if digits.startswith("8") and len(digits) == 11:
            digits = "7" + digits[1:]
        
        clean_phone = digits
        phone_with_plus = f"+{digits}" if digits else phone

        url = API_AUTH_SEND_SMS
        payload = {
            "phoneNumber": clean_phone,
        }

        try:
            async with self._session.post(url, json=payload, headers=self._headers()) as response:
                if response.status in (200, 201, 202, 204):
                    try:
                        res_json = await response.json()
                        data_obj = res_json.get("data") if isinstance(res_json, dict) else {}
                        if isinstance(data_obj, dict) and "codeId" in data_obj:
                            self.last_code_id = str(data_obj["codeId"])
                        elif isinstance(res_json, dict) and "codeId" in res_json:
                            self.last_code_id = str(res_json["codeId"])
                        LOGGER.info("SMS code requested successfully. codeId: %s", self.last_code_id)
                    except Exception as err:
                        LOGGER.debug("Could not parse JSON response for codeId: %s", err)
                    return True
                
                resp_text = await response.text()
                LOGGER.error("Failed to request SMS code (URL: %s, Status: %s, Body: %s)", url, response.status, resp_text)
                
                # Retry with plus format if plain digits failed
                alt_payload = {
                    "phoneNumber": phone_with_plus,
                }
                async with self._session.post(url, json=alt_payload, headers=self._headers()) as alt_resp:
                    if alt_resp.status in (200, 201, 202, 204):
                        try:
                            res_json = await alt_resp.json()
                            data_obj = res_json.get("data") if isinstance(res_json, dict) else {}
                            if isinstance(data_obj, dict) and "codeId" in data_obj:
                                self.last_code_id = str(data_obj["codeId"])
                            elif isinstance(res_json, dict) and "codeId" in res_json:
                                self.last_code_id = str(res_json["codeId"])
                        except Exception:
                            pass
                        LOGGER.info("SMS code requested with + prefix for phone: %s", phone_with_plus)
                        return True
                    alt_text = await alt_resp.text()
                    LOGGER.error("Failed to request SMS code with + prefix (Status: %s, Body: %s)", alt_resp.status, alt_text)

                raise RostelecomKeyApiError(f"SMS request failed with status {response.status}: {resp_text}")
        except aiohttp.ClientError as err:
            raise RostelecomKeyNetworkError(f"Network error requesting SMS code: {err}") from err

    async def async_verify_sms(self, phone: str, code: str, code_id: Optional[str] = None) -> Dict[str, str]:
        """Verify SMS code and obtain access_token & refresh_token."""
        effective_code_id = code_id or self.last_code_id

        url = API_AUTH_VERIFY_SMS
        payload = {
            "code": code,
            "codeId": effective_code_id or "",
        }

        try:
            async with self._session.post(url, json=payload, headers=self._headers()) as response:
                if response.status in (200, 201):
                    data = await response.json()
                    inner_data = data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), dict) else {}
                    token = (
                        data.get("accessToken")
                        or data.get("access_token")
                        or data.get("token")
                        or inner_data.get("accessToken")
                        or inner_data.get("access_token")
                        or inner_data.get("token")
                    )
                    refresh_token = (
                        data.get("refreshToken")
                        or data.get("refresh_token")
                        or inner_data.get("refreshToken")
                        or inner_data.get("refresh_token")
                        or ""
                    )
                    if not token:
                        raise RostelecomKeyAuthError("No access token returned in verify response")
                    
                    self._set_token(token, refresh_token)
                    return {"token": token, "refresh_token": refresh_token}

                resp_text = await response.text()
                raise RostelecomKeyAuthError(f"SMS verification failed ({response.status}): {resp_text}")
        except aiohttp.ClientError as err:
            raise RostelecomKeyNetworkError(f"Network error verifying SMS code: {err}") from err

    async def async_get_current_user(self) -> Dict[str, Any]:
        """Fetch current user profile from household.key.rt.ru using Bearer token."""
        from ..const import API_USERS_CURRENT_URL
        res = await self._async_get(API_USERS_CURRENT_URL)
        if isinstance(res, dict) and isinstance(res.get("data"), dict):
            self._vc_id = res["data"].get("vc_id")
        return res

    async def async_get_vc_id(self) -> Optional[int]:
        """Fetch or return cached vc_id of current user."""
        if getattr(self, "_vc_id", None) is None:
            try:
                await self.async_get_current_user()
            except Exception as err:
                LOGGER.debug("Could not fetch user profile for vc_id: %s", err)
        return getattr(self, "_vc_id", None)

    async def async_refresh_access_token(self) -> str:
        """Refresh access token using refresh_token or password login."""
        if self.refresh_token:
            url = API_AUTH_REFRESH
            payload = {"refresh_token": self.refresh_token}

            try:
                async with self._session.post(url, json=payload, headers=self._headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        new_token = data.get("access_token") or data.get("token")
                        new_refresh = data.get("refresh_token") or self.refresh_token
                        if new_token:
                            self._set_token(new_token, new_refresh)
                            return new_token
            except Exception as err:
                LOGGER.debug("Refresh token endpoint failed: %s", err)

        if getattr(self, "phone", None) and getattr(self, "password", None):
            LOGGER.info("Attempting session renewal via password login for %s", self.phone)
            res = await self.async_login_by_password(self.phone, self.password)
            return res["token"]

        raise RostelecomKeyAuthError("No refresh token or password available to renew access token")
