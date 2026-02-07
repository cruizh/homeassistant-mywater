"""Adds config flow for Blueprint."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_API_KEY,
    CONF_API_TOKEN,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    MyWaterApiClient,
    MyWaterApiClientAuthenticationError,
    MyWaterApiClientCommunicationError,
    MyWaterApiClientError,
)
from .const import DOMAIN, LOGGER

_REPO_URL = "https://github.com/cruizh/homeassistant-mywater"


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    api_username=user_input[CONF_API_KEY],
                    api_password=user_input[CONF_API_TOKEN],
                    user_username=user_input[CONF_USERNAME],
                    user_password=user_input[CONF_PASSWORD],
                )
            except MyWaterApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except MyWaterApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except MyWaterApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_USERNAME])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            description_placeholders={"repo_url": _REPO_URL},
            errors=_errors,
        )

    async def _test_credentials(
        self,
        api_username: str,
        api_password: str,
        user_username: str,
        user_password: str,
    ) -> None:
        """Validate credentials."""
        client = MyWaterApiClient(
            api_username=api_username,
            api_password=api_password,
            user_username=user_username,
            user_password=user_password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
