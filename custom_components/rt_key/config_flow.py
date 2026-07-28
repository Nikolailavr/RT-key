"""Config flow for Ростелеком Ключ (RT-Key) integration."""
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RostelecomKeyApi, RostelecomKeyAuthError, RostelecomKeyApiError
from .const import (
    DOMAIN,
    LOGGER,
    CONF_PHONE,
    CONF_PASSWORD,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE, default="+7"): str,
    }
)

STEP_TOKEN_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_REFRESH_TOKEN, default=""): str,
        vol.Optional(CONF_PHONE, default=""): str,
    }
)


@config_entries.HANDLERS.register(DOMAIN)
class RostelecomKeyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ростелеком Ключ."""

    domain = DOMAIN
    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._phone: Optional[str] = None
        self._api: Optional[RostelecomKeyApi] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle initial step (Choose Password, SMS, or direct Token)."""
        if user_input is not None:
            method = user_input.get("auth_method")
            if method == "password":
                return await self.async_step_password()
            elif method == "token":
                return await self.async_step_token()
            return await self.async_step_phone()

        schema = vol.Schema(
            {
                vol.Required("auth_method", default="password"): vol.In(
                    {
                        "password": "Вход по номеру телефона и паролю",
                        "sms": "Вход по номеру телефона (SMS)",
                        "token": "Ввод готового токена (Bearer Token)",
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema
        )

    async def async_step_password(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step to enter phone number and password."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            phone = user_input.get(CONF_PHONE, "").strip()
            password = user_input.get(CONF_PASSWORD, "").strip()
            session = async_get_clientsession(self.hass)
            api = RostelecomKeyApi(session=session)

            try:
                tokens = await api.async_login_by_password(phone, password)
                token = tokens.get("token")
                if token:
                    clean_phone = "".join(filter(str.isdigit, phone))
                    if clean_phone.startswith("8") and len(clean_phone) == 11:
                        clean_phone = "7" + clean_phone[1:]

                    await self.async_set_unique_id(clean_phone or phone)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Ростелеком Ключ ({phone})",
                        data={
                            CONF_PHONE: phone,
                            CONF_PASSWORD: password,
                            CONF_TOKEN: token,
                            CONF_REFRESH_TOKEN: "",
                        },
                    )
                errors["base"] = "invalid_auth"
            except RostelecomKeyAuthError:
                errors["base"] = "invalid_auth"
            except RostelecomKeyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error during password login")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_PHONE, default="+7"): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="password", data_schema=schema, errors=errors
        )

    async def async_step_phone(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step to enter phone number for SMS auth."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            self._phone = user_input.get(CONF_PHONE)
            session = async_get_clientsession(self.hass)
            self._api = RostelecomKeyApi(session=session)

            try:
                await self._api.async_request_sms(self._phone)
                return await self.async_step_sms()
            except RostelecomKeyAuthError:
                errors["base"] = "invalid_phone"
            except RostelecomKeyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error requesting SMS")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_PHONE, default="+7"): str,
            }
        )

        return self.async_show_form(
            step_id="phone", data_schema=schema, errors=errors
        )

    async def async_step_sms(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step to enter SMS confirmation code."""
        errors: Dict[str, str] = {}

        if user_input is not None and self._phone and self._api:
            code = user_input.get("code", "").strip()
            try:
                tokens = await self._api.async_verify_sms(self._phone, code)
                await self.async_set_unique_id(self._phone)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Ростелеком Ключ ({self._phone})",
                    data={
                        CONF_PHONE: self._phone,
                        CONF_TOKEN: tokens["token"],
                        CONF_REFRESH_TOKEN: tokens["refresh_token"],
                    },
                )
            except RostelecomKeyAuthError:
                errors["base"] = "invalid_code"
            except RostelecomKeyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error verifying SMS code")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required("code"): str,
            }
        )

        return self.async_show_form(
            step_id="sms",
            data_schema=schema,
            errors=errors,
            description_placeholders={"phone": self._phone or ""},
        )

    async def async_step_token(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step for entering direct token."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            refresh_token = user_input.get(CONF_REFRESH_TOKEN, "").strip()
            phone = user_input.get(CONF_PHONE, "").strip() or "Manual Token"

            session = async_get_clientsession(self.hass)
            api = RostelecomKeyApi(session=session, token=token)

            try:
                # Test API connectivity using current user endpoint with Bearer token
                try:
                    await api.async_get_current_user()
                except Exception:
                    await api.async_get_devices()

                await self.async_set_unique_id(f"token_{token[:12]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Ростелеком Ключ ({phone})",
                    data={
                        CONF_PHONE: phone,
                        CONF_TOKEN: token,
                        CONF_REFRESH_TOKEN: refresh_token,
                    },
                )
            except RostelecomKeyAuthError:
                errors["base"] = "invalid_auth"
            except RostelecomKeyApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="token", data_schema=STEP_TOKEN_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow for RT-Key."""
        return RostelecomKeyOptionsFlowHandler(config_entry)


class RostelecomKeyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for RT-Key."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage option settings."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
