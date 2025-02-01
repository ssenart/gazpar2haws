import calendar
from datetime import date, timedelta

from gazpar2haws.model import (ConsumptionPriceArray, ConsumptionQuantityArray,
                               CostArray, EnergyTaxesPriceArray, Value,
                               ValueArray, PriceUnit, Pricing, QuantityUnit,
                               SubscriptionPriceArray, TimeUnit,
                               TransportPriceArray, VatRate, VatRateArray, PriceValue, ValueUnit, BaseUnit)

from typing import Optional, Tuple, overload


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
    def get_vat_rate_array_by_id(self, start_date: date, end_date: date) -> dict[str, VatRateArray]:

        if self._pricing.vat is None or len(self._pricing.vat) == 0:
            raise ValueError("self._pricing.vat is None or empty")

        res = dict[str, VatRateArray]()
        vat_rate_by_id = dict[str, list[VatRate]]()
        for vat_rate in self._pricing.vat:
            res[vat_rate.id] = VatRateArray(
                id=vat_rate.id,
                start_date=start_date,
                end_date=end_date
            )
            if vat_rate.id not in vat_rate_by_id:
                vat_rate_by_id[vat_rate.id] = list[VatRate]()
            vat_rate_by_id[vat_rate.id].append(vat_rate)

        for vat_id, vat_rates in vat_rate_by_id.items():
            self._fill_value_array(res[vat_id], vat_rates)  # type: ignore

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
            base_unit=first_consumption_price.base_unit,
            vat_id=first_consumption_price.vat_id
        )

        self._fill_value_array(res, self._pricing.consumption_prices)  # type: ignore

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
            base_unit=first_subscription_price.base_unit,
            vat_id=first_subscription_price.vat_id
        )

        self._fill_value_array(res, self._pricing.subscription_prices)  # type: ignore

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
            base_unit=first_transport_price.base_unit,
            vat_id=first_transport_price.vat_id
        )

        self._fill_value_array(res, self._pricing.transport_prices)  # type: ignore

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
            base_unit=first_energy_taxes_price.base_unit,
            vat_id=first_energy_taxes_price.vat_id
        )

        self._fill_value_array(res, self._pricing.energy_taxes)  # type: ignore

        return res

    # ----------------------------------
    def _fill_value_array(self, out_value_array: ValueArray, in_values: list[Value]) -> None:

        if out_value_array is None:
            raise ValueError("out_value_array is None")

        if out_value_array.start_date is None:
            raise ValueError("out_value_array.start_date is None")

        start_date = out_value_array.start_date

        if out_value_array.end_date is None:
            raise ValueError("out_value_array.end_date is None")

        end_date = out_value_array.end_date

        if out_value_array.value_array is None:
            raise ValueError("out_value_array.value_array is None")

        value_array = out_value_array.value_array

        if in_values is None or len(in_values) == 0:
            raise ValueError("in_values is None or empty")

        first_value = in_values[0]
        last_value = in_values[-1]

        if first_value.start_date > end_date:
            # Fully before first value period.
            value_array[start_date:end_date] = first_value.value  # type: ignore
        elif last_value.end_date is not None and last_value.end_date < start_date:
            # Fully after last value period.
            value_array[start_date:end_date] = last_value.value  # type: ignore
        else:
            if start_date < first_value.start_date:
                # Partially before first value period.
                value_array[start_date:first_value.start_date] = first_value.value  # type: ignore
            if last_value.end_date is not None and end_date > last_value.end_date:
                # Partially after last value period.
                value_array[last_value.end_date:end_date] = last_value.value  # type: ignore
            # Inside value periods.
            for value in in_values:
                latest_start = max(value.start_date, start_date)
                earliest_end = min(value.end_date if value.end_date is not None else end_date, end_date)
                current_date = latest_start
                while current_date <= earliest_end:
                    value_array[current_date] = value.value
                    current_date += timedelta(days=1)

    # ----------------------------------
    def get_time_unit_convertion_factor(self, from_time_unit: TimeUnit, to_time_unit: TimeUnit, dt: date) -> float:

        if from_time_unit == to_time_unit:
            return 1.0

        def days_in_month(year: int, month: int) -> int:
            return calendar.monthrange(year, month)[1]

        def days_in_year(year: int) -> int:
            return 366 if calendar.isleap(year) else 365

        if from_time_unit == TimeUnit.MONTH or to_time_unit == TimeUnit.MONTH:
            switcher = {
                TimeUnit.DAY: 1.0 / days_in_month(dt.year, dt.month),
                TimeUnit.WEEK: 7.0 / days_in_month(dt.year, dt.month),
                TimeUnit.MONTH: 1.0,
                TimeUnit.YEAR: 12.0,
            }
        else:
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

        return switcher[to_time_unit] / switcher[from_time_unit]

    # ----------------------------------
    def get_price_unit_convertion_factor(self, from_price_unit: PriceUnit, to_price_unit: PriceUnit) -> float:

        if from_price_unit == to_price_unit:
            return 1.0

        switcher = {
            PriceUnit.EURO: 1.0,
            PriceUnit.CENT: 100.0,
        }

        if from_price_unit not in switcher:
            raise ValueError(f"from_price_unit {from_price_unit} not in switcher")

        if to_price_unit not in switcher:
            raise ValueError(f"to_price_unit {to_price_unit} not in switcher")

        return switcher[to_price_unit] / switcher[from_price_unit]

    # ----------------------------------
    def get_quantity_unit_convertion_factor(self, from_quantity_unit: QuantityUnit, to_quantity_unit: QuantityUnit) -> float:

        if from_quantity_unit == to_quantity_unit:
            return 1.0

        switcher = {
            QuantityUnit.WH: 1.0,
            QuantityUnit.KWH: 1000.0,
            QuantityUnit.MWH: 1000000.0,
        }

        if from_quantity_unit not in switcher:
            raise ValueError(f"from_quantity_unit {from_quantity_unit} not in switcher")

        if to_quantity_unit not in switcher:
            raise ValueError(f"to_quantity_unit {to_quantity_unit} not in switcher")

        return switcher[to_quantity_unit] / switcher[from_quantity_unit]

    # ----------------------------------
    @overload
    def get_convertion_factor(self, from_unit: Tuple[PriceUnit, QuantityUnit], to_unit: Tuple[PriceUnit, QuantityUnit], dt: Optional[date] = None) -> float:
        ...

    @overload
    def get_convertion_factor(self, from_unit: Tuple[PriceUnit, TimeUnit], to_unit: Tuple[PriceUnit, TimeUnit], dt: Optional[date] = None) -> float:
        ...

    def get_convertion_factor(self, from_unit, to_unit, dt: Optional[date] = None) -> float:
        if type(from_unit) is not type(to_unit):
            raise ValueError(f"from_unit {from_unit} and to_unit {to_unit} must be of the same type")
        if isinstance(from_unit, tuple) and isinstance(from_unit[0], PriceUnit) and isinstance(from_unit[1], QuantityUnit):
            return self.get_price_unit_convertion_factor(from_unit[0], to_unit[0]) * self.get_quantity_unit_convertion_factor(from_unit[1], to_unit[1])
        elif isinstance(from_unit, tuple) and isinstance(from_unit[0], PriceUnit) and isinstance(from_unit[1], TimeUnit):
            if dt is None:
                raise ValueError(f"dt must not be None when from_unit {from_unit} and to_unit {to_unit} are of type Tuple[PriceUnit, TimeUnit]")
            return self.get_price_unit_convertion_factor(from_unit[0], to_unit[0]) * self.get_time_unit_convertion_factor(from_unit[1], to_unit[1], dt)
        else:
            raise ValueError(f"from_unit {from_unit} and to_unit {to_unit} must be of type Tuple[PriceUnit, QuantityUnit] or Tuple[PriceUnit, TimeUnit]")
