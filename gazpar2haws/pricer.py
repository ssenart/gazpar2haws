from datetime import date, timedelta

from gazpar2haws.configuration import Pricing, PriceUnit, QuantityUnit, ConsumptionPriceArray


class Pricer:

    def __init__(self, pricing: Pricing):
        self._pricing = pricing

    def get_consumption_price_array(self, start_date: date, end_date: date) -> ConsumptionPriceArray:

        if self._pricing.consumption_prices is not None and len(self._pricing.consumption_prices) > 0:
            first_consumption_price = self._pricing.consumption_prices[0]
            last_consumption_price = self._pricing.consumption_prices[-1]
        else:
            first_consumption_price = None
            last_consumption_price = None

        res = ConsumptionPriceArray(
            start_date=start_date,
            end_date=end_date,
            price_unit=first_consumption_price.price_unit if first_consumption_price is not None else PriceUnit.EURO,
            quantity_unit=first_consumption_price.quantity_unit if first_consumption_price is not None else QuantityUnit.KWH,
            vat_id=first_consumption_price.vat_id if first_consumption_price is not None else None
        )

        if res.price_array is not None:
            if first_consumption_price is not None and first_consumption_price.start_date > end_date:
                # Fully before first consumption period.
                res.price_array[start_date:end_date] = first_consumption_price.price
            elif last_consumption_price is not None and last_consumption_price.end_date is not None and last_consumption_price.end_date < start_date:
                # Fully after last consumption period.
                res.price_array[start_date:end_date] = last_consumption_price.price
            else:
                if first_consumption_price is not None and start_date < first_consumption_price.start_date:
                    # Partially before first consumption period.
                    res.price_array[start_date:first_consumption_price.start_date] = first_consumption_price.price
                if last_consumption_price is not None and last_consumption_price.end_date is not None and end_date > last_consumption_price.end_date:
                    # Partially after last consumption period.
                    res.price_array[last_consumption_price.end_date:end_date] = last_consumption_price.price
                # Inside consumption periods.
                for consumption_price in self._pricing.consumption_prices:
                    latest_start = max(consumption_price.start_date, start_date)
                    earliest_end = min(consumption_price.end_date if consumption_price.end_date is not None else end_date, end_date)
                    current_date = latest_start
                    while current_date <= earliest_end:
                        res.price_array[current_date] = consumption_price.price
                        current_date += timedelta(days=1)

        return res

    def convert_price(self, price: float, from_price_unit: PriceUnit, to_price_unit: PriceUnit) -> float:

        switcher = {
            PriceUnit.EURO: 1,
            PriceUnit.CENT: 100,
        }

        return price * switcher.get(from_price_unit) / switcher.get(to_price_unit)

    def convert_quantity(self, quantity: float, from_quantity_unit: QuantityUnit, to_quantity_unit: QuantityUnit) -> float:

        switcher = {
            QuantityUnit.KWH: 1,
            QuantityUnit.MWH: 1000,
        }

        return quantity * switcher.get(from_quantity_unit) / switcher.get(to_quantity_unit)