from datetime import date

from gazpar2haws.model import TimeUnit, PriceUnit, QuantityUnit, VATRate, ConsumptionPrice, SubscriptionPrice, TransportPrice, EnergyTaxes

from gazpar2haws.date_array import DateArray

class Pricing:

    def __init__(self):
        self._vat_rates = dict[VATRate, Rate]
        self._consumption_prices = list[ConsumptionPrice]
        self._subscription_prices = list[SubscriptionPrice]
        self._transport_prices = list[TransportPrice]
        self._energy_taxes = list[EnergyTaxes]

    def compute(self, date: date, energy_quantity: float) -> float:

        return 0.0

    def get_vat_rate(self, date: date, level: str) -> float:

        return 0.0

    def get_consumption_price(self, date: date, price_unit: str, quantity_unit: str) -> float:

        for price in self._consumption_prices:
            if price.start_date <= date <= price.end_date:
                return price.price

        return 0.0

    def get_subscription_price(self, date: date, price_unit: str, time_unit: str) -> float:

        return 0.0

    def get_transport_price(self, date: date, price_unit: str, time_unit: str) -> float:

        return 0.0

    def get_energy_taxes(self, date: date, price_unit: str, quantity_unit: str) -> float:

        return 0.0

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