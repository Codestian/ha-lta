# Singapore LTA bus timings custom component for Home Assistant 🚍

Home Assistant custom component to retrieve bus timings in Singapore, using the [Datamall API](https://datamall.lta.gov.sg/content/datamall/en.html) provided by LTA.

## Whats new:
Updated to support v3 of the API (Thanks flaskr), and decapted Codestian's LTA Pip package

## What's new'nt (0.3.0)
- Added `operator` and `type` attributes
  - Now you can tell if its SMRT or Tower Transit etc
  - As well as if its single or double deck
- Fixed a bug where Home Assistant throws an error when buses tracking are not in operation
- [**BREAKING CHANGE**] All sensor values are now strictly integers (no more `ARR` and `NA` text)
  - This is to make automations easier to edit
  - Buses that are arriving or not in operation have values set to `0` min
  - To identify the timing statuses, the attribute flags `bus_arriving` and `bus_unavailable` must be used
  - Refer to table below in **Usage** for explanation

## Installation (HACS)

Installation by HACS is recommended if you would like to stay updated with latest releases.

1. Search for `ha-lta` in the community store and click on `Download this repository with HACS`.

2. Once installed, request for an API key at [Datamall](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html). This key is required for Home Assistant to interact with the bus API.

3. Restart Home Assistant and configure the component in configuration.yaml with the API key and bus stop codes.


## Installation (Manual)

1. Download this repository as a ZIP. Copy the folder `ha-lta` and paste it to the `/custom_components/` folder in your Home Assistant directory. If you do not have a custom_components folder, create one.

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

Some buses only operate on certain timings. By default, all bus numbers configured will have their timings and attributes set to either `0` or `""` unless the response from the API contains the necessary data.

Most buses provide their present locations and can be viewed on the map. If no locations are provided by the API, both latitude and longitude are set to `0` respectively.

### Use cases
- Tell the bus timing before leaving the house through a smart speaker
- Setup a dashboard to track timings without opening phone app
- Make use of timing entities for other IOT related projects
- Have full control of what you want to do with bus timings

### Attribute flags

Version 0.3.0 introduces two new flags that can determine if a bus is either arriving or not in operation. The truth table is as follows:

| `bus_arriving` | `bus_unavailable` | Result | Comments                                                                   |
|--------------|-----------------|--------|----------------------------------------------------------------------------|
| T            | T               | F      | Should not happen, considered invalid as bus cannot be unavailable and arriving at same time |
| T            | F               | T      | Bus is less than 1 min to arrive at bus stop                             |
| F            | T               | T      | Bus is not in operation at point in time or does not exist                    |
| F            | F               | F      | Bus is taking X min to arrive at bus stop                                  |
