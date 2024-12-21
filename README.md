# gazpar2haws
Gazpar2HAWS is a gateway that reads data history from the GrDF (French gas provider) meter and send it to Home Assistant using WebSocket interface.

It is compatible with Home Assistant Energy Dashboard and permits to upload the history and keep it updated with the latest readings.

## Installation

Gazpar2HAWS can be installed on any host as a standalone program.

### 1. Using source files

The project requires [Poetry](https://python-poetry.org/) tool for dependency and package management.

```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2haws.git

$ cd gazpar2haws

$ poetry install

$ poetry shell

```

### 2. Using PIP package

```sh
$ cd /path/to/my_install_folder/

$ mkdir gazpar2haws

$ cd gazpar2haws

$ python -m venv .venv

$ source .venv/bin/activate

$ pip install gazpar2haws

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
  format: '%(asctime)s %(levelname)s [%(name)s] %(message)s'

grdf:
  scan_interval: 0 # Number of minutes between each data retrieval (0 means no scan: a single data retrieval at startup, then stops).
  devices:
  - name: gazpar2haws
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

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Project status
Gazpar2HAWS has been initiated for integration with [Home Assistant](https://www.home-assistant.io/) energy dashboard.



