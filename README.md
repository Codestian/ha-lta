# LTA bus arrival timings custom component for Home Assistant 🚌

Home Assistant custom component to retrieve bus timings, using the [Datamall API](https://datamall.lta.gov.sg/content/datamall/en.html) provided by LTA.

## Installation (HACS)

Installation by HACS is recommended if you would like to stay updated with latest releases.

1. [Follow the instructions here](https://hacs.xyz/docs/faq/custom_repositories) and add this repository.

2. Request for an API key at [Datamall](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html). This key is required for Home Assistant to interact with the bus API.

3. Restart Home Assistant and configure the component in configuration.yaml with the API key and bus stop codes.

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

## Usage

After you have added the configuration with a proper bus stop code, multiple sensor entities will be added for each bus number. Each bus number has 3 subsequent timings. The naming convention for a ```lta sensor``` is as follows:

```
lta.$BUS_STOP_CODE-$BUS_NUMBER-$BUS_ORDER
```

For example, sensor ```lta.98051-19-1``` indicates the first timing for bus 19 towards bus stop code 98051. Sensor ```lta.98051-19-2``` will indicate the next subsequent timing for the same bus number.

In rare cases, some bus numbers will only operate in service at certain timings. Home Assistant will automatically add any new additional bus numbers and remember them. 