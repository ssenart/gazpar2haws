import pytest
from gazpar2haws.haws import HomeAssistantWS
from gazpar2haws import config_utils

# See WebSocket source code here: https://git.informatik.uni-kl.de/s_menne19/hassio-core/-/blob/fix-tests-assist/homeassistant/components/recorder/websocket_api.py


# ----------------------------------
@pytest.mark.asyncio
async def test_connect():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    await haws.disconnect()


# ----------------------------------
@pytest.mark.asyncio
async def test_list_statistic_ids():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    statistics = await haws.list_statistic_ids("sum")

    assert statistics is not None

    await haws.disconnect()


# ----------------------------------
@pytest.mark.asyncio
async def test_exists_statistic_id():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    exists_statistic_id = await haws.exists_statistic_id("sensor.gazpar2haws_volume")

    assert exists_statistic_id is not None

    await haws.disconnect()


# ----------------------------------
@pytest.mark.asyncio
async def test_get_last_statistic():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    statistics = await haws.get_last_statistic("sensor.gazpar2haws_volume")

    assert statistics is not None

    await haws.disconnect()


# ----------------------------------
@pytest.mark.asyncio
async def test_import_statistics():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    statistics = [
        {
            "start": "2024-12-14T00:00:00+00:00",
            "state": 100.0,
            "sum": 100.0
        },
        {
            "start": "2024-12-15T00:00:00+00:00",
            "state": 200.0,
            "sum": 200.0
        },
        {
            "start": "2024-12-16T00:00:00+00:00",
            "state": 300.0,
            "sum": 300.0
        }
    ]

    await haws.import_statistics("sensor.gazpar2haws_volume", "recorder", "test", "m³", statistics)

    await haws.disconnect()


# ----------------------------------
@pytest.mark.asyncio
async def test_clear_statistics():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    await haws.connect()

    await haws.clear_statistics(["sensor.gazpar2haws_volume"])

    await haws.disconnect()
