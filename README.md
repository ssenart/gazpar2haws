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
  format: '%(asctime)s %(levelname)s [%(name)s] %(message)s'

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
- sensor.${name}_volume: Volume history in m³.
- sensor.${name}_energy: Energy history in kWh.

`${name}` is 'gazpar2haws' defined in the above configuration file. It can be replaced by any other name.

### Environment variable for Docker

In a Docker environment, the configurations files are instantiated by replacing the environment variables below in the template files:

| Environment variable | Description | Required | Default value |
|---|---|---|---|
| GRDF_USERNAME  |  GrDF account user name  | Yes | - |
| GRDF_PASSWORD  |  GrDF account password (avoid using special characters) | Yes | - |
| GRDF_PCE_IDENTIFIER  | GrDF meter PCE identifier  | Yes | - |
| GRDF_SCAN_INTERVAL  | Period in minutes to refresh meter data (0 means one single refresh and stop) | No | 480 (8 hours) |
| GRDF_LAST_DAYS | Number of days of history data to retrieve  | No | 1095 (3 years) |
| HOMEASSISTANT_HOST  | Home Assistant instance host name  | Yes | - |
| HOMEASSISTANT_PORT  | Home Assistant instance port number  | No | 8123 |
| HOMEASSISTANT_TOKEN  | Home Assistant access token  | Yes | - |

You can setup them directly in a docker-compose.yaml file (environment section) or from a Docker command line (-e option).

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



