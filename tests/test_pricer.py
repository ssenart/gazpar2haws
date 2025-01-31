"""Test pricer module."""

from gazpar2haws.configuration import Configuration
from gazpar2haws.pricer import Pricer

from datetime import date

# ----------------------------------
class TestPricer:

    # ----------------------------------
    def setup_method(self):
        
        # Load configuration
        config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

        self._pricer = Pricer(config.pricing)

    # ----------------------------------
    def test_get_consumption_price_array_inside(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 6
        assert consumption_price_array.price_array[start_date] == 0.05568
        assert consumption_price_array.price_array[end_date] == 0.05568

    # ----------------------------------
    def test_get_consumption_price_array_accross_middle(self):

        start_date = date(2023, 8, 20)
        end_date = date(2023, 9, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 17
        assert consumption_price_array.price_array[start_date] == 0.05568
        assert consumption_price_array.price_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_accross_start(self):

        start_date = date(2023, 5, 25)
        end_date = date(2023, 6, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 12
        assert consumption_price_array.price_array[start_date] == 0.07790
        assert consumption_price_array.price_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_accross_end(self):

        start_date = date(2024, 12, 25)
        end_date = date(2025, 1, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 12
        assert consumption_price_array.price_array[start_date] == 0.04842
        assert consumption_price_array.price_array[end_date] == 0.07807

    # ----------------------------------
    def test_get_consumption_price_array_outside(self):

        start_date = date(2023, 7, 20)
        end_date = date(2023, 9, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 48
        assert consumption_price_array.price_array[start_date] == 0.05392
        assert consumption_price_array.price_array[end_date] == 0.05412

    # ----------------------------------
    def test_get_consumption_price_array_before(self):

        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 5
        assert consumption_price_array.price_array[start_date] == 0.07790
        assert consumption_price_array.price_array[end_date] == 0.07790

    # ----------------------------------
    def test_get_consumption_price_array_after(self):

        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 5)

        consumption_price_array = self._pricer.get_consumption_price_array(start_date=start_date, end_date=end_date)

        assert consumption_price_array.start_date == start_date
        assert consumption_price_array.end_date == end_date
        assert consumption_price_array.price_unit == "€"
        assert consumption_price_array.quantity_unit == "kWh"
        assert consumption_price_array.vat_id == "reduced"
        assert len(consumption_price_array.price_array) == 5
        assert consumption_price_array.price_array[start_date] == 0.07807
        assert consumption_price_array.price_array[end_date] == 0.07807
