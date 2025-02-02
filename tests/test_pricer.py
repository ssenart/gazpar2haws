"""Test pricer module."""

import math
from datetime import date

from gazpar2haws.configuration import Configuration
from gazpar2haws.model import (ConsumptionQuantityArray, DateArray, PriceUnit,
                               QuantityUnit, TimeUnit, VatRateArray)
from gazpar2haws.pricer import Pricer


# ----------------------------------
class TestPricer:

    # ----------------------------------
    def setup_method(self):

        # Load configuration
        config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

        self._pricer = Pricer(config.pricing)  # pylint: disable=W0201

    # ----------------------------------
    def test_get_consumption_price_array_inside(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 6
        assert consumption_price_array.value_array[start_date] == 0.05568
        assert consumption_price_array.value_array[end_date] == 0.05568

    # ----------------------------------
    def test_get_consumption_price_array_accross_middle(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 9, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 17
        assert consumption_price_array.value_array[start_date] == 0.05568
        assert consumption_price_array.value_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_accross_start(self):

        start_date = date(2023, 5, 25)
        end_date = date(2023, 6, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 12
        assert consumption_price_array.value_array[start_date] == 0.07790
        assert consumption_price_array.value_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_accross_end(self):

        start_date = date(2024, 12, 25)
        end_date = date(2025, 1, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 12
        assert consumption_price_array.value_array[start_date] == 0.04842
        assert consumption_price_array.value_array[end_date] == 0.07807

    # ----------------------------------
    def test_get_consumption_price_array_outside(self):

        start_date = date(2023, 7, 20)
        end_date = date(2023, 9, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 48
        assert consumption_price_array.value_array[start_date] == 0.05392
        assert consumption_price_array.value_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_before(self):

        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 5
        assert consumption_price_array.value_array[start_date] == 0.07790
        assert consumption_price_array.value_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_after(self):

        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "standard": VatRateArray(id="standard", start_date=start_date, end_date=end_date),
        }

        consumption_price_array = Pricer.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=self._pricer.pricing_data().consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.value_unit == "€"
        assert consumption_price_array.base_unit == "kWh"
        assert consumption_price_array.vat_id == "standard"
        assert len(consumption_price_array.value_array) == 5
        assert consumption_price_array.value_array[start_date] == 0.07807
        assert consumption_price_array.value_array[end_date] == 0.07807

    # ----------------------------------
    def test_get_vat_rate_array_by_id(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        vat_rate_array_by_id = Pricer.get_vat_rate_array_by_id(
            start_date=start_date,
            end_date=end_date,
            vat_rates=self._pricer.pricing_data().vat,
        )

        assert len(vat_rate_array_by_id) == 2
        assert vat_rate_array_by_id.get("reduced") is not None
        assert vat_rate_array_by_id.get("standard") is not None
        assert vat_rate_array_by_id.get("reduced").start_date == start_date
        assert vat_rate_array_by_id.get("reduced").end_date == end_date
        assert len(vat_rate_array_by_id.get("reduced").value_array) == 6
        assert vat_rate_array_by_id.get("reduced").value_array[start_date] == 0.055
        assert vat_rate_array_by_id.get("reduced").value_array[end_date] == 0.055
        assert vat_rate_array_by_id.get("standard").start_date == start_date
        assert vat_rate_array_by_id.get("standard").end_date == end_date
        assert len(vat_rate_array_by_id.get("standard").value_array) == 6
        assert vat_rate_array_by_id.get("standard").value_array[start_date] == 0.2
        assert vat_rate_array_by_id.get("standard").value_array[end_date] == 0.2

    # ----------------------------------
    def test_get_convertion_factor(self):

        dt = date(2023, 8, 20)

        euro_per_kwh = (PriceUnit.EURO, QuantityUnit.KWH)
        cent_per_kwh = (PriceUnit.CENT, QuantityUnit.KWH)
        euro_per_mwh = (PriceUnit.EURO, QuantityUnit.MWH)
        cent_per_mwh = (PriceUnit.CENT, QuantityUnit.MWH)

        euro_per_year = (PriceUnit.EURO, TimeUnit.YEAR)
        cent_per_year = (PriceUnit.CENT, TimeUnit.YEAR)
        euro_per_month = (PriceUnit.EURO, TimeUnit.MONTH)
        cent_per_month = (PriceUnit.CENT, TimeUnit.MONTH)
        euro_per_day = (PriceUnit.EURO, TimeUnit.DAY)
        cent_per_day = (PriceUnit.CENT, TimeUnit.DAY)

        assert self._pricer.get_convertion_factor(euro_per_kwh, euro_per_kwh) == 1.0
        assert self._pricer.get_convertion_factor(euro_per_kwh, cent_per_kwh) == 100.0
        assert self._pricer.get_convertion_factor(cent_per_kwh, euro_per_kwh) == 0.01

        assert self._pricer.get_convertion_factor(euro_per_kwh, euro_per_mwh) == 1000.0
        assert self._pricer.get_convertion_factor(euro_per_mwh, euro_per_kwh) == 0.001

        assert self._pricer.get_convertion_factor(cent_per_mwh, euro_per_kwh) == 0.00001

        assert self._pricer.get_convertion_factor(euro_per_year, euro_per_month, dt) == 1 / 12
        assert self._pricer.get_convertion_factor(euro_per_month, euro_per_year, dt) == 12
        assert self._pricer.get_convertion_factor(euro_per_year, euro_per_day, dt) == 1 / 365
        assert self._pricer.get_convertion_factor(euro_per_day, euro_per_year, dt) == 365

        assert self._pricer.get_convertion_factor(cent_per_year, cent_per_month, dt) == 1 / 12
        assert self._pricer.get_convertion_factor(cent_per_month, cent_per_year, dt) == 12
        assert self._pricer.get_convertion_factor(cent_per_year, cent_per_day, dt) == 1 / 365
        assert self._pricer.get_convertion_factor(cent_per_day, cent_per_year, dt) == 365

    # ----------------------------------
    def test_convert(self):

        consumption_prices = self._pricer.pricing_data().consumption_prices

        converted_prices = self._pricer.convert(consumption_prices, (PriceUnit.CENT, QuantityUnit.WH))

        for i in range(len(consumption_prices) - 1):
            consumption_price = consumption_prices[i]
            converted_price = converted_prices[i]

            assert converted_price.value_unit == PriceUnit.CENT
            assert converted_price.base_unit == QuantityUnit.WH
            assert converted_price.value == 0.1 * consumption_price.value

    # ----------------------------------
    def test_compute(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        quantities = ConsumptionQuantityArray(
            start_date=start_date,
            end_date=end_date,
            value_unit="kWh",
            base_unit="day",
        )

        quantities.value_array = DateArray(start_date=start_date, end_date=end_date, initial_value=1.0)

        cost_array = self._pricer.compute(quantities, PriceUnit.EURO)

        assert cost_array.start_date == start_date
        assert cost_array.end_date == end_date
        assert cost_array.value_unit == "€"
        assert len(cost_array.value_array) == 6
        assert math.isclose(cost_array.value_array[start_date], 0.86912910, rel_tol=1e-6)
        assert math.isclose(cost_array.value_array[end_date], 0.86912910, rel_tol=1e-6)
