import logging
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import aiohttp

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]
DOMAIN = "magyar_vizhomerseklet"
API_URL = "https://api.omw.hu/water_temp_hu.php"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    
    try:
        async with async_timeout.timeout(10):
            async with session.get(API_URL) as response:
                if response.status != 200:
                    _LOGGER.error("API error: %s", response.status)
                    raise ConfigEntryNotReady(f"Error connecting to API: {response.status}")
                    
                data = await response.json()
                _LOGGER.debug("Received data: %s", data)
                
                if data is None:
                    _LOGGER.error("API returned None")
                    raise ConfigEntryNotReady("API returned no data")
                
                if not isinstance(data, dict):
                    _LOGGER.error("Invalid data format: %s", type(data))
                    raise ConfigEntryNotReady("Invalid data format received from API")
                
                if "data" not in data or not isinstance(data["data"], list):
                    _LOGGER.error("Missing or invalid data array")
                    raise ConfigEntryNotReady("Invalid data structure received from API")
                
                water_data = data["data"]
                if not water_data:
                    _LOGGER.error("No water data found")
                    raise ConfigEntryNotReady("No water data found")
                
                valid_data = [item for item in water_data if isinstance(item, dict) and "type" in item]
                if not valid_data:
                    _LOGGER.error("No valid water data with type field found")
                    raise ConfigEntryNotReady("No valid water data found")
                
                hass.data.setdefault(DOMAIN, {})
                hass.data[DOMAIN][entry.entry_id] = valid_data
                
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.error("Connection error: %s", err)
        raise ConfigEntryNotReady(f"Error connecting to API: {err}") from err
    except Exception as err:
        _LOGGER.error("Unexpected error occurred: %s", err)
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)