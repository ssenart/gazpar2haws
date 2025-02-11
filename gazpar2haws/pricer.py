import calendar
from datetime import date, timedelta
from typing import Optional, Tuple, overload

from gazpar2haws.model import (
    BaseUnit,
    ConsumptionPriceArray,
    ConsumptionQuantityArray,
    CostArray,
    EnergyTaxesPriceArray,
    PriceUnit,
    PriceValue,
    Pricing,
    QuantityUnit,
    SubscriptionPriceArray,
    TimeUnit,
    TransportPriceArray,
    Value,
    ValueArray,
    ValueUnit,
    VatRate,
    VatRateArray,
)


class Pricer:

    # ----------------------------------
    def __init__(self, pricing: Pricing):
        self._pricing = pricing

    # ----------------------------------
    def pricing_data(self) -> Pricing:
        return self._pricing

    # ----------------------------------
    def compute(  # pylint: disable=too-many-branches
        self, quantities: ConsumptionQuantityArray, price_unit: PriceUnit
    ) -> CostArray:

        if quantities is None:
            raise ValueError("quantities is None")

        if quantities.start_date is None:
            raise ValueError("quantities.start_date is None")

        start_date = quantities.start_date

        if quantities.end_date is None:
            raise ValueError("quantities.end_date is None")

        end_date = quantities.end_date

        if quantities.value_array is None:
            raise ValueError("quantities.value_array is None")

        if quantities.value_unit is None:
            raise ValueError("quantities.value_unit is None")

        if quantities.base_unit is None:
            raise ValueError("quantities.base_unit is None")

        quantity_array = quantities.value_array

        # Convert all pricing data to the same unit as the quantities.
        consumption_prices = Pricer.convert(self._pricing.consumption_prices, (price_unit, quantities.value_unit))

        if self._pricing.subscription_prices is not None and len(self._pricing.subscription_prices) > 0:
            subscription_prices = Pricer.convert(self._pricing.subscription_prices, (price_unit, quantities.base_unit))
        else:
            subscription_prices = None

        if self._pricing.transport_prices is not None and len(self._pricing.transport_prices) > 0:
            transport_prices = Pricer.convert(self._pricing.transport_prices, (price_unit, quantities.base_unit))
        else:
            transport_prices = None

        if self._pricing.energy_taxes is not None and len(self._pricing.energy_taxes) > 0:
            energy_taxes = Pricer.convert(self._pricing.energy_taxes, (price_unit, quantities.value_unit))
        else:
            energy_taxes = None

        # Transform to the vectorized form.
        if self._pricing.vat is not None and len(self._pricing.vat) > 0:
            vat_rate_array_by_id = self.get_vat_rate_array_by_id(
                start_date=start_date, end_date=end_date, vat_rates=self._pricing.vat
            )
        else:
            vat_rate_array_by_id = dict[str, VatRateArray]()

        consumption_price_array = self.get_consumption_price_array(
            start_date=start_date,
            end_date=end_date,
            consumption_prices=consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
        )

        # Subscription price is optional.
        if subscription_prices is not None and len(subscription_prices) > 0:
            subscription_price_array = self.get_subscription_price_array(
                start_date=start_date,
                end_date=end_date,
                subscription_prices=subscription_prices,
                vat_rate_array_by_id=vat_rate_array_by_id,
            )
        else:
            subscription_price_array = SubscriptionPriceArray(
                name="subscription_prices",
                start_date=start_date,
                end_date=end_date,
                value_unit=price_unit,
                base_unit=quantities.base_unit,
            )

        # Transport price is optional.
        if transport_prices is not None and len(transport_prices) > 0:
            transport_price_array = self.get_transport_price_array(
                start_date=start_date,
                end_date=end_date,
                transport_prices=transport_prices,
                vat_rate_array_by_id=vat_rate_array_by_id,
            )
        else:
            transport_price_array = TransportPriceArray(
                name="transport_prices",
                start_date=start_date,
                end_date=end_date,
                value_unit=price_unit,
                base_unit=quantities.base_unit,
            )

        # Energy taxes are optional.
        if energy_taxes is not None and len(energy_taxes) > 0:
            energy_taxes_price_array = self.get_energy_taxes_price_array(
                start_date=start_date,
                end_date=end_date,
                energy_taxes_prices=energy_taxes,
                vat_rate_array_by_id=vat_rate_array_by_id,
            )
        else:
            energy_taxes_price_array = EnergyTaxesPriceArray(
                name="energy_taxes",
                start_date=start_date,
                end_date=end_date,
                value_unit=price_unit,
                base_unit=quantities.value_unit,
            )

        res = CostArray(
            name="costs",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )

        # Compute pricing formula
        res.value_array = quantity_array * (consumption_price_array.value_array + energy_taxes_price_array.value_array) + subscription_price_array.value_array + transport_price_array.value_array  # type: ignore

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
            res[vat_rate.id] = VatRateArray(name="vats", id=vat_rate.id, start_date=start_date, end_date=end_date)
            if vat_rate.id not in vat_rate_by_id:
                vat_rate_by_id[vat_rate.id] = list[VatRate]()
            vat_rate_by_id[vat_rate.id].append(vat_rate)

        for vat_id, vat_rate_list in vat_rate_by_id.items():
            cls._fill_value_array(res[vat_id], vat_rate_list)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_consumption_price_array(
        cls,
        start_date: date,
        end_date: date,
        consumption_prices: list[PriceValue[PriceUnit, QuantityUnit]],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> ConsumptionPriceArray:

        if consumption_prices is None or len(consumption_prices) == 0:
            raise ValueError("consumption_prices is None or empty")

        first_consumption_price = consumption_prices[0]

        res = ConsumptionPriceArray(
            name="consumption_prices",
            start_date=start_date,
            end_date=end_date,
            value_unit=first_consumption_price.value_unit,
            base_unit=first_consumption_price.base_unit,
            vat_id=first_consumption_price.vat_id,
        )

        cls._fill_price_array(res, consumption_prices, vat_rate_array_by_id)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_subscription_price_array(
        cls,
        start_date: date,
        end_date: date,
        subscription_prices: list[PriceValue[PriceUnit, TimeUnit]],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> SubscriptionPriceArray:

        if subscription_prices is None or len(subscription_prices) == 0:
            raise ValueError("subscription_prices is None or empty")

        first_subscription_price = subscription_prices[0]

        res = SubscriptionPriceArray(
            name="subscription_prices",
            start_date=start_date,
            end_date=end_date,
            value_unit=first_subscription_price.value_unit,
            base_unit=first_subscription_price.base_unit,
            vat_id=first_subscription_price.vat_id,
        )

        cls._fill_price_array(res, subscription_prices, vat_rate_array_by_id)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_transport_price_array(
        cls,
        start_date: date,
        end_date: date,
        transport_prices: list[PriceValue[PriceUnit, TimeUnit]],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> TransportPriceArray:

        if transport_prices is None or len(transport_prices) == 0:
            raise ValueError("transport_prices is None or empty")

        first_transport_price = transport_prices[0]

        res = TransportPriceArray(
            name="transport_prices",
            start_date=start_date,
            end_date=end_date,
            value_unit=first_transport_price.value_unit,
            base_unit=first_transport_price.base_unit,
            vat_id=first_transport_price.vat_id,
        )

        cls._fill_price_array(res, transport_prices, vat_rate_array_by_id)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def get_energy_taxes_price_array(
        cls,
        start_date: date,
        end_date: date,
        energy_taxes_prices: list[PriceValue[PriceUnit, QuantityUnit]],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> EnergyTaxesPriceArray:

        if energy_taxes_prices is None or len(energy_taxes_prices) == 0:
            raise ValueError("energy_taxes_prices is None or empty")

        first_energy_taxes_price = energy_taxes_prices[0]

        res = EnergyTaxesPriceArray(
            name="energy_taxes",
            start_date=start_date,
            end_date=end_date,
            value_unit=first_energy_taxes_price.value_unit,
            base_unit=first_energy_taxes_price.base_unit,
            vat_id=first_energy_taxes_price.vat_id,
        )

        cls._fill_price_array(res, energy_taxes_prices, vat_rate_array_by_id)  # type: ignore

        return res

    # ----------------------------------
    @classmethod
    def _fill_value_array(cls, out_value_array: ValueArray, in_values: list[Value]) -> None:

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
            value_array[start_date : end_date + timedelta(1)] = first_value.value  # type: ignore
        elif last_value.end_date is not None and last_value.end_date < start_date:
            # Fully after last value period.
            value_array[start_date : end_date + timedelta(1)] = last_value.value  # type: ignore
        else:
            if start_date < first_value.start_date:
                # Partially before first value period.
                value_array[start_date : first_value.start_date + timedelta(1)] = first_value.value  # type: ignore
            if last_value.end_date is not None and end_date > last_value.end_date:
                # Partially after last value period.
                value_array[last_value.end_date : end_date + timedelta(1)] = last_value.value  # type: ignore
            # Inside value periods.
            for value in in_values:
                latest_start = max(value.start_date, start_date)
                earliest_end = min(value.end_date if value.end_date is not None else end_date, end_date)
                current_date = latest_start
                while current_date <= earliest_end:
                    value_array[current_date] = value.value
                    current_date += timedelta(days=1)

    # ----------------------------------
    @classmethod
    def _fill_price_array(  # pylint: disable=too-many-branches
        cls,
        out_value_array: ValueArray,
        in_values: list[PriceValue],
        vat_rate_array_by_id: dict[str, VatRateArray],
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
            if vat_rate_array_by_id is not None and first_value.vat_id in vat_rate_array_by_id:
                vat_value = vat_rate_array_by_id[first_value.vat_id].value_array[start_date : end_date + timedelta(1)]  # type: ignore
            else:
                vat_value = 0.0
            value_array[start_date : end_date + timedelta(1)] = (vat_value + 1) * first_value.value  # type: ignore
        elif last_value.end_date is not None and last_value.end_date < start_date:
            # Fully after last value period.
            if vat_rate_array_by_id is not None and last_value.vat_id in vat_rate_array_by_id:
                vat_value = vat_rate_array_by_id[last_value.vat_id].value_array[start_date : end_date + timedelta(1)]  # type: ignore
            else:
                vat_value = 0.0
            value_array[start_date : end_date + timedelta(1)] = (vat_value + 1) * last_value.value  # type: ignore
        else:
            if start_date < first_value.start_date:
                # Partially before first value period.
                if vat_rate_array_by_id is not None and first_value.vat_id in vat_rate_array_by_id:
                    vat_value = vat_rate_array_by_id[first_value.vat_id].value_array[start_date : first_value.start_date + timedelta(1)]  # type: ignore
                else:
                    vat_value = 0.0
                value_array[start_date : first_value.start_date + timedelta(1)] = (vat_value + 1) * first_value.value  # type: ignore
            if last_value.end_date is not None and end_date > last_value.end_date:
                # Partially after last value period.
                if vat_rate_array_by_id is not None and last_value.vat_id in vat_rate_array_by_id:
                    vat_value = vat_rate_array_by_id[last_value.vat_id].value_array[last_value.end_date : end_date + timedelta(1)]  # type: ignore
                else:
                    vat_value = 0.0
                value_array[last_value.end_date : end_date + timedelta(1)] = (vat_value + 1) * last_value.value  # type: ignore
            # Inside value periods.
            for value in in_values:
                latest_start = max(value.start_date, start_date)
                earliest_end = min(value.end_date if value.end_date is not None else end_date, end_date)
                current_date = latest_start
                while current_date <= earliest_end:
                    if vat_rate_array_by_id is not None and value.vat_id in vat_rate_array_by_id:
                        vat_value = vat_rate_array_by_id[value.vat_id].value_array[current_date]  # type: ignore
                    else:
                        vat_value = 0.0
                    value_array[current_date] = (vat_value + 1) * value.value  # type: ignore
                    current_date += timedelta(days=1)

    # ----------------------------------
    @classmethod
    def get_time_unit_convertion_factor(cls, from_time_unit: TimeUnit, to_time_unit: TimeUnit, dt: date) -> float:

        if from_time_unit == to_time_unit:
            return 1.0

        def days_in_month(year: int, month: int) -> int:
            return calendar.monthrange(year, month)[1]

        def days_in_year(year: int) -> int:
            return 366 if calendar.isleap(year) else 365

        if TimeUnit.MONTH in (from_time_unit, to_time_unit):
            switcher = {
                TimeUnit.DAY: days_in_month(dt.year, dt.month),
                TimeUnit.WEEK: days_in_month(dt.year, dt.month) / 7.0,
                TimeUnit.MONTH: 1.0,
                TimeUnit.YEAR: 1.0 / 12.0,
            }
        else:
            switcher = {
                TimeUnit.DAY: 1.0,
                TimeUnit.WEEK: 1 / 7.0,
                TimeUnit.MONTH: 1 / days_in_month(dt.year, dt.month),
                TimeUnit.YEAR: 1 / days_in_year(dt.year),
            }

        if from_time_unit not in switcher:
            raise ValueError(f"Invalid 'from' time unit: {from_time_unit}")

        if to_time_unit not in switcher:
            raise ValueError(f"Invalid 'to' time unit: {to_time_unit}")

        return switcher[to_time_unit] / switcher[from_time_unit]

    # ----------------------------------
    @classmethod
    def get_price_unit_convertion_factor(cls, from_price_unit: PriceUnit, to_price_unit: PriceUnit) -> float:

        if from_price_unit == to_price_unit:
            return 1.0

        switcher = {
            PriceUnit.EURO: 1.0,
            PriceUnit.CENT: 100.0,
        }

        if from_price_unit not in switcher:
            raise ValueError(f"Invalid 'from' price unit: {from_price_unit}")

        if to_price_unit not in switcher:
            raise ValueError(f"Invalid 'to' price unit: {to_price_unit}")

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
            QuantityUnit.KWH: 0.001,
            QuantityUnit.MWH: 0.000001,
        }

        if from_quantity_unit not in switcher:
            raise ValueError(f"Invalid 'from' quantity unit: {from_quantity_unit}")

        if to_quantity_unit not in switcher:
            raise ValueError(f"Invalid 'to' quantity unit: {to_quantity_unit}")

        return switcher[to_quantity_unit] / switcher[from_quantity_unit]

    # ----------------------------------
    @overload
    @classmethod
    def get_convertion_factor(
        cls,
        from_unit: Tuple[PriceUnit, QuantityUnit],
        to_unit: Tuple[PriceUnit, QuantityUnit],
        dt: Optional[date] = None,
    ) -> float: ...

    @overload
    @classmethod
    def get_convertion_factor(
        cls,
        from_unit: Tuple[PriceUnit, TimeUnit],
        to_unit: Tuple[PriceUnit, TimeUnit],
        dt: Optional[date] = None,
    ) -> float: ...

    @classmethod
    def get_convertion_factor(cls, from_unit, to_unit, dt: Optional[date] = None) -> float:
        if type(from_unit) is not type(to_unit):
            raise ValueError(f"from_unit {from_unit} and to_unit {to_unit} must be of the same type")
        if (
            isinstance(from_unit, tuple)
            and isinstance(from_unit[0], PriceUnit)
            and isinstance(from_unit[1], QuantityUnit)
        ):
            return cls.get_price_unit_convertion_factor(
                from_unit[0], to_unit[0]
            ) / cls.get_quantity_unit_convertion_factor(from_unit[1], to_unit[1])
        if isinstance(from_unit, tuple) and isinstance(from_unit[0], PriceUnit) and isinstance(from_unit[1], TimeUnit):
            if dt is None:
                raise ValueError(
                    f"dt must not be None when from_unit {from_unit} and to_unit {to_unit} are of type Tuple[PriceUnit, TimeUnit]"
                )
            return cls.get_price_unit_convertion_factor(from_unit[0], to_unit[0]) / cls.get_time_unit_convertion_factor(
                from_unit[1], to_unit[1], dt
            )

        raise ValueError(
            f"from_unit {from_unit} and to_unit {to_unit} must be of type Tuple[PriceUnit, QuantityUnit] or Tuple[PriceUnit, TimeUnit]"
        )

    # ----------------------------------
    @classmethod
    def convert(
        cls,
        price_values: list[PriceValue[ValueUnit, BaseUnit]],
        to_unit: Tuple[ValueUnit, BaseUnit],
    ) -> list[PriceValue[ValueUnit, BaseUnit]]:

        if price_values is None or len(price_values) == 0:
            raise ValueError("price_values is None or empty")

        if to_unit is None:
            raise ValueError("to_unit is None")

        res = list[PriceValue[ValueUnit, BaseUnit]]()
        for price_value in price_values:
            if price_value.value_unit is None:
                raise ValueError("price_value.value_unit is None")
            if price_value.base_unit is None:
                raise ValueError("price_value.base_unit is None")

            res.append(
                PriceValue(
                    start_date=price_value.start_date,
                    end_date=price_value.end_date,
                    value=price_value.value
                    * cls.get_convertion_factor(
                        (price_value.value_unit, price_value.base_unit), to_unit, price_value.start_date  # type: ignore
                    ),
                    value_unit=to_unit[0],
                    base_unit=to_unit[1],
                    vat_id=price_value.vat_id,
                )
            )

        return res
