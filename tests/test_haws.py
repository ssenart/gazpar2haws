"""Test haws module."""

import asyncio
from datetime import datetime

import pytest

from gazpar2haws import config_utils
from gazpar2haws.haws import HomeAssistantWS
from gazpar2haws.model import PriceUnit

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

        await self._haws.import_statistics("sensor.gazpar2haws_volume", "recorder", "test", "volume", "m³", statistics)

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_clear_statistics(self):

        await self._haws.connect()

        await self._haws.clear_statistics(
            ["sensor.gazpar2haws_energy", "sensor.gazpar2haws_volume", "sensor.gazpar2haws_cost"]
        )

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_update_statistics_metadata(self):

        await self._haws.connect()

        await self._haws.update_statistics_metadata(
            "sensor.gazpar2haws_energy",
            "energy",
            "kWh",
        )

        await self._haws.update_statistics_metadata(
            "sensor.gazpar2haws_cost",
            None,
            PriceUnit.EUR,
        )

        await self._haws.update_statistics_metadata(
            "sensor.gazpar2haws_volume",
            "volume",
            "m³",
        )

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistic_from_v_0_3_x_old_sensor_not_exists(self):
        """Test migration when old sensor doesn't exist - should skip gracefully."""

        await self._haws.connect()

        # Migrate from non-existent old sensor - should return True (success/skip)
        from datetime import date

        result = await self._haws.migrate_statistic_from_v_0_3_x(
            "sensor.gazpar2haws_nonexistent",
            "sensor.gazpar2haws_total_cost",
            "Gazpar2HAWS Total Cost",
            None,
            PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date.today(),
        )

        assert result is True

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistic_from_v_0_3_x_both_sensors_exist(self):
        """Test migration when both old and new sensors exist - should skip to prevent data loss."""

        await self._haws.connect()

        # Clear any existing data from previous tests
        try:
            await self._haws.clear_statistics(["sensor.gazpar2haws_cost", "sensor.gazpar2haws_total_cost"])
        except Exception:  # pylint: disable=broad-except
            pass  # OK if sensors don't exist yet

        # First, ensure both sensors exist by importing test data
        old_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
        ]
        new_statistics = [
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        await self._haws.import_statistics("sensor.gazpar2haws_cost", "recorder", "Old Cost", None, PriceUnit.EUR, old_statistics)
        await self._haws.import_statistics(
            "sensor.gazpar2haws_total_cost", "recorder", "New Total Cost", None, PriceUnit.EUR, new_statistics
        )

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Attempt migration when both exist - should return True (skip with warning)
        from datetime import date

        result = await self._haws.migrate_statistic_from_v_0_3_x(
            "sensor.gazpar2haws_cost",
            "sensor.gazpar2haws_total_cost",
            "Gazpar2HAWS Total Cost",
            None,
            PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date(2024, 12, 31),
        )

        assert result is True

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Verify new sensor still has original data (not overwritten)
        import pytz

        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime(2024, 12, 1))
        end = tz.localize(datetime(2024, 12, 31))
        new_stats = await self._haws.statistics_during_period(["sensor.gazpar2haws_total_cost"], start, end)
        assert len(new_stats["sensor.gazpar2haws_total_cost"]) == 1
        assert new_stats["sensor.gazpar2haws_total_cost"][0]["sum"] == 300.0

        # Clean up
        await self._haws.clear_statistics(["sensor.gazpar2haws_cost", "sensor.gazpar2haws_total_cost"])

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistic_from_v_0_3_x_successful_migration(self):
        """Test successful migration of data from old to new sensor."""

        await self._haws.connect()

        # Clear any existing data from previous tests
        try:
            await self._haws.clear_statistics(
                ["sensor.gazpar2haws_cost_migrate_test", "sensor.gazpar2haws_total_cost_migrate_test"]
            )
        except Exception:  # pylint: disable=broad-except
            pass  # OK if sensors don't exist yet

        # Create old sensor with historical data
        old_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        await self._haws.import_statistics(
            "sensor.gazpar2haws_cost_migrate_test", "recorder", "Old Cost", None, PriceUnit.EUR, old_statistics
        )

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Perform migration - should succeed and copy all data
        from datetime import date

        result = await self._haws.migrate_statistic_from_v_0_3_x(
            "sensor.gazpar2haws_cost_migrate_test",
            "sensor.gazpar2haws_total_cost_migrate_test",
            "Gazpar2HAWS Total Cost",
            None,
            PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date(2024, 12, 31),
        )

        assert result is True

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Verify new sensor has all the data from old sensor
        import pytz

        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime(2024, 12, 1))
        end = tz.localize(datetime(2024, 12, 31))
        new_stats = await self._haws.statistics_during_period(
            ["sensor.gazpar2haws_total_cost_migrate_test"], start, end
        )
        assert "sensor.gazpar2haws_total_cost_migrate_test" in new_stats
        assert len(new_stats["sensor.gazpar2haws_total_cost_migrate_test"]) == 3
        assert new_stats["sensor.gazpar2haws_total_cost_migrate_test"][0]["sum"] == 100.0
        assert new_stats["sensor.gazpar2haws_total_cost_migrate_test"][1]["sum"] == 200.0
        assert new_stats["sensor.gazpar2haws_total_cost_migrate_test"][2]["sum"] == 300.0

        # Clean up
        await self._haws.clear_statistics(
            ["sensor.gazpar2haws_cost_migrate_test", "sensor.gazpar2haws_total_cost_migrate_test"]
        )

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistics_from_v_0_4_x_successful_migration(self):
        """Test successful migration of data from old to new units."""

        await self._haws.connect()

        # Clear any existing data from previous tests
        try:
            await self._haws.clear_statistics(
                ["sensor.gazpar2haws_consumption_cost_migrate_test", "sensor.gazpar2haws_subscription_cost_migrate_test"]
            )
        except Exception:  # pylint: disable=broad-except
            pass  # OK if sensors don't exist yet

        # Create old sensor with historical data
        consumption_cost_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        subscription_cost_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        sensors = {
            "sensor.gazpar2haws_consumption_cost_migrate_test": consumption_cost_statistics,
            "sensor.gazpar2haws_subscription_cost_migrate_test": subscription_cost_statistics,
        }

        for sensor_id, statistics in sensors.items():
            await self._haws.import_statistics(sensor_id, "recorder", "Old " + sensor_id.split("_")[-1], None, "€", statistics)

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Perform migration - should succeed and copy all data
        from datetime import date

        result = await self._haws.migrate_statistics_from_v_0_4_x(
            entity_ids=[sensor for sensor in sensors.keys()],
            unit_class=None,
            unit_of_measurement=PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date(2024, 12, 31),
        )

        assert result is True

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Verify new sensor has all the data from old sensor
        import pytz

        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime(2024, 12, 1))
        end = tz.localize(datetime(2024, 12, 31))
        new_stats = await self._haws.statistics_during_period(list(sensors.keys()), start, end)

        for sensor_id in sensors.keys():
            assert sensor_id in new_stats
            assert len(new_stats[sensor_id]) == 3
            assert new_stats[sensor_id][0]["sum"] == 100.0
            assert new_stats[sensor_id][1]["sum"] == 200.0
            assert new_stats[sensor_id][2]["sum"] == 300.0

        await self._haws.disconnect()

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistics_from_v_0_4_x_with_cents_unit(self):
        """Test successful migration of data from old to new units with cents unit."""

        await self._haws.connect()

        # Clear any existing data from previous tests
        try:
            await self._haws.clear_statistics(
                ["sensor.gazpar2haws_transport_cost_migrate_test", "sensor.gazpar2haws_energy_taxes_cost_migrate_test"]
            )
        except Exception:  # pylint: disable=broad-except
            pass  # OK if sensors don't exist yet

        # Create old sensor with historical data

        transport_cost_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        energy_taxes_cost_statistics = [
            {"start": "2024-12-14T00:00:00+00:00", "state": 100.0, "sum": 100.0},
            {"start": "2024-12-15T00:00:00+00:00", "state": 200.0, "sum": 200.0},
            {"start": "2024-12-16T00:00:00+00:00", "state": 300.0, "sum": 300.0},
        ]

        sensors = {
            "sensor.gazpar2haws_transport_cost_migrate_test": transport_cost_statistics,
            "sensor.gazpar2haws_energy_taxes_cost_migrate_test": energy_taxes_cost_statistics,
        }

        for sensor_id, statistics in sensors.items():
            await self._haws.import_statistics(sensor_id, "recorder", "Old " + sensor_id.split("_")[-1], None, "¢", statistics)

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Perform migration - should succeed and copy all data
        from datetime import date

        result = await self._haws.migrate_statistics_from_v_0_4_x(
            entity_ids=[sensor for sensor in sensors.keys()],
            unit_class=None,
            unit_of_measurement=PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date(2024, 12, 31),
        )

        assert result is True

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Verify new sensor has all the data from old sensor
        import pytz

        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime(2024, 12, 1))
        end = tz.localize(datetime(2024, 12, 31))
        new_stats = await self._haws.statistics_during_period(list(sensors.keys()), start, end)

        for sensor_id in sensors.keys():
            assert sensor_id in new_stats
            assert len(new_stats[sensor_id]) == 3
            assert new_stats[sensor_id][0]["sum"] == 10000.0
            assert new_stats[sensor_id][1]["sum"] == 20000.0
            assert new_stats[sensor_id][2]["sum"] == 30000.0

        await self._haws.disconnect()


    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_migrate_statistics_from_v_0_4_x_no_old_data(self):
        """Test successful migration of data from old to new units with no old data."""

        await self._haws.connect()

        # Clear any existing data from previous tests
        try:
            await self._haws.clear_statistics(
                ["sensor.gazpar2haws_consumption_cost_migrate_test", "sensor.gazpar2haws_subscription_cost_migrate_test"]
            )
        except Exception:  # pylint: disable=broad-except
            pass  # OK if sensors don't exist yet

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Perform migration - should succeed and copy all data
        from datetime import date

        result = await self._haws.migrate_statistics_from_v_0_4_x(
            entity_ids=["sensor.gazpar2haws_consumption_cost_migrate_test", "sensor.gazpar2haws_subscription_cost_migrate_test"],
            unit_class=None,
            unit_of_measurement=PriceUnit.EUR,
            timezone="Europe/Paris",
            as_of_date=date(2024, 12, 31),
        )

        assert result is True

        # Wait a moment for Home Assistant to process the import
        await asyncio.sleep(1)

        # Verify new sensor has all the data from old sensor
        import pytz

        tz = pytz.timezone("Europe/Paris")
        start = tz.localize(datetime(2024, 12, 1))
        end = tz.localize(datetime(2024, 12, 31))

        new_stats = await self._haws.statistics_during_period(["sensor.gazpar2haws_consumption_cost_migrate_test", "sensor.gazpar2haws_subscription_cost_migrate_test"], start, end)

        for sensor_id in ["sensor.gazpar2haws_consumption_cost_migrate_test", "sensor.gazpar2haws_subscription_cost_migrate_test"]:
            assert sensor_id not in new_stats

        await self._haws.disconnect()
