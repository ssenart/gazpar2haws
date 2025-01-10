"""Test gazpar module."""
import pytest
from gazpar2haws import config_utils
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS


# ----------------------------------
@pytest.mark.skip(reason="Requires Home Assistant server")
@pytest.mark.asyncio
async def test_publish():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_endpoint = config.get("homeassistant.endpoint")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_endpoint, ha_token)

    grdf_device_config = config.get("grdf.devices")[0]

    gazpar = Gazpar(grdf_device_config, haws)

    await haws.connect()

    await gazpar.publish()

    await haws.disconnect()
