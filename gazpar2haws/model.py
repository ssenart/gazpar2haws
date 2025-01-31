from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr, model_validator

from gazpar2haws.date_array import DateArray


class LoggingLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TimeUnit(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class PriceUnit(str, Enum):
    EURO = "€"
    CENT = "¢"


class QuantityUnit(str, Enum):
    MWH = "MWh"
    KWH = "kWh"
    WH = "Wh"
    M3 = "m³"
    LITER = "l"


class Logging(BaseModel):
    file: str
    console: bool
    level: LoggingLevel
    format: str


class Device(BaseModel):
    name: str
    data_source: Optional[str] = None
    as_of_date: Optional[date] = None
    username: Optional[EmailStr] = None
    password: Optional[SecretStr] = None
    pce_identifier: Optional[SecretStr] = None
    timezone: Optional[str] = "Europe/Paris"
    last_days: Optional[int] = 365
    reset: Optional[bool] = False


class Grdf(BaseModel):
    scan_interval: Optional[int] = 480
    devices: list[Device]


class HomeAssistant(BaseModel):
    host: str
    port: int
    endpoint: Optional[str] = "/api/websocket"
    token: str


class Period(BaseModel):
    start_date: date
    end_date: Optional[date] = None


class Rate(Period):
    rate: float


class Price(Period):
    price: float


class PriceArray(Period):
    price_array: Optional[DateArray] = None


class Consumption(BaseModel):
    price_unit: PriceUnit = PriceUnit.EURO
    quantity_unit: QuantityUnit = QuantityUnit.KWH
    vat_id: Optional[str] = None


class ConsumptionPrice(Consumption, Price):
    pass


class ConsumptionPriceArray(Consumption, PriceArray):

    @model_validator(mode="after")
    def set_price_array(self):
        self.price_array = DateArray(start_date=self.start_date, end_date=self.end_date)  # pylint: disable=attribute-defined-outside-init
        return self


class Subscription(BaseModel):
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    time_unit: Optional[TimeUnit] = TimeUnit.MONTH
    vat_id: Optional[str] = None


class SubscriptionPrice(Subscription, Price):
    pass


class SubscriptionPriceArray(Subscription, PriceArray):

    @model_validator(mode="after")
    def set_price_array(self):
        self.price_array = DateArray(start_date=self.start_date, end_date=self.end_date)  # pylint: disable=attribute-defined-outside-init
        return self


class Transport(BaseModel):
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    time_unit: Optional[TimeUnit] = TimeUnit.YEAR
    vat_id: Optional[str] = None


class TransportPrice(Transport, Price):
    pass


class TransportPriceArray(Transport, PriceArray):

    @model_validator(mode="after")
    def set_price_array(self):
        self.price_array = DateArray(start_date=self.start_date, end_date=self.end_date)  # pylint: disable=attribute-defined-outside-init
        return self


class EnergyTaxes(BaseModel):
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    quantity_unit: Optional[QuantityUnit] = QuantityUnit.KWH
    vat_id: Optional[str] = None


class EnergyTaxesPrice(EnergyTaxes, Price):
    pass


class EnergyTaxesPriceArray(EnergyTaxes, PriceArray):

    @model_validator(mode="after")
    def set_price_array(self):
        self.price_array = DateArray(start_date=self.start_date, end_date=self.end_date)  # pylint: disable=attribute-defined-outside-init
        return self


class Pricing(BaseModel):
    value_added_tax: dict[str, list[Rate]]
    consumption_prices: list[ConsumptionPrice]
    subscription_prices: list[SubscriptionPrice]
    transport_prices: list[TransportPrice]
    energy_taxes: list[EnergyTaxesPrice]

    @model_validator(mode="before")
    @classmethod
    def set_end_dates(cls, values):
        for price_list in ['consumption_prices', 'subscription_prices', 'transport_prices', 'energy_taxes']:
            prices = values.get(price_list, [])
            for i in range(len(prices) - 1):
                prices[i]['end_date'] = prices[i + 1]['start_date']
        return values


class ConsumptionQuantityArray(BaseModel):
    start_date: date
    end_date: date
    quantity_array: Optional[DateArray] = None
    quantity_unit: QuantityUnit

    @model_validator(mode="after")
    def set_quantity_array(self):
        if self.quantity_array is None:
            self.quantity_array = DateArray(start_date=self.start_date, end_date=self.end_date)
        return self


class CostArray(BaseModel):
    start_date: date
    end_date: date
    cost_array: Optional[DateArray] = None
    cost_unit: PriceUnit

