"""
Config flow for RTKey.
"""

from __future__ import annotations

import voluptuous as vol

from aiohttp import ClientSession

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RTKeyApi, RTKeySession
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_PHONE,
    CONF_CODE,
    CONF_CODE_ID,
    DEFAULT_NAME,
    DOMAIN,
)
from .exceptions import (
    RTKeyApiError,
    RTKeyAuthError,
)


class RTKeyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle RTKey config flow."""

    VERSION = 1

    _phone: str | None = None
    _code_id: str | None = None
    _session: RTKeySession | None = None
    _api: RTKeyApi | None = None

    async def async_step_user(self, user_input=None):
        """Step 1: phone."""

        errors = {}

        if user_input is not None:
            self._phone = user_input[CONF_PHONE]
            self._session = RTKeySession()
            client: ClientSession = async_get_clientsession(self.hass)
            self._api = RTKeyApi(
                client,
                self._session,
            )

            try:
                self._code_id = await self._api.auth.send_code(
                    self._phone,
                )
                return await self.async_step_code()
            except RTKeyApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PHONE): str,
                }
            ),
            errors=errors,
        )

    async def async_step_code(self, user_input=None):
        """Step 2: sms code."""

        errors = {}
        if user_input is not None:
            try:
                await self._api.auth.login(
                    user_input[CONF_CODE],
                    self._code_id,
                )
                user = await self._api.auth.current_user()
                await self.async_set_unique_id(
                    str(user["data"]["id"])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_PHONE: self._phone,
                        CONF_ACCESS_TOKEN: self._session.access_token,
                        CONF_DEVICE_ID: self._session.device_id,
                    },
                )
            except RTKeyAuthError:
                errors["base"] = "invalid_auth"
            except RTKeyApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="code",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CODE): str,
                }
            ),
            errors=errors,
        )