"""Test haws module."""

from datetime import datetime

import pytest

from gazpar2haws import config_utils
from gazpar2haws.haws import HomeAssistantWS

# See WebSocket source code here: https://git.informatik.uni-kl.de/s_menne19/hassio-core/-/blob/fix-tests-assist/homeassistant/components/recorder/websocket_api.py


# ----------------------------------
class TestHomeAssistantWS:

    # ----------------------------------
    def setup_method(self):
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        # Load configuration
        self._config = config_utils.ConfigLoader(  # pylint: disable=W0201
            "tests/config/configuration.yaml", "tests/config/secrets.yaml"
        )
        self._config.load_secrets()
        self._config.load_config()

        ha_host = self._config.get("homeassistant.host")
        ha_port = self._config.get("homeassistant.port")
        ha_endpoint = (
            self._config.get("homeassistant.endpoint")
            if self._config.get("homeassistant.endpoint")
            else "/api/websocket"
        )
        ha_token = self._config.get("homeassistant.token")

        self._haws = HomeAssistantWS(ha_host, ha_port, ha_endpoint, ha_token)  # pylint: disable=W0201

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_connect(self):

        await self._haws.connect()

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_list_statistic_ids(self):

        await self._haws.connect()

        statistics = await self._haws.list_statistic_ids("sum")

        assert statistics is not None

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_exists_statistic_id(self):

        await self._haws.connect()

        exists_statistic_id = await self._haws.exists_statistic_id("sensor.gazpar2haws_volume")

        assert exists_statistic_id is not None

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_get_last_statistic(self):

        await self._haws.connect()

        statistics = await self._haws.get_last_statistic("sensor.gazpar2haws_volume", datetime.now(), 30)

        assert statistics is not None

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_import_statistics(self):

        await self._haws.connect()

        statistics = [
            {"start": "2020-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2020-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2020-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        await self._haws.import_statistics("sensor.gazpar2haws_volume", "recorder", "test", "m³", statistics)

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_clear_statistics(self):

        await self._haws.connect()

        await self._haws.clear_statistics(["sensor.gazpar2haws_energy", "sensor.gazpar2haws_volume"])

        await self._haws.disconnect()
