"""Real time bus arrival timings from LTA DataMall"""
from datetime import datetime, timedelta, timezone
import logging

import async_timeout
from dateutil import parser, tz
from ltapysg import get_bus_arrival
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import TIME_MINUTES
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

CONF_API_KEY = "api_key"
CONF_BUS_STOP_CODE = "bus_stop_code"

BUS_ARRIVING = "ARR"
BUS_UNAVAILABLE = "NA"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_API_KEY): cv.string, vol.Required(CONF_BUS_STOP_CODE): cv.string}
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor and initialize platform with configuration values"""

    hass.data["lta"] = {"buses": []}

    def create_bus_sensor(
        bus_number, bus_order, bus_latitude, bus_longitude, bus_timing
    ):
        def convert_datetime(bustime):
            """Convert UTC 8+ datetime to the number of minutes before bus arrive"""
            if bustime:
                time_bus = parser.parse(bustime).astimezone(tz.UTC)
                time_now = datetime.now(tz=timezone.utc)

                time_diff = time_bus - time_now

                time_diff_formatted = round(time_diff.total_seconds() / 60)

                if time_diff_formatted <= 1:
                    return BUS_ARRIVING
                else:
                    return time_diff_formatted
            else:
                return BUS_UNAVAILABLE

        bus_dict = {
            "unique_id": f"{config.get(CONF_BUS_STOP_CODE)}_{bus_number}_{bus_order}",
            "attributes": {} if (bus_latitude == "0" and bus_longitude == "0") or (bus_latitude == "" and bus_longitude == "") else {
                "latitude": bus_latitude,
                "longitude": bus_longitude
            },
            "state": convert_datetime(bus_timing),
        }

        return bus_dict

    async def async_update_data():
        """Poll API and update data to sensors"""
        async with async_timeout.timeout(20):

            sensors = []
            buses = []

            try:

                data = await get_bus_arrival(
                    config.get(CONF_API_KEY), config.get(CONF_BUS_STOP_CODE)
                )

                for bus in data:
                    buses.append(bus["ServiceNo"])

                if not hass.data["lta"]["buses"]:
                    hass.data["lta"]["buses"] = list(buses)
                else:
                    if len(buses) > len(hass.data["lta"]["buses"]):
                        hass.data["lta"]["buses"] = list(buses)

                for bus in hass.data["lta"]["buses"]:
                    test = next(
                        (x for x in data if x["ServiceNo"] == bus), {"ServiceNo": ""}
                    )

                    sensors.append(
                        create_bus_sensor(
                            bus,
                            "1",
                            test["NextBus"]["Latitude"],
                            test["NextBus"]["Longitude"],
                            test["NextBus"]["EstimatedArrival"],
                        )
                    )
                    sensors.append(
                        create_bus_sensor(
                            bus,
                            "2",
                            test["NextBus2"]["Latitude"],
                            test["NextBus2"]["Longitude"],
                            test["NextBus2"]["EstimatedArrival"],
                        )
                    )
                    sensors.append(
                        create_bus_sensor(
                            bus,
                            "3",
                            test["NextBus3"]["Latitude"],
                            test["NextBus3"]["Longitude"],
                            test["NextBus3"]["EstimatedArrival"],
                        )
                    )
            except Exception as e:

                print(e)

                # _LOGGER.error(
                #     e
                #     # "Unable to interact with Datamall, ensure you have an internet connection and a proper bus stop code"
                # )

                for bus in hass.data["lta"]["buses"]:

                    sensors.append(create_bus_sensor(bus, "1", "", "", "",))
                    sensors.append(create_bus_sensor(bus, "2", "", "", "",))
                    sensors.append(create_bus_sensor(bus, "3", "", "", "",))

            return sensors

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_refresh()

    async_add_entities(
        LandTransportSensor(coordinator, idx)
        for idx, ent in enumerate(coordinator.data)
    )


class LandTransportSensor(Entity):
    """
    Sensor that reads bus arrival data from LTA's Datamall.
    The Datamall provides transport related data.
    """

    def __init__(self, coordinator, idx):
        """Initialize the sensor."""

        self.coordinator = coordinator
        self.idx = idx
        self._attributes = coordinator.data[idx]["attributes"]
        self._unique_id = coordinator.data[idx]["unique_id"]
        self._state = coordinator.data[idx]["state"]

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return self.coordinator.data[self.idx]["unique_id"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if(self.coordinator.last_update_success):
            return "mdi:bus-clock"
        else:
            return "mdi:bus-alert"

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor"""
        return self.coordinator.data[self.idx]["attributes"]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.idx]["state"]

    @property
    def should_poll(self):
        return False

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TIME_MINUTES

    @property
    def available(self):
        """Return the availability of sensor"""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update sensor data"""
        await self.coordinator.async_request_refresh()
