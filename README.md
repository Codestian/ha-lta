# LTA bus arrival timings custom component for Home Assistant

Home Assistant custom component to retrieve bus timings for specified bus stops, using the [Datamall API](https://datamall.lta.gov.sg/content/datamall/en.html) provided by LTA.

## Installation (Manual)

1. Download this repository as a ZIP. Copy the folder `/custom_components/ha-lta` and paste it to the `/custom_components/` folder in your Home Assistant directory. If you do not have a custom_components folder, create one.

2. Request for an API key at [Datamall](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html). This key is required for Home Assistant to interact with the bus API.

3. Configure the component in configuration.yaml with the API key and bus stop codes.


## Configuration

Add the following to your configuration.yaml file and restart Home Assistant to load it. Bus stop codes are found at all bus stops and are 5 digit numbers (etc. 97061, 08138).

```yaml
sensor:
  - platform: lta
    bus_stop_code: 'XXXXX'
```

