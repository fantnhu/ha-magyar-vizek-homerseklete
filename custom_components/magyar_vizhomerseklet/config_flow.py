"""Config flow for Magyar Vizek Hőmérséklete integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return {"title": "Magyar Vizek Hőmérséklete"}

class MagyarVizhomersekletConfigFlow(config_entries.ConfigFlow, domain="magyar_vizhomerseklet"):
    """Handle a config flow for Magyar Vizek Hőmérséklete integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({})
            )

        await self.async_set_unique_id("magyar_vizhomerseklet")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Magyar Vizek Hőmérséklete",
            data={}
        )