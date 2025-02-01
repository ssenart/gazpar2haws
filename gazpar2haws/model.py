from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr, model_validator

from gazpar2haws.date_array import DateArray

from typing import Generic, TypeVar


# ----------------------------------
class LoggingLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ----------------------------------
class TimeUnit(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# ----------------------------------
class PriceUnit(str, Enum):
    EURO = "€"
    CENT = "¢"


# ----------------------------------
class QuantityUnit(str, Enum):
    MWH = "MWh"
    KWH = "kWh"
    WH = "Wh"
    M3 = "m³"
    LITER = "l"


# ----------------------------------
class Logging(BaseModel):
    file: str
    console: bool
    level: LoggingLevel
    format: str


# ----------------------------------
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


# ----------------------------------
class Grdf(BaseModel):
    scan_interval: Optional[int] = 480
    devices: list[Device]


# ----------------------------------
class HomeAssistant(BaseModel):
    host: str
    port: int
    endpoint: Optional[str] = "/api/websocket"
    token: str


# ----------------------------------
class Period(BaseModel):
    start_date: date
    end_date: Optional[date] = None


# ----------------------------------
class Value(Period):
    value: float


# ----------------------------------
class ValueArray(Period):
    value_array: Optional[DateArray] = None

    @model_validator(mode="after")
    def set_value_array(self):
        self.value_array = DateArray(
            start_date=self.start_date, end_date=self.end_date
        )  # pylint: disable=attribute-defined-outside-init
        return self


# ----------------------------------
class Vat(BaseModel):
    id: str


# ----------------------------------
class VatRate(Vat, Value):
    pass


# ----------------------------------
class VatRateArray(Vat, ValueArray):
    pass


# ----------------------------------
# Define type variables
ValueUnit = TypeVar('ValueUnit')
BaseUnit = TypeVar('BaseUnit')


# ----------------------------------
class Price(BaseModel, Generic[ValueUnit, BaseUnit]):
    price_unit: Optional[ValueUnit] = None
    base_unit: Optional[BaseUnit] = None
    vat_id: Optional[str] = None


# ----------------------------------
class PriceValue(Price[ValueUnit, BaseUnit], Value):
    pass


# ----------------------------------
class PriceValueArray(Price[ValueUnit, BaseUnit], ValueArray):
    pass


# ----------------------------------
class ConsumptionPriceArray(PriceValueArray[PriceUnit, QuantityUnit]):
    pass


# ----------------------------------
class SubscriptionPriceArray(PriceValueArray[PriceUnit, TimeUnit]):
    pass


# ----------------------------------
class TransportPriceArray(PriceValueArray[PriceUnit, TimeUnit]):
    pass


# ----------------------------------
class EnergyTaxesPriceArray(PriceValueArray[PriceUnit, QuantityUnit]):
    pass


# ----------------------------------
class Pricing(BaseModel):
    vat: list[VatRate]
    consumption_prices: list[PriceValue[PriceUnit, QuantityUnit]]
    subscription_prices: list[PriceValue[PriceUnit, TimeUnit]]
    transport_prices: list[PriceValue[PriceUnit, TimeUnit]]
    energy_taxes: list[PriceValue[PriceUnit, QuantityUnit]]

    @model_validator(mode="before")
    @classmethod
    def propagates_properties(cls, values):
        for price_list in [
            "consumption_prices",
            "subscription_prices",
            "transport_prices",
            "energy_taxes",
        ]:
            prices = values.get(price_list, [])

            if len(prices) == 0:
                continue

            if "start_date" not in prices[0]:
                raise ValueError(f"Missing start_date in first element of {price_list}")
            if "price_unit" not in prices[0]:
                raise ValueError(f"Missing price_unit in first element of {price_list}")
            if "base_unit" not in prices[0]:
                raise ValueError(f"Missing base_unit in first element of {price_list}")
            if "vat_id" not in prices[0]:
                raise ValueError(f"Missing vat_id in first element of {price_list}")

            for i in range(len(prices) - 1):
                if "end_date" not in prices[i]:
                    prices[i]["end_date"] = prices[i + 1]["start_date"]
                if "price_unit" not in prices[i + 1]:
                    prices[i + 1]["price_unit"] = prices[i]["price_unit"]
                if "base_unit" not in prices[i + 1]:
                    prices[i + 1]["base_unit"] = prices[i]["base_unit"]
                if "vat_id" not in prices[i + 1]:
                    prices[i + 1]["vat_id"] = prices[i]["vat_id"]

        return values


# ----------------------------------
class ConsumptionQuantityArray(BaseModel):
    start_date: date
    end_date: date
    quantity_array: Optional[DateArray] = None
    quantity_unit: QuantityUnit

    @model_validator(mode="after")
    def set_quantity_array(self):
        if self.quantity_array is None:
            self.quantity_array = DateArray(
                start_date=self.start_date, end_date=self.end_date
            )
        return self


# ----------------------------------
class CostArray(BaseModel):
    start_date: date
    end_date: date
    cost_array: Optional[DateArray] = None
    cost_unit: PriceUnit
