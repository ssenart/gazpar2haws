import pytest
from gazpar2haws import config_utils
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS


# ----------------------------------
@pytest.mark.asyncio
async def test_publish():

    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    ha_host = config.get("homeassistant.host")
    ha_port = config.get("homeassistant.port")
    ha_token = config.get("homeassistant.token")

    haws = HomeAssistantWS(ha_host, ha_port, ha_token)

    grdf_device_config = config.get("grdf.devices")[0]

    gazpar = Gazpar(grdf_device_config, haws)

    await haws.connect()

    await gazpar.publish()

    await haws.disconnect()
