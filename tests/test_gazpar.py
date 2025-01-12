"""Test gazpar module."""

import pytest

from gazpar2haws import config_utils
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS


# ----------------------------------
class TestGazpar:

    # ----------------------------------
    def setup_method(self):  # pylint: disable=R0801
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        # Load configuration
        self._config = config_utils.ConfigLoader(  # pylint: disable=W0201
            "config/configuration.yaml", "config/secrets.yaml"
        )
        self._config.load_secrets()
        self._config.load_config()

        ha_host = self._config.get("homeassistant.host")
        ha_port = self._config.get("homeassistant.port")
        ha_endpoint = self._config.get("homeassistant.endpoint")
        ha_token = self._config.get("homeassistant.token")

        self._haws = HomeAssistantWS(  # pylint: disable=W0201
            ha_host, ha_port, ha_endpoint, ha_token
        )

        self._grdf_device_config = self._config.get(  # pylint: disable=W0201
            "grdf.devices"
        )[0]

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_publish(self):

        gazpar = Gazpar(self._grdf_device_config, self._haws)

        await self._haws.connect()

        await gazpar.publish()

        await self._haws.disconnect()
