import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN
from .const import CONF_TOKEN


class RTKeyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            return self.async_create_entry(
                title="Ростелеком Ключ",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOKEN): str,
                }
            ),
        )