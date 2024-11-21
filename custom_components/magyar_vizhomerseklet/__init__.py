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
                    raise ConfigEntryNotReady(f"Error connecting to API: {response.status}")
                    
                data = await response.json()
                
                if not isinstance(data, dict) or "data" not in data:
                    raise ConfigEntryNotReady("Invalid data format received from API")
                
                water_data = data["data"]
                if not isinstance(water_data, list) or not water_data:
                    raise ConfigEntryNotReady("No water data found")
                
                valid_data = [item for item in water_data 
                            if isinstance(item, dict) and 
                            "type" in item and 
                            "nameOfRiver" in item and 
                            "avgTemp" in item]
                
                if not valid_data:
                    raise ConfigEntryNotReady("No valid water data found")
                
                hass.data.setdefault(DOMAIN, {})
                hass.data[DOMAIN][entry.entry_id] = valid_data
                
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise ConfigEntryNotReady(f"Error connecting to API: {err}") from err
    except Exception as err:
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