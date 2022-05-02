# LTA bus arrival timings custom component for Home Assistant 🚌

Home Assistant custom component to retrieve bus timings, using the [Datamall API](https://datamall.lta.gov.sg/content/datamall/en.html) provided by LTA.

## What's new (2.1.1)
- Changed `device_state_attributes` to `extra_state_attributes`, longitude and latitude attributes should be working again.
- Repository now available to download in the community store. You no longer need to add a custom repository.

## Installation (HACS)

Installation by HACS is recommended if you would like to stay updated with latest releases.

1. Search for `ha-lta` in the community store and click on `Download this repository with HACS`.

2. Once installed, request for an API key at [Datamall](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html). This key is required for Home Assistant to interact with the bus API.

3. Restart Home Assistant and configure the component in configuration.yaml with the API key and bus stop codes.

## Installation (Manual)

1. Download this repository as a ZIP. Copy the folder `/custom_components/ha-lta` and paste it to the `/custom_components/` folder in your Home Assistant directory. If you do not have a custom_components folder, create one.

2. Request for an API key at [LTA Datamall](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html). This key is required for Home Assistant to interact with the bus API.

3. Configure the component in configuration.yaml with the API key and bus stop codes.


## Configuration

Add the following to your `configuration.yaml` file and restart Home Assistant to load the custom component. Bus stop codes are found at all bus stops and are 5 digit numbers such as `97061` and `08138`. At least one bus stop code and one bus is required. 

```yaml
sensor:
- platform: lta
  api_key: XXXXXXXXXX
  bus_stops:
  - code: 'XXXXX'
    buses:
    - 'XX'
    - 'XXX'
    - 'X'
  - code: 'XXXXX'
    buses:
    - 'X'
    - 'XX'
```

## Usage

After you have setup the configuration with valid bus stop codes and bus numbers, multiple sensor entities will be added for each bus number. Each bus number has 3 subsequent timings. The naming convention for a ```lta``` sensor is as follows:

```
lta.BUS_STOP_CODE-BUS_NUMBER-BUS_ORDER
```

For example, sensor ```lta.98051-19-1``` indicates the first timing for bus 19 towards bus stop code 98051. Sensor ```lta.98051-19-2``` will indicate the next subsequent timing for the same bus number.

Some buses only operate on certain timings. Home Assistant will automatically add and remember them when they are in operation.

Most buses provide their present locations and can be viewed on the map.

### Use cases
- Tell the bus timing before leaving the house through a smart speaker
- Setup a dashboard to track timings without opening phone app
- Make use of timing entities for other IOT related projects 