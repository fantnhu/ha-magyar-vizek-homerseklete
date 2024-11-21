from datetime import timedelta
import logging
from typing import Any, Dict, Optional
import asyncio
import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async def async_update_data():
        try:
            session = async_get_clientsession(hass)
            async with async_timeout.timeout(10):
                async with session.get(API_URL) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error {response.status} from API")
                    data = await response.json()
                    
                    if not isinstance(data, dict) or "data" not in data:
                        raise UpdateFailed("Invalid data format received from API")
                    
                    return data["data"]
                    
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout fetching data") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []
    
    if coordinator.data:
        for water_data in coordinator.data:
            if isinstance(water_data, dict) and "nameOfRiver" in water_data and "type" in water_data:
                entities.append(WaterTemperatureSensor(coordinator, water_data))

    async_add_entities(entities, True)

class WaterTemperatureSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = True
    _attr_should_poll = False
    _attr_entity_category = None

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        water_data: dict,
    ) -> None:
        super().__init__(coordinator)
        self._water_name = water_data["nameOfRiver"]
        self._water_type = water_data["type"]
        self._attr_unique_id = f"magyar_vizek_{self._water_type}_{self._water_name.lower()}"
        self._attr_name = self._water_name
        self._attr_native_unit_of_measurement = water_data.get("unitOfMeasurement", "°C")
        
        device_type = "Folyók" if self._water_type == "river" else "Tavak"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"magyar_vizek_{self._water_type}")},
            "name": device_type,
            "manufacturer": "HungaroMet",
            "model": "Vízhőmérséklet szenzor",
            "sw_version": "1.0.0",
        }

    @property
    def icon(self) -> str:
        if self.native_value is None:
            return "mdi:thermometer"
            
        temp = float(self.native_value)
        if temp < 10:
            return "mdi:thermometer-low"
        if temp > 15:
            return "mdi:thermometer-high"
        return "mdi:thermometer"

    @property
    def native_value(self) -> StateType:
        if not self.coordinator.data:
            return None

        water_data = next(
            (item for item in self.coordinator.data 
             if isinstance(item, dict) and 
             item.get("nameOfRiver") == self._water_name and
             item.get("type") == self._water_type),
            None,
        )
        
        if not water_data or "avgTemp" not in water_data:
            return None

        try:
            return float(water_data["avgTemp"])
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> Optional[Dict[str, Any]]:
        if not self.coordinator.data:
            return {}

        water_data = next(
            (item for item in self.coordinator.data 
             if isinstance(item, dict) and 
             item.get("nameOfRiver") == self._water_name and
             item.get("type") == self._water_type),
            None,
        )
        
        if not water_data:
            return {}

        attributes = {
            "type": "Folyó" if self._water_type == "river" else "Tó" if self._water_type == "lake" else self._water_type
        }
        
        unit = water_data.get("unitOfMeasurement", "°C")
        
        if "lastMeasurement" in water_data and isinstance(water_data["lastMeasurement"], list):
            for measurement in water_data["lastMeasurement"]:
                if isinstance(measurement, dict):
                    for location, value in measurement.items():
                        attributes[location] = f"{value} {unit}"

        return attributes