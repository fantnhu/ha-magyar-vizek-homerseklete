from __future__ import annotations
from typing import Any
from homeassistant import config_entries
import voluptuous as vol
from . import DOMAIN

class MagyarVizhomersekletConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Magyar Vizek Hőmérséklete",
                data={},
                description_placeholders={
                    "description": "A Magyar Vizek Hőmérséklete integráció adatait a HungaroMet biztosítja"
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "description": "A Magyar Vizek Hőmérséklete integráció adatait a HungaroMet biztosítja"
            }
        )