import calendar
from datetime import date, timedelta

from gazpar2haws.model import (
    ConsumptionPriceArray,
    ConsumptionQuantityArray,
    CostArray,
    EnergyTaxesPriceArray,
    Value,
    ValueArray,
    PriceUnit,
    Pricing,
    QuantityUnit,
    SubscriptionPriceArray,
    TimeUnit,
    TransportPriceArray,
    VatRate,
    VatRateArray,
    PriceValue,
    ValueUnit,
    BaseUnit
)

from typing import Optional, Tuple, overload


class Pricer:

    # ----------------------------------
    def __init__(self, pricing: Pricing):
        self._pricing = pricing

    # ----------------------------------
    def pricing_data(self) -> Pricing:
        return self._pricing

    # ----------------------------------
    def compute(self, quantities: ConsumptionQuantityArray, price_unit: PriceUnit) -> CostArray:

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

        # Convert all pricing data to the same unit as the quantities.
        consumption_prices = Pricer.convert(self._pricing.consumption_prices, (price_unit, quantities.quantity_unit))
        subscription_prices = Pricer.convert(self._pricing.subscription_prices, (price_unit, TimeUnit.DAY))
        transport_prices = Pricer.convert(self._pricing.transport_prices, (price_unit, TimeUnit.DAY))
        energy_taxes = Pricer.convert(self._pricing.energy_taxes, (price_unit, quantities.quantity_unit))

        # Transform to the vectorized form.
        vat_rate_array_by_id = self.get_vat_rate_array_by_id(
            start_date=start_date, end_date=end_date, vat_rates=self._pricing.vat
        )

        consumption_price_array = self.get_consumption_price_array(
            start_date=start_date, end_date=end_date, consumption_prices=consumption_prices
        )

        subscription_price_array = self.get_subscription_price_array(
            start_date=start_date, end_date=end_date, subscription_prices=subscription_prices
        )

        transport_price_array = self.get_transport_price_array(
            start_date=start_date, end_date=end_date, transport_prices=transport_prices
        )

        energy_taxes_price_array = self.get_energy_taxes_price_array(
            start_date=start_date, end_date=end_date, energy_taxes_prices=energy_taxes
        )

        res = CostArray(
            start_date=start_date,
            end_date=end_date,
            cost_unit=price_unit,
        )

        res.cost_array = quantity_array * (consumption_price_array.value_array + energy_taxes_price_array.value_array) + subscription_price_array.value_array + transport_price_array.value_array  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_vat_rate_array_by_id(
        cls, start_date: date, end_date: date, vat_rates: list[VatRate]
    ) -> dict[str, VatRateArray]:

        if vat_rates is None or len(vat_rates) == 0:
            raise ValueError("vat_rates is None or empty")

        res = dict[str, VatRateArray]()
        vat_rate_by_id = dict[str, list[VatRate]]()
        for vat_rate in vat_rates:
            res[vat_rate.id] = VatRateArray(
                id=vat_rate.id, start_date=start_date, end_date=end_date
            )
            if vat_rate.id not in vat_rate_by_id:
                vat_rate_by_id[vat_rate.id] = list[VatRate]()
            vat_rate_by_id[vat_rate.id].append(vat_rate)

        for vat_id, vat_rates in vat_rate_by_id.items():
            cls._fill_value_array(res[vat_id], vat_rates)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_consumption_price_array(
        cls, start_date: date, end_date: date, consumption_prices: list[PriceValue[PriceUnit, QuantityUnit]]
    ) -> ConsumptionPriceArray:

        if (
            consumption_prices is None or len(consumption_prices) == 0
        ):
            raise ValueError("consumption_prices is None or empty")

        first_consumption_price = consumption_prices[0]

        res = ConsumptionPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_consumption_price.price_unit,
            base_unit=first_consumption_price.base_unit,
            vat_id=first_consumption_price.vat_id,
        )

        cls._fill_value_array(res, consumption_prices)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_subscription_price_array(
        cls, start_date: date, end_date: date, subscription_prices: list[PriceValue[PriceUnit, TimeUnit]]
    ) -> SubscriptionPriceArray:

        if (
            subscription_prices is None or len(subscription_prices) == 0
        ):
            raise ValueError("subscription_prices is None or empty")

        first_subscription_price = subscription_prices[0]

        res = SubscriptionPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_subscription_price.price_unit,
            base_unit=first_subscription_price.base_unit,
            vat_id=first_subscription_price.vat_id,
        )

        cls._fill_value_array(res, subscription_prices)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_transport_price_array(
        cls, start_date: date, end_date: date, transport_prices: list[PriceValue[PriceUnit, TimeUnit]]
    ) -> TransportPriceArray:

        if (
            transport_prices is None or len(transport_prices) == 0
        ):
            raise ValueError("transport_prices is None or empty")

        first_transport_price = transport_prices[0]

        res = TransportPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_transport_price.price_unit,
            base_unit=first_transport_price.base_unit,
            vat_id=first_transport_price.vat_id,
        )

        cls._fill_value_array(res, transport_prices)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_energy_taxes_price_array(
        cls, start_date: date, end_date: date, energy_taxes_prices: list[PriceValue[PriceUnit, QuantityUnit]]
    ) -> EnergyTaxesPriceArray:

        if energy_taxes_prices is None or len(energy_taxes_prices) == 0:
            raise ValueError("energy_taxes_prices is None or empty")

        first_energy_taxes_price = energy_taxes_prices[0]

        res = EnergyTaxesPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_energy_taxes_price.price_unit,
            base_unit=first_energy_taxes_price.base_unit,
            vat_id=first_energy_taxes_price.vat_id,
        )

        cls._fill_value_array(res, energy_taxes_prices)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def _fill_value_array(
        cls, out_value_array: ValueArray, in_values: list[Value]
    ) -> None:

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
                earliest_end = min(
                    value.end_date if value.end_date is not None else end_date, end_date
                )
                current_date = latest_start
                while current_date <= earliest_end:
                    value_array[current_date] = value.value
                    current_date += timedelta(days=1)

    # ----------------------------------
    @classmethod
    def get_time_unit_convertion_factor(
        cls, from_time_unit: TimeUnit, to_time_unit: TimeUnit, dt: date
    ) -> float:

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
    @classmethod
    def get_price_unit_convertion_factor(
        cls, from_price_unit: PriceUnit, to_price_unit: PriceUnit
    ) -> float:

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
    @classmethod
    def get_quantity_unit_convertion_factor(
        cls, from_quantity_unit: QuantityUnit, to_quantity_unit: QuantityUnit
    ) -> float:

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
    @classmethod
    def get_convertion_factor(
        cls,
        from_unit: Tuple[PriceUnit, QuantityUnit],
        to_unit: Tuple[PriceUnit, QuantityUnit],
        dt: Optional[date] = None,
    ) -> float:
        ...

    @overload
    @classmethod
    def get_convertion_factor(
        cls,
        from_unit: Tuple[PriceUnit, TimeUnit],
        to_unit: Tuple[PriceUnit, TimeUnit],
        dt: Optional[date] = None,
    ) -> float:
        ...

    @classmethod
    def get_convertion_factor(
        cls, from_unit, to_unit, dt: Optional[date] = None
    ) -> float:
        if type(from_unit) is not type(to_unit):
            raise ValueError(
                f"from_unit {from_unit} and to_unit {to_unit} must be of the same type"
            )
        if (
            isinstance(from_unit, tuple) and isinstance(from_unit[0], PriceUnit) and isinstance(from_unit[1], QuantityUnit)
        ):
            return cls.get_price_unit_convertion_factor(
                from_unit[0], to_unit[0]
            ) * cls.get_quantity_unit_convertion_factor(from_unit[1], to_unit[1])
        if (
            isinstance(from_unit, tuple) and isinstance(from_unit[0], PriceUnit) and isinstance(from_unit[1], TimeUnit)
        ):
            if dt is None:
                raise ValueError(
                    f"dt must not be None when from_unit {from_unit} and to_unit {to_unit} are of type Tuple[PriceUnit, TimeUnit]"
                )
            return cls.get_price_unit_convertion_factor(
                from_unit[0], to_unit[0]
            ) * cls.get_time_unit_convertion_factor(from_unit[1], to_unit[1], dt)

        raise ValueError(
            f"from_unit {from_unit} and to_unit {to_unit} must be of type Tuple[PriceUnit, QuantityUnit] or Tuple[PriceUnit, TimeUnit]"
        )

    # ----------------------------------
    @classmethod
    def convert(cls, price_values: list[PriceValue[ValueUnit, BaseUnit]], to_unit: Tuple[ValueUnit, BaseUnit]) -> list[PriceValue[ValueUnit, BaseUnit]]:

        if price_values is None or len(price_values) == 0:
            raise ValueError("price_values is None or empty")

        if to_unit is None:
            raise ValueError("to_unit is None")

        res = list[PriceValue[ValueUnit, BaseUnit]]()
        for price_value in price_values:
            if price_value.price_unit is None:
                raise ValueError("price_value.price_unit is None")
            if price_value.base_unit is None:
                raise ValueError("price_value.base_unit is None")

            res.append(
                PriceValue(
                    start_date=price_value.start_date,
                    end_date=price_value.end_date,
                    value=price_value.value * cls.get_convertion_factor(
                        (price_value.price_unit, price_value.base_unit), to_unit, price_value.start_date  # type: ignore
                    ),
                    price_unit=to_unit[0],
                    base_unit=to_unit[1],
                    vat_id=price_value.vat_id,
                )
            )

        return res
