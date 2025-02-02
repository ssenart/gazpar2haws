"""Test gazpar module."""

from datetime import date

import pygazpar  # type: ignore
import pytest

from gazpar2haws.configuration import Configuration
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS
from gazpar2haws.model import (
    ConsumptionQuantityArray,
    PriceUnit,
    QuantityUnit,
    TimeUnit,
)
from gazpar2haws.pricer import Pricer


# ----------------------------------
class TestGazpar:

    # ----------------------------------
    def setup_method(self):  # pylint: disable=R0801
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """

        # Load configuration
        self._config = Configuration.load(  # pylint: disable=W0201
            "tests/config/configuration.yaml", "tests/config/secrets.yaml"
        )

        ha_host = self._config.homeassistant.host
        ha_port = self._config.homeassistant.port
        ha_endpoint = self._config.homeassistant.endpoint
        ha_token = self._config.homeassistant.token.get_secret_value()

        self._haws = HomeAssistantWS(  # pylint: disable=W0201
            ha_host, ha_port, ha_endpoint, ha_token
        )

        self._grdf_device_config = self._config.grdf.devices[0]  # pylint: disable=W0201
        self._pricing_config = self._config.pricing  # pylint: disable=W0201

    # ----------------------------------
    # @pytest.mark.skip(reason="Requires Home Assistant server")
    @pytest.mark.asyncio
    async def test_publish(self):

        gazpar = Gazpar(self._grdf_device_config, self._pricing_config, self._haws)

        await self._haws.connect()

        await gazpar.publish()

        await self._haws.disconnect()

    # ----------------------------------
    def test_fetch_daily_gazpar_history(self):

        gazpar = Gazpar(self._grdf_device_config, self._pricing_config, self._haws)

        start_date = date(2019, 6, 1)
        end_date = date(2019, 6, 30)

        daily_history = gazpar.fetch_daily_gazpar_history(start_date, end_date)

        assert daily_history is not None and len(daily_history) > 0

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_find_last_date_and_value(self):

        gazpar = Gazpar(self._grdf_device_config, self._pricing_config, self._haws)

        await self._haws.connect()

        last_date, last_value = await gazpar.find_last_date_and_value(
            "sensor.gazpar2haws_test"
        )

        assert last_date is not None
        assert last_value is not None

        await self._haws.disconnect()

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_push_energy_date_array(self):

        gazpar = Gazpar(self._grdf_device_config, self._pricing_config, self._haws)

        await self._haws.connect()

        start_date = date(2019, 6, 1)
        end_date = date(2019, 6, 30)

        # Fetch the data from GrDF and publish it to Home Assistant
        daily_history = gazpar.fetch_daily_gazpar_history(start_date, end_date)

        # Extract the energy from the daily history
        energy_array = gazpar.extract_property_from_daily_gazpar_history(
            daily_history, pygazpar.PropertyName.ENERGY.value, start_date, end_date
        )

        await gazpar.publish_date_array(
            "sensor.gazpar2haws_test", "kWh", energy_array, 0
        )

        await self._haws.disconnect()

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_push_cost_date_array(self):

        gazpar = Gazpar(self._grdf_device_config, self._pricing_config, self._haws)

        await self._haws.connect()

        start_date = date(2019, 6, 1)
        end_date = date(2019, 6, 30)

        # Fetch the data from GrDF and publish it to Home Assistant
        daily_history = gazpar.fetch_daily_gazpar_history(start_date, end_date)

        # Extract the energy from the daily history
        energy_array = gazpar.extract_property_from_daily_gazpar_history(
            daily_history, pygazpar.PropertyName.ENERGY.value, start_date, end_date
        )

        # Compute the cost from the energy
        quantities = ConsumptionQuantityArray(
            start_date=start_date,
            end_date=end_date,
            value_unit=QuantityUnit.KWH,
            base_unit=TimeUnit.DAY,
            value_array=energy_array,
        )

        # Compute the cost
        if energy_array is not None:
            pricer = Pricer(self._pricing_config)

            cost_array = pricer.compute(quantities, PriceUnit.EURO)
        else:
            cost_array = None

        await gazpar.publish_date_array(
            "sensor.gazpar2haws_energy_test", "kWh", energy_array, 0
        )

        await gazpar.publish_date_array(
            "sensor.gazpar2haws_cost_test",
            cost_array.value_unit,
            cost_array.value_array,
            0,
        )

        await self._haws.disconnect()
