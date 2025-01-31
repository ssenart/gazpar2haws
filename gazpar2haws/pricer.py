import calendar
from datetime import date, timedelta

from gazpar2haws.model import (ConsumptionPriceArray, ConsumptionQuantityArray,
                               CostArray, EnergyTaxesPriceArray, Price,
                               PriceArray, PriceUnit, Pricing, QuantityUnit,
                               SubscriptionPriceArray, TimeUnit,
                               TransportPriceArray)


class Pricer:

    # ----------------------------------
    def __init__(self, pricing: Pricing):
        self._pricing = pricing

    # ----------------------------------
    def compute(self, quantities: ConsumptionQuantityArray) -> CostArray:

        if quantities is None:
            raise ValueError("quantities is None")

        if quantities.start_date is None:
            raise ValueError("quantities.start_date is None")

        start_date = quantities.start_date

        if quantities.end_date is None:
            raise ValueError("quantities.end_date is None")

        end_date = quantities.end_date

        if quantities.quantity_array is None:
            raise ValueError("quantities.quantity_array is None")

        quantity_array = quantities.quantity_array

        consumption_price_array = self.get_consumption_price_array(start_date=start_date, end_date=end_date)

        subscription_price_array = self.get_subscription_price_array(start_date=start_date, end_date=end_date)

        transport_price_array = self.get_transport_price_array(start_date=start_date, end_date=end_date)

        energy_taxes_price_array = self.get_energy_taxes_price_array(start_date=start_date, end_date=end_date)

        res = CostArray(
            start_date=start_date,
            end_date=end_date,
            cost_unit=consumption_price_array.price_unit,
        )

        res.cost_array = quantity_array * (consumption_price_array.price_array + energy_taxes_price_array.price_array) + subscription_price_array.price_array + transport_price_array.price_array  # type: ignore

        return res

    # ----------------------------------
    def get_consumption_price_array(self, start_date: date, end_date: date) -> ConsumptionPriceArray:

        if self._pricing.consumption_prices is None or len(self._pricing.consumption_prices) == 0:
            raise ValueError("self._pricing.consumption_prices is None or empty")

        first_consumption_price = self._pricing.consumption_prices[0]

        res = ConsumptionPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_consumption_price.price_unit,
            quantity_unit=first_consumption_price.quantity_unit,
            vat_id=first_consumption_price.vat_id
        )

        self._fill_price_array(res, self._pricing.consumption_prices)  # type: ignore

        return res

    # ----------------------------------
    def get_subscription_price_array(self, start_date: date, end_date: date) -> SubscriptionPriceArray:

        if self._pricing.subscription_prices is None or len(self._pricing.subscription_prices) == 0:
            raise ValueError("self._pricing.subscription_prices is None or empty")

        first_subscription_price = self._pricing.subscription_prices[0]

        res = SubscriptionPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_subscription_price.price_unit,
            time_unit=first_subscription_price.time_unit,
            vat_id=first_subscription_price.vat_id
        )

        self._fill_price_array(res, self._pricing.subscription_prices)  # type: ignore

        return res

    # ----------------------------------
    def get_transport_price_array(self, start_date: date, end_date: date) -> TransportPriceArray:

        if self._pricing.transport_prices is None or len(self._pricing.transport_prices) == 0:
            raise ValueError("self._pricing.transport_prices is None or empty")

        first_transport_price = self._pricing.transport_prices[0]

        res = TransportPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_transport_price.price_unit,
            time_unit=first_transport_price.time_unit,
            vat_id=first_transport_price.vat_id
        )

        self._fill_price_array(res, self._pricing.transport_prices)  # type: ignore

        return res

    # ----------------------------------
    def get_energy_taxes_price_array(self, start_date: date, end_date: date) -> EnergyTaxesPriceArray:

        if self._pricing.energy_taxes is None or len(self._pricing.energy_taxes) == 0:
            raise ValueError("self._pricing.energy_taxes is None or empty")

        first_energy_taxes_price = self._pricing.energy_taxes[0]

        res = EnergyTaxesPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_energy_taxes_price.price_unit,
            quantity_unit=first_energy_taxes_price.quantity_unit,
            vat_id=first_energy_taxes_price.vat_id
        )

        self._fill_price_array(res, self._pricing.energy_taxes)  # type: ignore

        return res

    # ----------------------------------
    def _fill_price_array(self, out_price_array: PriceArray, in_prices: list[Price]) -> None:

        if out_price_array is None:
            raise ValueError("out_price_array is None")

        if out_price_array.start_date is None:
            raise ValueError("out_price_array.start_date is None")

        start_date = out_price_array.start_date

        if out_price_array.end_date is None:
            raise ValueError("out_price_array.end_date is None")

        end_date = out_price_array.end_date

        if out_price_array.price_array is None:
            raise ValueError("out_price_array.price_array is None")

        price_array = out_price_array.price_array

        if in_prices is None or len(in_prices) == 0:
            raise ValueError("in_prices is None or empty")

        first_price = in_prices[0]
        last_price = in_prices[-1]

        if first_price.start_date > end_date:
            # Fully before first price period.
            price_array[start_date:end_date] = first_price.price  # type: ignore
        elif last_price.end_date is not None and last_price.end_date < start_date:
            # Fully after last price period.
            price_array[start_date:end_date] = last_price.price  # type: ignore
        else:
            if start_date < first_price.start_date:
                # Partially before first price period.
                price_array[start_date:first_price.start_date] = first_price.price  # type: ignore
            if last_price.end_date is not None and end_date > last_price.end_date:
                # Partially after last price period.
                price_array[last_price.end_date:end_date] = last_price.price  # type: ignore
            # Inside price periods.
            for price in in_prices:
                latest_start = max(price.start_date, start_date)
                earliest_end = min(price.end_date if price.end_date is not None else end_date, end_date)
                current_date = latest_start
                while current_date <= earliest_end:
                    price_array[current_date] = price.price
                    current_date += timedelta(days=1)

    # ----------------------------------
    def convert_price_with_price_unit(self, price: float, from_price_unit: PriceUnit, to_price_unit: PriceUnit) -> float:

        if from_price_unit == to_price_unit:
            return price

        switcher = {
            PriceUnit.EURO: 1.0,
            PriceUnit.CENT: 100.0,
        }

        if from_price_unit not in switcher:
            raise ValueError(f"from_price_unit {from_price_unit} not in switcher")

        if to_price_unit not in switcher:
            raise ValueError(f"to_price_unit {to_price_unit} not in switcher")

        return price * switcher.get(from_price_unit) / switcher.get(to_price_unit)

    # ----------------------------------
    def convert_quantity(self, quantity: float, from_quantity_unit: QuantityUnit, to_quantity_unit: QuantityUnit) -> float:

        if from_quantity_unit == to_quantity_unit:
            return quantity

        switcher = {
            QuantityUnit.WH: 1.0,
            QuantityUnit.KWH: 1000.0,
            QuantityUnit.MWH: 1000000.0,
        }

        if from_quantity_unit not in switcher:
            raise ValueError(f"from_quantity_unit {from_quantity_unit} not in switcher")

        if to_quantity_unit not in switcher:
            raise ValueError(f"to_quantity_unit {to_quantity_unit} not in switcher")

        return quantity * switcher.get(from_quantity_unit) / switcher.get(to_quantity_unit)

    # ----------------------------------
    def convert_price_with_time_unit(self, price: float, from_time_unit: TimeUnit, to_time_unit: TimeUnit, dt: date) -> float:

        if from_time_unit == to_time_unit:
            return price

        def days_in_month(year: int, month: int) -> int:
            return calendar.monthrange(year, month)[1]

        def days_in_year(year: int) -> int:
            return 366 if calendar.isleap(year) else 365

        switcher = {
            TimeUnit.DAY: 1.0,
            TimeUnit.WEEK: 7.0,
            TimeUnit.MONTH: days_in_month(dt.year, dt.month),
            TimeUnit.YEAR: days_in_year(dt.year),
        }

        if from_time_unit not in switcher:
            raise ValueError(f"from_time_unit {from_time_unit} not in switcher")

        if to_time_unit not in switcher:
            raise ValueError(f"to_time_unit {to_time_unit} not in switcher")

        return price * switcher[from_time_unit] / switcher[to_time_unit]