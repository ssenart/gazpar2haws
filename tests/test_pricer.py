"""Test pricer module."""

import math
from datetime import date

from gazpar2haws.configuration import Configuration
from gazpar2haws.model import (
    CompositePriceValue,
    ConsumptionQuantityArray,
    DateArray,
    PriceUnit,
    QuantityUnit,
    TimeUnit,
    VatRateArray,
)
from gazpar2haws.pricer import Pricer


# ----------------------------------
class TestPricer:  # pylint: disable=R0904

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
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 6
        assert consumption_price_array.value_array[start_date] == 0.05568
        assert consumption_price_array.value_array[end_date] == 0.05568

    # ----------------------------------
    def test_get_consumption_price_array_accross_middle(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 9, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 17
        assert consumption_price_array.value_array[start_date] == 0.05568
        assert consumption_price_array.value_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_accross_start(self):

        start_date = date(2023, 5, 25)
        end_date = date(2023, 6, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 12
        assert consumption_price_array.value_array[start_date] == 0.07790
        assert consumption_price_array.value_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_accross_end(self):

        start_date = date(2024, 12, 25)
        end_date = date(2025, 1, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 12
        assert consumption_price_array.value_array[start_date] == 0.04842
        assert consumption_price_array.value_array[end_date] == 0.07807

    # ----------------------------------
    def test_get_consumption_price_array_outside(self):

        start_date = date(2023, 7, 20)
        end_date = date(2023, 9, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 48
        assert consumption_price_array.value_array[start_date] == 0.05392
        assert consumption_price_array.value_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_before(self):

        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
        assert len(consumption_price_array.value_array) == 5
        assert consumption_price_array.value_array[start_date] == 0.07790
        assert consumption_price_array.value_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_after(self):

        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 5)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
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
        assert consumption_price_array.vat_id == "normal"
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
        assert vat_rate_array_by_id.get("normal") is not None
        assert vat_rate_array_by_id.get("reduced").start_date == start_date
        assert vat_rate_array_by_id.get("reduced").end_date == end_date
        assert len(vat_rate_array_by_id.get("reduced").value_array) == 6
        assert vat_rate_array_by_id.get("reduced").value_array[start_date] == 0.055
        assert vat_rate_array_by_id.get("reduced").value_array[end_date] == 0.055
        assert vat_rate_array_by_id.get("normal").start_date == start_date
        assert vat_rate_array_by_id.get("normal").end_date == end_date
        assert len(vat_rate_array_by_id.get("normal").value_array) == 6
        assert vat_rate_array_by_id.get("normal").value_array[start_date] == 0.2
        assert vat_rate_array_by_id.get("normal").value_array[end_date] == 0.2

    # ----------------------------------
    def test_get_time_unit_convertion_factor(self):

        dt = date(2023, 8, 20)

        assert math.isclose(Pricer.get_time_unit_convertion_factor(TimeUnit.YEAR, TimeUnit.MONTH, dt), 12, rel_tol=1e-6)
        assert math.isclose(
            Pricer.get_time_unit_convertion_factor(TimeUnit.MONTH, TimeUnit.YEAR, dt), 1 / 12, rel_tol=1e-6
        )
        assert math.isclose(Pricer.get_time_unit_convertion_factor(TimeUnit.YEAR, TimeUnit.DAY, dt), 365, rel_tol=1e-6)
        assert math.isclose(
            Pricer.get_time_unit_convertion_factor(TimeUnit.DAY, TimeUnit.YEAR, dt), 1 / 365, rel_tol=1e-6
        )
        assert math.isclose(Pricer.get_time_unit_convertion_factor(TimeUnit.MONTH, TimeUnit.DAY, dt), 31, rel_tol=1e-6)
        assert math.isclose(
            Pricer.get_time_unit_convertion_factor(TimeUnit.DAY, TimeUnit.MONTH, dt), 1 / 31, rel_tol=1e-6
        )

    # ----------------------------------
    def test_get_price_unit_convertion_factor(self):

        assert math.isclose(
            Pricer.get_price_unit_convertion_factor(PriceUnit.EURO, PriceUnit.CENT), 100.0, rel_tol=1e-6
        )
        assert math.isclose(Pricer.get_price_unit_convertion_factor(PriceUnit.CENT, PriceUnit.EURO), 0.01, rel_tol=1e-6)

    # ----------------------------------
    def test_get_quantity_unit_convertion_factor(self):

        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.KWH, QuantityUnit.MWH), 0.001, rel_tol=1e-6
        )
        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.MWH, QuantityUnit.KWH), 1000.0, rel_tol=1e-6
        )
        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.WH, QuantityUnit.KWH), 0.001, rel_tol=1e-6
        )
        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.KWH, QuantityUnit.WH), 1000.0, rel_tol=1e-6
        )
        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.WH, QuantityUnit.MWH), 0.000001, rel_tol=1e-6
        )
        assert math.isclose(
            Pricer.get_quantity_unit_convertion_factor(QuantityUnit.MWH, QuantityUnit.WH), 1000000.0, rel_tol=1e-6
        )

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

        assert math.isclose(Pricer.get_convertion_factor(euro_per_kwh, euro_per_kwh), 1.0, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_kwh, cent_per_kwh), 100.0, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(cent_per_kwh, euro_per_kwh), 0.01, rel_tol=1e-6)

        assert math.isclose(Pricer.get_convertion_factor(euro_per_kwh, euro_per_mwh), 1000.0, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_mwh, euro_per_kwh), 0.001, rel_tol=1e-6)

        assert math.isclose(Pricer.get_convertion_factor(cent_per_mwh, euro_per_kwh), 0.00001, rel_tol=1e-6)

        assert math.isclose(Pricer.get_convertion_factor(euro_per_year, euro_per_month, dt), 1 / 12, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_month, euro_per_year, dt), 12, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_year, euro_per_day, dt), 1 / 365, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_day, euro_per_year, dt), 365, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_month, euro_per_day, dt), 1 / 31, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(euro_per_day, euro_per_month, dt), 31, rel_tol=1e-6)

        assert math.isclose(Pricer.get_convertion_factor(cent_per_year, cent_per_month, dt), 1 / 12, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(cent_per_month, cent_per_year, dt), 12, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(cent_per_year, cent_per_day, dt), 1 / 365, rel_tol=1e-6)
        assert math.isclose(Pricer.get_convertion_factor(cent_per_day, cent_per_year, dt), 365, rel_tol=1e-6)

    # ----------------------------------
    def test_convert(self):

        consumption_prices = self._pricer.pricing_data().consumption_prices

        converted_prices = Pricer.convert(consumption_prices, (PriceUnit.CENT, QuantityUnit.WH, TimeUnit.DAY))

        for i in range(len(consumption_prices) - 1):
            consumption_price = consumption_prices[i]
            converted_price = converted_prices[i]

            assert converted_price.price_unit == PriceUnit.CENT
            assert converted_price.quantity_unit == QuantityUnit.WH
            assert converted_price.quantity_value == 0.1 * consumption_price.quantity_value

    # ----------------------------------
    def _create_quantities(
        self, start_date: date, end_date: date, quantity: float, unit: QuantityUnit
    ) -> ConsumptionQuantityArray:

        quantities = ConsumptionQuantityArray(
            start_date=start_date,
            end_date=end_date,
            value_array=DateArray(start_date=start_date, end_date=end_date, initial_value=quantity),
            value_unit=unit,
            base_unit=TimeUnit.DAY,
        )

        return quantities

    # ----------------------------------
    def test_compute(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        quantities = self._create_quantities(start_date, end_date, 1.0, QuantityUnit.KWH)

        cost_array = self._pricer.compute(quantities, PriceUnit.EURO)

        assert cost_array.start_date == start_date
        assert cost_array.end_date == end_date
        assert cost_array.value_unit == "€"
        assert len(cost_array.value_array) == 6
        assert math.isclose(cost_array.value_array[start_date], 0.86912910, rel_tol=1e-6)
        assert math.isclose(cost_array.value_array[end_date], 0.86912910, rel_tol=1e-6)

    # ----------------------------------
    def _compute_cost(self, pricer: Pricer, single_date: date, quantity: float, unit: QuantityUnit) -> float:

        # Prepare the quantities
        quantities = self._create_quantities(single_date, single_date, quantity, unit)

        # Compute the cost
        cost_array = pricer.compute(quantities, PriceUnit.EURO)

        if cost_array.value_array is not None:
            return cost_array.value_array[single_date]

        return 0.0

    # ----------------------------------
    def test_example_1(self):

        # Load configuration
        config = Configuration.load("tests/config/example_1.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 6, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # Before the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 4, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # After the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 8, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

    # ----------------------------------
    def test_example_2(self):

        # Load configuration
        config = Configuration.load("tests/config/example_2.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 6, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # Before the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 4, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # After the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 8, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

    # ----------------------------------
    def test_example_3(self):

        # Load configuration
        config = Configuration.load("tests/config/example_3.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 6, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # Before the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 4, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # After the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 8, 1), 1.0, QuantityUnit.KWH), 0.0779, rel_tol=1e-6)

        # At the date.
        assert math.isclose(self._compute_cost(pricer, date(2024, 1, 1), 1.0, QuantityUnit.KWH), 0.06888, rel_tol=1e-6)

        # Before the date.
        assert math.isclose(self._compute_cost(pricer, date(2024, 11, 1), 1.0, QuantityUnit.KWH), 0.06888, rel_tol=1e-6)

        # After the date.
        assert math.isclose(self._compute_cost(pricer, date(2024, 3, 1), 1.0, QuantityUnit.KWH), 0.06888, rel_tol=1e-6)

    # ----------------------------------
    def test_example_4(self):

        # Load configuration
        config = Configuration.load("tests/config/example_4.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 6, 1), 10.0, QuantityUnit.KWH), 0.9348, rel_tol=1e-6)

        # Before the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 4, 1), 10.0, QuantityUnit.KWH), 0.9348, rel_tol=1e-6)

        # After the date.
        assert math.isclose(self._compute_cost(pricer, date(2023, 8, 1), 10.0, QuantityUnit.KWH), 0.9348, rel_tol=1e-6)

    # ----------------------------------
    def test_example_5(self):

        # Load configuration
        config = Configuration.load("tests/config/example_5.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 6, 1), 58.0, QuantityUnit.KWH), 6.119195, rel_tol=1e-6
        )

        # Before the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 4, 1), 58.0, QuantityUnit.KWH), 6.119195, rel_tol=1e-6
        )

        # After the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 8, 1), 58.0, QuantityUnit.KWH), 6.119195, rel_tol=1e-6
        )

    # ----------------------------------
    def test_example_6(self):

        # Load configuration
        config = Configuration.load("tests/config/example_6.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 6, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

        # Before the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 4, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

        # After the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 8, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

    # ----------------------------------
    def test_example_6bis(self):

        # Load configuration
        config = Configuration.load("tests/config/example_6bis.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 6, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

        # Before the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 4, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

        # After the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 8, 1), 372.0, QuantityUnit.KWH), 34.87393, rel_tol=1e-6
        )

    # ----------------------------------
    def test_example_7(self):

        # Load configuration
        config = Configuration.load("tests/config/example_7.yaml", "tests/config/secrets.yaml")

        # Build the pricer
        pricer = Pricer(config.pricing)

        # At the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 6, 1), 1476.0, QuantityUnit.KWH), 152.8014, rel_tol=1e-6
        )

        # Before the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 4, 1), 1476.0, QuantityUnit.KWH), 152.8014, rel_tol=1e-6
        )

        # After the date.
        assert math.isclose(
            self._compute_cost(pricer, date(2023, 8, 1), 1476.0, QuantityUnit.KWH), 152.8014, rel_tol=1e-6
        )

    # ----------------------------------
    def test_get_composite_price_array(self):
        """Test the new get_composite_price_array method with both quantity and time components."""

        start_date = date(2023, 6, 1)
        end_date = date(2023, 6, 5)

        # Create VAT rate arrays
        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
        }

        # Fill VAT arrays with test values
        Pricer._fill_value_array(vat_rate_array_by_id["reduced"], self._pricer.pricing_data().vat[:1])  # type: ignore
        Pricer._fill_value_array(vat_rate_array_by_id["normal"], self._pricer.pricing_data().vat[1:2])  # type: ignore

        # Create composite prices with both quantity and time components
        composite_prices = [
            CompositePriceValue(
                start_date=date(2023, 6, 1),
                end_date=date(2023, 6, 3),
                price_unit=PriceUnit.EURO,
                quantity_value=0.08,  # €/kWh
                quantity_unit=QuantityUnit.KWH,
                time_value=20.0,  # €/month
                time_unit=TimeUnit.MONTH,
                vat_id="normal",
            ),
            CompositePriceValue(
                start_date=date(2023, 6, 3),
                end_date=date(2023, 6, 10),
                price_unit=PriceUnit.EURO,
                quantity_value=0.07,  # €/kWh (changed)
                quantity_unit=QuantityUnit.KWH,
                time_value=25.0,  # €/month (changed)
                time_unit=TimeUnit.MONTH,
                vat_id="normal",
            ),
        ]

        # Get the composite price array
        composite_price_array = Pricer.get_composite_price_array(
            start_date=start_date,
            end_date=end_date,
            composite_prices=composite_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        # Verify structure
        assert composite_price_array is not None
        assert composite_price_array.start_date == start_date
        assert composite_price_array.end_date == end_date
        assert composite_price_array.price_unit == PriceUnit.EURO
        assert composite_price_array.quantity_unit == QuantityUnit.KWH
        assert composite_price_array.time_unit == TimeUnit.MONTH
        assert composite_price_array.vat_id == "normal"

        # Verify quantity array
        assert composite_price_array.quantity_value_array is not None
        assert len(composite_price_array.quantity_value_array) == 5  # type: ignore
        # First period (June 1-2): 0.08 * (1 + 0.20) = 0.096
        assert composite_price_array.quantity_value_array[date(2023, 6, 1)] == 0.096  # type: ignore
        assert composite_price_array.quantity_value_array[date(2023, 6, 2)] == 0.096  # type: ignore
        # Second period (June 3-5): 0.07 * (1 + 0.20) = 0.084
        assert composite_price_array.quantity_value_array[date(2023, 6, 3)] == 0.084  # type: ignore
        assert composite_price_array.quantity_value_array[date(2023, 6, 5)] == 0.084  # type: ignore

        # Verify time array
        assert composite_price_array.time_value_array is not None
        assert len(composite_price_array.time_value_array) == 5  # type: ignore
        # First period (June 1-2): 20.0 * (1 + 0.20) = 24.0
        assert composite_price_array.time_value_array[date(2023, 6, 1)] == 24.0  # type: ignore
        assert composite_price_array.time_value_array[date(2023, 6, 2)] == 24.0  # type: ignore
        # Second period (June 3-5): 25.0 * (1 + 0.20) = 30.0
        assert composite_price_array.time_value_array[date(2023, 6, 3)] == 30.0  # type: ignore
        assert composite_price_array.time_value_array[date(2023, 6, 5)] == 30.0  # type: ignore

    # ----------------------------------
    def test_get_composite_price_array_quantity_only(self):
        """Test get_composite_price_array with only quantity component (no time component)."""

        start_date = date(2023, 7, 1)
        end_date = date(2023, 7, 3)

        vat_rate_array_by_id = {
            "normal": VatRateArray(id="normal", start_date=start_date, end_date=end_date),
        }
        Pricer._fill_value_array(vat_rate_array_by_id["normal"], self._pricer.pricing_data().vat[1:2])  # type: ignore

        # Composite price with only quantity component
        composite_prices = [
            CompositePriceValue(
                start_date=date(2023, 7, 1),
                price_unit=PriceUnit.EURO,
                quantity_value=0.05,  # €/kWh
                quantity_unit=QuantityUnit.KWH,
                time_value=None,  # No time component
                time_unit=TimeUnit.MONTH,
                vat_id="normal",
            ),
        ]

        composite_price_array = Pricer.get_composite_price_array(
            start_date=start_date,
            end_date=end_date,
            composite_prices=composite_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        # Quantity array should be filled
        assert composite_price_array.quantity_value_array is not None
        assert composite_price_array.quantity_value_array[date(2023, 7, 1)] == 0.05 * 1.20  # type: ignore

        # Time array should exist but be empty (all zeros/None)
        assert composite_price_array.time_value_array is not None

    # ----------------------------------
    def test_get_composite_price_array_time_only(self):
        """Test get_composite_price_array with only time component (no quantity component)."""

        start_date = date(2023, 7, 1)
        end_date = date(2023, 7, 3)

        vat_rate_array_by_id = {
            "reduced": VatRateArray(id="reduced", start_date=start_date, end_date=end_date),
        }
        Pricer._fill_value_array(vat_rate_array_by_id["reduced"], self._pricer.pricing_data().vat[:1])  # type: ignore

        # Composite price with only time component
        composite_prices = [
            CompositePriceValue(
                start_date=date(2023, 7, 1),
                price_unit=PriceUnit.EURO,
                quantity_value=None,  # No quantity component
                quantity_unit=QuantityUnit.KWH,
                time_value=15.0,  # €/month
                time_unit=TimeUnit.MONTH,
                vat_id="reduced",
            ),
        ]

        composite_price_array = Pricer.get_composite_price_array(
            start_date=start_date,
            end_date=end_date,
            composite_prices=composite_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        # Time array should be filled
        assert composite_price_array.time_value_array is not None
        assert composite_price_array.time_value_array[date(2023, 7, 1)] == 15.0 * 1.055  # type: ignore

        # Quantity array should exist but be empty
        assert composite_price_array.quantity_value_array is not None
