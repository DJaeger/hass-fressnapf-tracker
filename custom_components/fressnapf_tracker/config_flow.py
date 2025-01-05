"""Adds config flow for fressnapf_tracker."""

import logging
from typing import TYPE_CHECKING, Any

import phonenumbers
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import SelectSelector, SelectSelectorMode, SelectSelectorConfig
from phonenumbers import format_number, parse

from .client import (
    InvalidToken,
    InvalidCredentials,
    request_sms_code, verify_phone_number, get_devices
)
import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    CONN_CLASS_CLOUD_POLL,
)
from homeassistant.helpers.httpx_client import get_async_client

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_PHONENUMBER, CONF_SMSTOKEN, CONF_SERIALNUMBER, CONF_AUTH_TOKEN, CONF_DEVICE_TOKEN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FressnapfTrackerFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._userid = ""
        self._user_access_token = ""
        self._devicelist = []
        self._cloud_auth_token = "FgvX_UJ7!BQRLU((1WhwFoOp"  # yes, that's a static key....
    """Config flow for fressnapf_tracker."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Manual user configuration."""
        return await self.async_step_request_sms_code(user_input)


    async def async_step_request_sms_code(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:

            formatted_number = format_number(phonenumbers.parse(user_input[CONF_PHONENUMBER], "DE"),
                                             phonenumbers.PhoneNumberFormat.E164)
            try:
                response = await request_sms_code(
                    get_async_client(self.hass),
                    formatted_number,
                    self._cloud_auth_token
                )
                self._userid = response["id"]
            except:
                return await self._show_config_form_request_sms_code(user_input)

            return await self.async_step_verify_phone_number()
        return await self._show_config_form_request_sms_code(user_input)

    async def async_step_get_devices(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        self._errors = {}

        try:
            response = await get_devices(
                get_async_client(self.hass),
                self._userid,
                self._user_access_token,
                self._cloud_auth_token
            )
        except InvalidCredentials:
            self._errors["base"] = "invalid_credentials"
            return await self._show_config_form_verify_phone_number(user_input)

        if not user_input is None:

            for entry in self._async_current_entries():
                if entry.data[CONF_SERIALNUMBER] == user_input[CONF_SERIALNUMBER]:
                    #return self.async_abort(reason="already_configured")  # type: ignore[no-any-return]
                    self._errors["base"] = "already_configured"
                    return await self._show_config_form_show_device_selection([device["serialnumber"] for device in response])

            return self.async_create_entry(  # type: ignore[no-any-return]
                title=user_input[CONF_SERIALNUMBER],
                data={CONF_SERIALNUMBER: user_input[CONF_SERIALNUMBER],
                      CONF_AUTH_TOKEN: self._cloud_auth_token,
                      CONF_DEVICE_TOKEN: [a["token"] for a in response if a["serialnumber"] == user_input[CONF_SERIALNUMBER]][0] },
            )

        return await self._show_config_form_show_device_selection([device["serialnumber"] for device in response])

    async def async_step_verify_phone_number(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        self._errors = {}

        if user_input is not None:

            try:
                response = await verify_phone_number(
                    get_async_client(self.hass),
                    self._userid,
                    user_input[CONF_SMSTOKEN],
                    self._cloud_auth_token
                )
            except InvalidToken:
                self._errors["base"] = "invalid_token"
                return await self._show_config_form_verify_phone_number(user_input)

            self._user_access_token = response["user_token"]["access_token"]
            return await self.async_step_get_devices()
        return await self._show_config_form_verify_phone_number(user_input)

    async def _show_config_form_request_sms_code(self, user_input) -> ConfigFlowResult:
        """Show the configuration form."""
        return self.async_show_form(  # type: ignore[no-any-return]
            step_id="request_sms_code",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_PHONENUMBER): str,
                    }
                ),
                user_input,
            ),
            errors=self._errors,
        )

    async def _show_config_form_verify_phone_number(self, user_input) -> ConfigFlowResult:
        """Show the configuration form."""
        return self.async_show_form(  # type: ignore[no-any-return]
            step_id="verify_phone_number",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_SMSTOKEN): str,
                    }
                ),
                user_input,
            ),
            errors=self._errors,
        )

    async def _show_config_form_show_device_selection(self, devices) -> ConfigFlowResult:
        return self.async_show_form(  # type: ignore[no-any-return]
            step_id="get_devices",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_SERIALNUMBER): SelectSelector(
                        config=SelectSelectorConfig(
                        mode=SelectSelectorMode.DROPDOWN,
                        sort=False,
                        options=devices,
                    )
            ),
                    }
                ),
                    devices,
            ),
            errors=self._errors,
        )

