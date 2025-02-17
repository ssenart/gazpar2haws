# gazpar2haws

Gazpar2HAWS is a gateway that reads data history from the GrDF (French gas provider) meter and send it to Home Assistant using WebSocket interface.

It is compatible with Home Assistant Energy Dashboard and permits to upload the history and keep it updated with the latest readings.

It is a complement to the other available projects:

- [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar): HA integration that publishes a Gazpar entity with the corresponding meter value.
- [gazpar2mqtt](https://github.com/ssenart/gazpar2mqtt): [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar) alternative but using MQTT events (it reduce coupling with HA).
- [lovelace-gazpar-card](https://github.com/ssenart/lovelace-gazpar-card): HA dashboard card compatible with [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar) and [gazpar2mqtt](https://github.com/ssenart/gazpar2mqtt).

## Installation

Gazpar2HAWS can be installed in many ways.

### 1. Home Assistant Add-on

In the **Add-on store**, click **⋮ → Repositories**, fill in **`https://github.com/ssenart/gazpar2haws`** and click **Add → Close** or click the **Add repository** button below, click **Add → Close** (You might need to enter the **internal IP address** of your Home Assistant instance first).

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fssenart%2Fgazpar2haws)

For usage and configuration, read the documentation [here](addons/gazpar2haws/DOCS.md).

### 2. Using Docker Hub

The following steps permits to run a container from an existing image available in the Docker Hub repository.

1. Copy and save the following docker-compose.yaml file:

```yaml
services:
  gazpar2haws:
    image: ssenart/gazpar2haws:latest
    container_name: gazpar2haws
    restart: unless-stopped
    network_mode: bridge
    user: "1000:1000"
    volumes:
      - ./gazpar2haws/config:/app/config
      - ./gazpar2haws/log:/app/log
    environment:
      - GRDF_USERNAME=<GrDF account username>
      - GRDF_PASSWORD=<GrDF account password>
      - GRDF_PCE_IDENTIFIER=<GrDF PCE meter identifier>
      - HOMEASSISTANT_HOST=<Home Assistant instance host name>
      - HOMEASSISTANT_TOKEN=<Home Assistant access token>
```

Edit the environment variable section according to your setup.

2. Run the container:

```sh
$ docker compose up -d
```

### 3. Using PIP package

```sh
$ cd /path/to/my_install_folder/

$ mkdir gazpar2haws

$ cd gazpar2haws

$ python -m venv .venv

$ source .venv/bin/activate

$ pip install gazpar2haws

```

### 4. Using Dockerfile

The following steps permit to build the Docker image based on the local source files.

1. Clone the repo locally:

```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2haws.git
```

2. Edit the docker-compose.yaml file by setting the environment variables corresponding to your GrDF account and Home Assistant setup:

```yaml
environment:
  - GRDF_USERNAME=<GrDF account username>
  - GRDF_PASSWORD=<GrDF account password>
  - GRDF_PCE_IDENTIFIER=<GrDF PCE meter identifier>
  - HOMEASSISTANT_HOST=<Home Assistant instance host name>
  - HOMEASSISTANT_PORT=<Home Assistant instance port number>
  - HOMEASSISTANT_TOKEN=<Home Assistant access token>
```

3. Build the image:

```sh
$ docker compose -f docker/docker-compose.yaml build
```

4. Run the container:

```sh
$ docker compose -f docker/docker-compose.yaml up -d
```

### 5. Using source files

The project requires [Poetry](https://python-poetry.org/) tool for dependency and package management.

```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2haws.git

$ cd gazpar2haws

$ poetry install

$ poetry shell

```

## Usage

### Command line

```sh
$ python -m gazpar2haws --config /path/to/configuration.yaml --secrets /path/to/secrets.yaml
```

### Configuration file

The default configuration file is below.

```yaml
logging:
  file: log/gazpar2haws.log
  console: true
  level: debug
  format: "%(asctime)s %(levelname)s [%(name)s] %(message)s"

grdf:
  scan_interval: 0 # Number of minutes between each data retrieval (0 means no scan: a single data retrieval at startup, then stops).
  devices:
    - name: gazpar2haws # Name of the device in home assistant. It will be used as the entity_ids: sensor.${name}_volume and sensor.${name}_energy.
      username: "!secret grdf.username"
      password: "!secret grdf.password"
      pce_identifier: "!secret grdf.pce_identifier"
      timezone: Europe/Paris
      last_days: 365 # Number of days of data to retrieve
      reset: false # If true, the data will be reset before the first data retrieval

homeassistant:
  host: "!secret homeassistant.host"
  port: "!secret homeassistant.port"
  token: "!secret homeassistant.token"
```

The default secret file:

```yaml
grdf.username: ${GRDF_USERNAME}
grdf.password: ${GRDF_PASSWORD}
grdf.pce_identifier: ${GRDF_PCE_IDENTIFIER}

homeassistant.host: ${HA_HOST}
homeassistant.port: ${HA_PORT}
homeassistant.token: ${HA_TOKEN}
```

The history is uploaded on the entities with names:

- sensor.${name}\_volume: Volume history in m³.
- sensor.${name}\_energy: Energy history in kWh.

`${name}` is 'gazpar2haws' defined in the above configuration file. It can be replaced by any other name.

### Cost configuration

Gazpar2HAWS is able to compute and publish cost history to Home Assistant.

The cost computation is based in gas prices defined in the configuration files.

The section 'Pricing' is broken into 5 sub-sections:
- vat: Value added tax definition.
- consumption_prices: All the gas price history in €/kWh.
- subscription_prices: The subscription prices in €/month (or year).
- transport_prices: The fixed prices in €/month (or year) to transport the gas.
- energy_taxes: Various taxes on energy in €/kWh.

Below, many examples illustrates how to use pricing configuration for use cases from the simplest to the most complex.


Example 1: A fixed consumption price
---

The given price applies at the given date, after and before.

The default unit is € per kWh.

**Formula:**
```math
cost[€] = quantity[kWh] * price[€/kWh]
```


```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
```

Example 2: A fixed consumption price in another unit
---

*value_unit* is the price unit (default: €).
*base_unit* is the denominator unit (default: kWh).

**Formula:**
```math
cost[€] = \frac{quantity[kWh] * price[¢/MWh] * converter\_factor[¢->€]} {converter\_factor[MWh->kWh]}
```


```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 7790.0 # Unit is now ¢/MWh.
      value_unit: "¢"
      base_unit: "MWh"
```

Example 3: Multiple prices over time
---

```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
    - start_date: "2024-01-01"
      value: 0.06888 # Default unit is €/kWh.
```

Price is 0.07790 before 2024-01-01.

Price is 0.06888 on 2024-01-01 and after.


Example 4: Price is given excluding tax
---

The *normal* value added tax (*vat*) rate is 20%.

```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
      vat_id: "normal" # Reference to the vat rate that is applied for this period.
```

**Formula:**
```math
cost[€] = quantity[kWh] * price[€/kWh] * (1 + vat[normal])
```

Example 5: Subscription price
---

A fixed montly subscription is due over consumption.

Subscription *vat* tax may be different than the consumption *vat* tax.

```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
    - id: reduced
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.0550
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
      vat_id: "normal" # Reference to the vat rate that is applied for this period.
  subscription_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 19.83
      value_unit: "€"
      base_unit: "month"
      vat_id: "reduced"
```

**Formula:**
```math
cost[€] = quantity[kWh] * cons\_price[€/kWh] * (1 + vat[normal]) + sub\_price * (1 + vat[reduced])
```


Example 6: Transport price
---

A fixed yearly transport may be charged as well.

```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
    - id: reduced
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.0550
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
      vat_id: "normal" # Reference to the vat rate that is applied for this period.
  transport_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 34.38
      value_unit: "€"
      base_unit: "year"
      vat_id: reduced
```
**Formula:**
```math
cost[€] = quantity[kWh] * cons\_price[€/kWh] * (1 + vat[normal]) + trans\_price * (1 + vat[reduced])
```

Example 7: Energy taxes
---

Consumption may be taxed by additional taxes (known as energy taxes).

```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
    - id: reduced
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.0550
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790 # Default unit is €/kWh.
      vat_id: "normal" # Reference to the vat rate that is applied for this period.
  energy_taxes:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.00837
      value_unit: "€"
      base_unit: "kWh"
      vat_id: normal
```
**Formula:**
```math
cost[€] = quantity[kWh] * (cons\_price[€/kWh] + ener\_taxes[€/kWh])* (1 + vat[normal])
```

Example 8: All in one
---

In the price list, the first item properties are propagated to the next items in the list. If their values does not change, it is not required to repeat them.

```yaml
pricing:
  vat:
    - id: reduced
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.0550
    - id: normal
      start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.20
  consumption_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.07790
      value_unit: "€"
      base_unit: "kWh"
      vat_id: normal
    - start_date: "2023-07-01"
      value: 0.05392
    - start_date: "2023-08-01"
      value: 0.05568
    - start_date: "2023-09-01"
      value: 0.05412
    - start_date: "2023-10-01"
      value: 0.06333
    - start_date: "2023-11-01"
      value: 0.06716
    - start_date: "2023-12-01"
      value: 0.07235
    - start_date: "2024-01-01"
      value: 0.06888
    - start_date: "2024-02-01"
      value: 0.05972
    - start_date: "2024-03-01"
      value: 0.05506
    - start_date: "2024-04-01"
      value: 0.04842
    - start_date: "2025-01-01"
      value: 0.07807
  subscription_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 19.83
      value_unit: "€"
      base_unit: "month"
      vat_id: reduced
    - start_date: "2023-07-01"
      value: 20.36
  transport_prices:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 34.38
      value_unit: "€"
      base_unit: "year"
      vat_id: reduced
  energy_taxes:
    - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
      value: 0.00837
      value_unit: "€"
      base_unit: "kWh"
      vat_id: normal
    - start_date: "2024-01-01"
      value: 0.01637
```

### Environment variable for Docker

In a Docker environment, the configurations files are instantiated by replacing the environment variables below in the template files:

| Environment variable | Description                                                                   | Required | Default value  |
| -------------------- | ----------------------------------------------------------------------------- | -------- | -------------- |
| GRDF_USERNAME        | GrDF account user name                                                        | Yes      | -              |
| GRDF_PASSWORD        | GrDF account password (avoid using special characters)                        | Yes      | -              |
| GRDF_PCE_IDENTIFIER  | GrDF meter PCE identifier                                                     | Yes      | -              |
| GRDF_SCAN_INTERVAL   | Period in minutes to refresh meter data (0 means one single refresh and stop) | No       | 480 (8 hours)  |
| GRDF_LAST_DAYS       | Number of days of history data to retrieve                                    | No       | 1095 (3 years) |
| HOMEASSISTANT_HOST   | Home Assistant instance host name                                             | Yes      | -              |
| HOMEASSISTANT_PORT   | Home Assistant instance port number                                           | No       | 8123           |
| HOMEASSISTANT_TOKEN  | Home Assistant access token                                                   | Yes      | -              |

You can setup them directly in a docker-compose.yaml file (environment section) or from a Docker command line (-e option).

## FAQ

- *Is it an official GrDF application ?*

  No, absolutely not. It was made by reverse engineering GrDF website without any guarantee of long-term operation. Indeed, any modification made to their website risks breaking it.

- *I'm confused. What are the differences between [PyGazpar](https://github.com/ssenart/PyGazpar), [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar), [lovelace-gazpar-card](https://github.com/ssenart/lovelace-gazpar-card), [Gazpar2MQTT](https://github.com/ssenart/gazpar2mqtt), [Gazpar2HAWS](https://github.com/ssenart/gazpar2haws) ?*

    - [PyGazpar](https://github.com/ssenart/PyGazpar) is the low-level Python library used to query GrDF data. It was written for use by other Python programs.
    - [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar) is the first program using PyGazpar. This is a Home Assistant integration which makes it possible to provide an energy sensor. Coupled with the Recorder integration, it is capable of building a history (called statistics in HA) and displaying it using the Energy Dashboard. It is also compatible with the [lovelace-gazpar-card](https://github.com/ssenart/lovelace-gazpar-card).
    - [lovelace-gazpar-card](https://github.com/ssenart/lovelace-gazpar-card) is a HA card which nicely displays historical data in the form of tables or bar graphs. It is also compatible with [Gazpar2MQTT](https://github.com/ssenart/gazpar2mqtt).
    - [Gazpar2MQTT](https://github.com/ssenart/gazpar2mqtt) offers exactly the same functionality as [home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar) but runs outside of HA as a standalone application, in a Docker container or in an HA add-on.
    - [Gazpar2HAWS](https://github.com/ssenart/gazpar2haws) replaces the use of home-assistant-gazpar/Gazpar2MQTT with the HA Recorder integration to create a data history (for Energy dashboard integration). The disadvantage of the latter solution is the non-alignment of the actual reading date and its publication date. Reading values ​​are made available for 2 to 5 days (and sometimes longer). [Gazpar2HAWS](https://github.com/ssenart/gazpar2haws) timestamps the reading value exactly to the observation dates without any offset. In addition, [Gazpar2HAWS](https://github.com/ssenart/gazpar2haws) is able to reconstruct the complete history of your data up to 3 years in the past, which is very practical in the event of data loss. Finally, it provides ways to calculate and publish energy costs.

- *My PCE ID has a leading zero (e.g. "0123456789") and the application fails with an error indicating that the PCE number is unknown. I can see in the log file that it uses "123456789" without the leading zero. What happened ?*

  The cause is in your configuration file (grdf.devices[].pce_identifier) ​​where you configured your PCE identifier and you did not quote it. Your PCE number is then interpreted as a number instead of a string.

## Troubleshooting

Sometimes, for any reason, the application does not work as expected. No entities is created in HA, some error messages are displayed, nothing happens...

In this situation, the most valuable tool for troubleshooting what is happening is the log file.

Take a look at it, try to find a clue that might help solve the problem. Sorry, the log file can sometimes appear cryptic.

If your configuration is correct, you may have spotted a bug.

In this case, capture a Github issue [here](https://github.com/ssenart/gazpar2haws/issues) with the following information:
1. What kind of setup do you use ? Standalone application, Docker container or HA addon.
2. Is this a first installation or a version upgrade ? If upgrading version, what was the previous version and did it work well ?
3. Describe as precisely as possible what is happening.
4. Provide the complete log file (from start to finish) and make sure to erase all your secrets from it.

The first log lines should be similar to:
```log
2025-02-17 02:01:17,626 INFO [__main__] Starting Gazpar2HAWS version 0.3.0
2025-02-17 02:01:17,627 INFO [__main__] Running on Python version: 3.12.9 (main, Feb  7 2025, 01:03:02) [GCC 12.2.0]
```

The normal last lines of the log should be:
```log
2025-02-17 10:02:42,162 INFO [gazpar2haws.gazpar] No volume data to publish
2025-02-17 10:02:42,162 INFO [gazpar2haws.gazpar] No energy data to publish
2025-02-17 10:02:42,162 INFO [gazpar2haws.gazpar] No cost data to publish
2025-02-17 10:02:42,162 INFO [gazpar2haws.bridge] Device 'gazpar2haws' data published to Home Assistant WS.
2025-02-17 10:02:42,162 INFO [gazpar2haws.bridge] Gazpar data published to Home Assistant WS.
2025-02-17 10:02:42,166 INFO [gazpar2haws.bridge] Waiting 480 minutes before next scan...
```

## Publish a new image on Docker Hub

1. List all local images

```sh
$ docker image ls
```

2. Build a new local image

```sh
$ docker compose -f docker/docker-compose.yaml build
```

3. Tag the new built image with the version number

```sh
$ docker image tag ssenart/gazpar2haws:latest ssenart/gazpar2haws:0.1.2
```

4. Login in Docker Hub

```sh
$ docker login
```

5. Push all the tagged local images to Docker Hub

```sh
$ docker push --all-tags ssenart/gazpar2haws
```

All the gazpar2haws images are available [here](https://hub.docker.com/repository/docker/ssenart/gazpar2haws/general).

## Contributing

Pull requests are welcome. For any change proposal, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Project status

Gazpar2HAWS has been initiated for integration with [Home Assistant](https://www.home-assistant.io/) energy dashboard.
