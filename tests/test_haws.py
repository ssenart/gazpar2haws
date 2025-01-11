"""Test haws module."""
import pytest
from gazpar2haws.haws import HomeAssistantWS

# See WebSocket source code here: https://git.informatik.uni-kl.de/s_menne19/hassio-core/-/blob/fix-tests-assist/homeassistant/components/recorder/websocket_api.py


class TestHomeAssistantWS:

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """

    def setup_method(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self._ha_host = "localhost"
        self._ha_port = 7123
        self._ha_endpoint = "/api/websocket"
        self._ha_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjNTI5N2JmN2U1ZjE0MWRmYWVmNzE4NWRiOTQyYmM3NyIsImlhdCI6MTczNjAxMzA3NiwiZXhwIjoyMDUxMzczMDc2fQ.zsoLmKM1e7CzHvUxbYNTcMYmafTxY9699PFMnOMR0rY"

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_connect(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        await haws.connect()

        await haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_list_statistic_ids(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        await haws.connect()

        statistics = await haws.list_statistic_ids("sum")

        assert statistics is not None

        await haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_exists_statistic_id(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        await haws.connect()

        exists_statistic_id = await haws.exists_statistic_id("sensor.gazpar2haws_volume")

        assert exists_statistic_id is not None

        await haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_get_last_statistic(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        await haws.connect()

        statistics = await haws.get_last_statistic("sensor.gazpar2haws_volume")

        assert statistics is not None

        await haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_import_statistics(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

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
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_clear_statistics(self):

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        await haws.connect()

        await haws.clear_statistics(["sensor.gazpar2haws_volume"])

        await haws.disconnect()

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_create_token(self):

        # Mount HA config: https://community.home-assistant.io/t/developing-home-assistant-core-in-a-vscode-devcontainer/235650

        # Configure API passwordin config: https://github.com/home-assistant/core/issues/25952

        haws = HomeAssistantWS(self._ha_host, self._ha_port, self._ha_endpoint, self._ha_token)

        token = await haws.create_token("ws://localhost:7123/api/websocket", "abc123")        

        assert token is not None