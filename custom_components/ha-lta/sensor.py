"""Real time bus arrival timings from LTA DataMall"""
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import UnitOfTime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


import logging
import async_timeout
from aiohttp import ClientSession, ClientConnectorError
import voluptuous as vol
from datetime import datetime, timedelta, timezone
from dateutil import parser, tz
from math import floor

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

CONF_API_KEY = "api_key"
CONF_BUS_STOPS = "bus_stops"
CONF_CODE = "code"
CONF_BUSES = "buses"
BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice/"



BUS_SCHEMA = {
    vol.Required(CONF_CODE): cv.string,
    vol.Required(CONF_BUSES): vol.All(cv.ensure_list, [cv.string]),
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_BUS_STOPS): vol.All(cv.ensure_list, [vol.Schema(BUS_SCHEMA)]),
    }
)


# Function to replace the lta pip module. Idea mainly from: https://github.com/Codestian/ha-lta/issues/19 Thanks to @flaskr for providing this fix
async def call(api_key, url):
    async with ClientSession() as session:
        try:
            async with session.get(
                BASE_URL + url,
                headers={"Accept": "application/json", "AccountKey": api_key},
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(
                        "Received status code " + str(response.status)
                    ) from None
        except ClientConnectorError as err:
            raise Exception(str(err)) from None


# Retrieve arrival timings for all buses operating for specified bus stop. Each bus has 3 recurring timings.
async def get_bus_arrival(api_key, bus_stop_code):
    data = await call(api_key, "v3/BusArrival?BusStopCode=" + str(bus_stop_code))
        if "Services" not in data:
        _LOGGER.warning("No 'Services' key in API response for bus stop %s: %s", bus_stop_code, data)
        return []
    return data["Services"]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor and initialize platform with configuration values."""

    def create_bus_sensor(
        bus_stop,
        bus_number,
        bus_order,
        bus_latitude,
        bus_longitude,
        bus_timing,
        bus_operator,
        bus_type,
        bus_load,
    ):
        def buildDict(bus_timing):
            """Convert UTC 8+ datetime to the number of minutes before bus arrives."""

            bus_arriving = False
            bus_unavailable = False
            bus_state = 0

            if bus_timing:
                time_bus = parser.parse(bus_timing).astimezone(tz.UTC)
                time_now = datetime.now(tz=timezone.utc)

                time_diff = time_bus - time_now

                time_diff_formatted = floor(time_diff.total_seconds() / 60)

                if time_diff_formatted <= 1:
                    bus_arriving = True
                else:
                    bus_state = time_diff_formatted
            else:
                bus_unavailable = True

            bus_dict = {
                "unique_id": f"{bus_stop}_{bus_number}_{bus_order}",
                "attributes": {
                    "bus_arriving": bus_arriving,
                    "bus_unavailable": bus_unavailable,
                    "latitude": bus_latitude,
                    "longitude": bus_longitude,
                    "operator": bus_operator,
                    "type": bus_type,
                    "load": bus_load
                },
                "state": bus_state,
            }

            return bus_dict

        return buildDict(bus_timing)

    async def async_update_data():
        """Poll API and update data to sensors."""
        async with async_timeout.timeout(20):

            sensors = []

            """Retrieve all bus timings from each bus stop."""
            try:
                for bus_stop in config.get(CONF_BUS_STOPS):

                    data = await get_bus_arrival(
                        config.get(CONF_API_KEY), bus_stop["code"]
                    )

                    print(data)

                    for one in list(bus_stop["buses"]):
                        idx = next(
                            (
                                index
                                for (index, d) in enumerate(data)
                                if d["ServiceNo"] == one
                            ),
                            None,
                        )
                        """If configured bus exists in API response, use data from response"""
                        if idx is not None:
                            bus = data[idx]
                            """Create entity for 1st timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"],
                                    bus["ServiceNo"],
                                    "1",
                                    bus["NextBus"]["Latitude"],
                                    bus["NextBus"]["Longitude"],
                                    bus["NextBus"]["EstimatedArrival"],
                                    bus["Operator"],
                                    bus["NextBus"]["Type"],
                                    bus["NextBus"]["Load"],
                                )
                            )

                            """Create entity for 2nd timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"],
                                    bus["ServiceNo"],
                                    "2",
                                    bus["NextBus2"]["Latitude"],
                                    bus["NextBus2"]["Longitude"],
                                    bus["NextBus2"]["EstimatedArrival"],
                                    bus["Operator"],
                                    bus["NextBus2"]["Type"],
                                    bus["NextBus2"]["Load"],
                                )
                            )

                            """Create entity for 3rd timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"],
                                    bus["ServiceNo"],
                                    "3",
                                    bus["NextBus3"]["Latitude"],
                                    bus["NextBus3"]["Longitude"],
                                    bus["NextBus3"]["EstimatedArrival"],
                                    bus["Operator"],
                                    bus["NextBus3"]["Type"],
                                    bus["NextBus3"]["Load"],
                                )
                            )
                        else:
                            """Create entity for 1st timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"], one, "1", 0, 0, 0, "", "",""
                                )
                            )
                            """Create entity for 2nd timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"], one, "2", 0, 0, 0, "", "",""
                                )
                            )
                            """Create entity for 3rd timing."""
                            sensors.append(
                                create_bus_sensor(
                                    bus_stop["code"], one, "3", 0, 0, 0, "", "",""
                                )
                            )

            except Exception as e:
                _LOGGER.error(e, "An exeption has occurred")

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
        BusArrivalSensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class BusArrivalSensor(Entity):
    """
    Sensor that tracks bus arrival data from LTA's Datamall API.
    The Datamall provides transport related data in Singapore.
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
        if self.coordinator.last_update_success:
            return "mdi:bus-clock"
        else:
            return "mdi:bus-alert"

    @property
    def extra_state_attributes(self):
        """Return the attributes of the sensor."""
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
        return UnitOfTime.MINUTES

    @property
    def available(self):
        """Return the availability of sensor."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update sensor data."""
        await self.coordinator.async_request_refresh()
