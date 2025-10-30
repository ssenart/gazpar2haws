import calendar
from datetime import date, timedelta
from typing import Callable, Optional, Tuple, overload

from gazpar2haws.date_array import DateArray
from gazpar2haws.model import (
    BaseUnit,
    CompositePriceArray,
    CompositePriceValue,
    ConsumptionQuantityArray,
    CostArray,
    CostBreakdown,
    PriceUnit,
    PriceValue,
    Pricing,
    QuantityUnit,
    TimeUnit,
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
    ) -> CostBreakdown:

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

        # Transform to the vectorized form.
        if self._pricing.vat is not None and len(self._pricing.vat) > 0:
            vat_rate_array_by_id = self.get_vat_rate_array_by_id(
                start_date=start_date, end_date=end_date, vat_rates=self._pricing.vat
            )
        else:
            vat_rate_array_by_id = dict[str, VatRateArray]()

        # Use get_composite_price_array for all price types (conversion happens inside)
        consumption_composite = self.get_composite_price_array(
            start_date=start_date,
            end_date=end_date,
            composite_prices=self._pricing.consumption_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
            target_price_unit=price_unit,
            target_quantity_unit=quantities.value_unit,
            target_time_unit=quantities.base_unit,
        )

        # Subscription price is optional.
        if self._pricing.subscription_prices is not None and len(self._pricing.subscription_prices) > 0:
            subscription_composite = self.get_composite_price_array(
                start_date=start_date,
                end_date=end_date,
                composite_prices=self._pricing.subscription_prices,
                vat_rate_array_by_id=vat_rate_array_by_id,
                target_price_unit=price_unit,
                target_quantity_unit=quantities.value_unit,
                target_time_unit=quantities.base_unit,
            )
        else:
            subscription_composite = CompositePriceArray(
                name="subscription_prices",
                start_date=start_date,
                end_date=end_date,
                price_unit=price_unit,
                quantity_unit=quantities.value_unit,
                time_unit=quantities.base_unit,
            )

        # Transport price is optional.
        if self._pricing.transport_prices is not None and len(self._pricing.transport_prices) > 0:
            transport_composite = self.get_composite_price_array(
                start_date=start_date,
                end_date=end_date,
                composite_prices=self._pricing.transport_prices,
                vat_rate_array_by_id=vat_rate_array_by_id,
                target_price_unit=price_unit,
                target_quantity_unit=quantities.value_unit,
                target_time_unit=quantities.base_unit,
            )
        else:
            transport_composite = CompositePriceArray(
                name="transport_prices",
                start_date=start_date,
                end_date=end_date,
                price_unit=price_unit,
                quantity_unit=quantities.value_unit,
                time_unit=quantities.base_unit,
            )

        # Energy taxes are optional.
        if self._pricing.energy_taxes is not None and len(self._pricing.energy_taxes) > 0:
            energy_taxes_composite = self.get_composite_price_array(
                start_date=start_date,
                end_date=end_date,
                composite_prices=self._pricing.energy_taxes,
                vat_rate_array_by_id=vat_rate_array_by_id,
                target_price_unit=price_unit,
                target_quantity_unit=quantities.value_unit,
                target_time_unit=quantities.base_unit,
            )
        else:
            energy_taxes_composite = CompositePriceArray(
                name="energy_taxes",
                start_date=start_date,
                end_date=end_date,
                price_unit=price_unit,
                quantity_unit=quantities.value_unit,
                time_unit=quantities.base_unit,
            )

        # Create individual cost arrays for each component
        consumption_cost = CostArray(
            name="consumption_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        consumption_cost.value_array = (
            quantity_array * consumption_composite.quantity_value_array  # type: ignore
            + consumption_composite.time_value_array  # type: ignore
        )

        subscription_cost = CostArray(
            name="subscription_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        subscription_cost.value_array = (
            quantity_array * subscription_composite.quantity_value_array  # type: ignore
            + subscription_composite.time_value_array  # type: ignore
        )

        transport_cost = CostArray(
            name="transport_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        transport_cost.value_array = (
            quantity_array * transport_composite.quantity_value_array  # type: ignore
            + transport_composite.time_value_array  # type: ignore
        )

        energy_taxes_cost = CostArray(
            name="energy_taxes_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        energy_taxes_cost.value_array = (
            quantity_array * energy_taxes_composite.quantity_value_array  # type: ignore
            + energy_taxes_composite.time_value_array  # type: ignore
        )

        # Calculate total cost
        total_cost = CostArray(
            name="total_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        total_cost.value_array = (
            consumption_cost.value_array  # type: ignore
            + subscription_cost.value_array  # type: ignore
            + transport_cost.value_array  # type: ignore
            + energy_taxes_cost.value_array  # type: ignore
        )

        # Return detailed breakdown
        return CostBreakdown(
            consumption=consumption_cost,
            subscription=subscription_cost,
            transport=transport_cost,
            energy_taxes=energy_taxes_cost,
            total=total_cost,
        )

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
    def get_composite_price_array(
        cls,
        start_date: date,
        end_date: date,
        composite_prices: list[CompositePriceValue],
        vat_rate_array_by_id: dict[str, VatRateArray],
        target_price_unit: PriceUnit,
        target_quantity_unit: QuantityUnit,
        target_time_unit: TimeUnit,
    ) -> CompositePriceArray:

        if composite_prices is None or len(composite_prices) == 0:
            raise ValueError("composite_prices is None or empty")

        # Convert all composite prices to target units
        composite_prices_converted = cls.convert(
            composite_prices, (target_price_unit, target_quantity_unit, target_time_unit)
        )

        # Get vat_id from first element (after conversion it should all be the same)
        first_composite_price = composite_prices_converted[0]

        res = CompositePriceArray(
            name="composite_prices",
            start_date=start_date,
            end_date=end_date,
            price_unit=target_price_unit,
            quantity_unit=target_quantity_unit,
            time_unit=target_time_unit,
            vat_id=first_composite_price.vat_id,
        )

        # Fill the quantity component array (if present in the composite prices)
        cls._fill_composite_quantity_array(res, composite_prices_converted, vat_rate_array_by_id)

        # Fill the time component array (if present in the composite prices)
        cls._fill_composite_time_array(res, composite_prices_converted, vat_rate_array_by_id)

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
    def _fill_composite_component_array(  # pylint: disable=too-many-branches, too-many-statements
        cls,
        out_composite_array: CompositePriceArray,
        in_composite_values: list[CompositePriceValue],
        vat_rate_array_by_id: dict[str, VatRateArray],
        get_array: Callable[[CompositePriceArray], DateArray],
        get_value: Callable[[CompositePriceValue], Optional[float]],
    ) -> None:
        """Generic method to fill either quantity or time component array of a CompositePriceArray."""

        if out_composite_array is None:
            raise ValueError("out_composite_array is None")

        if out_composite_array.start_date is None:
            raise ValueError("out_composite_array.start_date is None")

        start_date = out_composite_array.start_date

        if out_composite_array.end_date is None:
            raise ValueError("out_composite_array.end_date is None")

        end_date = out_composite_array.end_date

        component_array = get_array(out_composite_array)
        if component_array is None:
            raise ValueError("component_array is None")

        if in_composite_values is None or len(in_composite_values) == 0:
            raise ValueError("in_composite_values is None or empty")

        first_value = in_composite_values[0]
        last_value = in_composite_values[-1]

        if first_value.start_date > end_date:
            # Fully before first value period.
            component_value = get_value(first_value)
            if component_value is not None:
                if vat_rate_array_by_id is not None and first_value.vat_id in vat_rate_array_by_id:
                    vat_value = vat_rate_array_by_id[first_value.vat_id].value_array[start_date : end_date + timedelta(1)]  # type: ignore
                else:
                    vat_value = 0.0
                component_array[start_date : end_date + timedelta(1)] = (vat_value + 1) * component_value  # type: ignore
        elif last_value.end_date is not None and last_value.end_date < start_date:
            # Fully after last value period.
            component_value = get_value(last_value)
            if component_value is not None:
                if vat_rate_array_by_id is not None and last_value.vat_id in vat_rate_array_by_id:
                    vat_value = vat_rate_array_by_id[last_value.vat_id].value_array[start_date : end_date + timedelta(1)]  # type: ignore
                else:
                    vat_value = 0.0
                component_array[start_date : end_date + timedelta(1)] = (vat_value + 1) * component_value  # type: ignore
        else:
            if start_date < first_value.start_date:
                # Partially before first value period.
                component_value = get_value(first_value)
                if component_value is not None:
                    if vat_rate_array_by_id is not None and first_value.vat_id in vat_rate_array_by_id:
                        vat_value = vat_rate_array_by_id[first_value.vat_id].value_array[start_date : first_value.start_date + timedelta(1)]  # type: ignore
                    else:
                        vat_value = 0.0
                    component_array[start_date : first_value.start_date + timedelta(1)] = (vat_value + 1) * component_value  # type: ignore
            if last_value.end_date is not None and end_date > last_value.end_date:
                # Partially after last value period.
                component_value = get_value(last_value)
                if component_value is not None:
                    if vat_rate_array_by_id is not None and last_value.vat_id in vat_rate_array_by_id:
                        vat_value = vat_rate_array_by_id[last_value.vat_id].value_array[last_value.end_date : end_date + timedelta(1)]  # type: ignore
                    else:
                        vat_value = 0.0
                    component_array[last_value.end_date : end_date + timedelta(1)] = (vat_value + 1) * component_value  # type: ignore
            # Inside value periods.
            for value in in_composite_values:
                component_value = get_value(value)
                if component_value is not None:
                    latest_start = max(value.start_date, start_date)
                    earliest_end = min(value.end_date if value.end_date is not None else end_date, end_date)
                    current_date = latest_start
                    while current_date <= earliest_end:
                        if vat_rate_array_by_id is not None and value.vat_id in vat_rate_array_by_id:
                            vat_value = vat_rate_array_by_id[value.vat_id].value_array[current_date]  # type: ignore
                        else:
                            vat_value = 0.0
                        component_array[current_date] = (vat_value + 1) * component_value  # type: ignore
                        current_date += timedelta(days=1)

    # ----------------------------------
    @classmethod
    def _fill_composite_quantity_array(
        cls,
        out_composite_array: CompositePriceArray,
        in_composite_values: list[CompositePriceValue],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> None:
        """Fill the quantity component array of a CompositePriceArray."""
        cls._fill_composite_component_array(
            out_composite_array,
            in_composite_values,
            vat_rate_array_by_id,
            lambda arr: arr.quantity_value_array,  # type: ignore
            lambda val: val.quantity_value,
        )

    # ----------------------------------
    @classmethod
    def _fill_composite_time_array(
        cls,
        out_composite_array: CompositePriceArray,
        in_composite_values: list[CompositePriceValue],
        vat_rate_array_by_id: dict[str, VatRateArray],
    ) -> None:
        """Fill the time component array of a CompositePriceArray."""
        cls._fill_composite_component_array(
            out_composite_array,
            in_composite_values,
            vat_rate_array_by_id,
            lambda arr: arr.time_value_array,  # type: ignore
            lambda val: val.time_value,
        )

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
    @overload
    @classmethod
    def convert(
        cls,
        price_values: list[PriceValue[ValueUnit, BaseUnit]],
        to_unit: Tuple[ValueUnit, BaseUnit],
    ) -> list[PriceValue[ValueUnit, BaseUnit]]: ...

    @overload
    @classmethod
    def convert(
        cls,
        composite_prices: list[CompositePriceValue],
        to_unit: Tuple[PriceUnit, QuantityUnit, TimeUnit],
    ) -> list[CompositePriceValue]: ...

    @classmethod
    def convert(cls, price_values, to_unit):

        if price_values is None or len(price_values) == 0:
            raise ValueError("price_values is None or empty")

        if to_unit is None:
            raise ValueError("to_unit is None")

        # Check if input is CompositePriceValue list (has 3-tuple with QuantityUnit and TimeUnit)
        if isinstance(price_values[0], CompositePriceValue):
            # to_unit is (PriceUnit, QuantityUnit, TimeUnit)
            target_price_unit = to_unit[0]
            target_quantity_unit = to_unit[1]
            target_time_unit = to_unit[2]

            res = list[CompositePriceValue]()
            for composite_price in price_values:
                converted_quantity_value = None
                converted_time_value = None

                # Convert quantity component if present
                if composite_price.quantity_value is not None and composite_price.quantity_unit is not None:
                    quantity_conversion_factor = cls.get_convertion_factor(
                        (composite_price.price_unit, composite_price.quantity_unit),
                        (target_price_unit, target_quantity_unit),
                        composite_price.start_date,
                    )
                    converted_quantity_value = composite_price.quantity_value * quantity_conversion_factor

                # Convert time component if present
                if composite_price.time_value is not None and composite_price.time_unit is not None:
                    time_conversion_factor = cls.get_convertion_factor(
                        (composite_price.price_unit, composite_price.time_unit),
                        (target_price_unit, target_time_unit),
                        composite_price.start_date,
                    )
                    converted_time_value = composite_price.time_value * time_conversion_factor

                res.append(
                    CompositePriceValue(
                        start_date=composite_price.start_date,
                        end_date=composite_price.end_date,
                        price_unit=target_price_unit,
                        quantity_value=converted_quantity_value,
                        quantity_unit=target_quantity_unit,
                        time_value=converted_time_value,
                        time_unit=target_time_unit,
                        vat_id=composite_price.vat_id,
                    )
                )
            return res

        # Original PriceValue conversion logic (2-tuple)
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
