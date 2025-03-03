from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, DirectoryPath, EmailStr, SecretStr, model_validator
from pydantic_extra_types.timezone_name import TimeZoneName

from gazpar2haws.date_array import DateArray


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
    data_source: str = "json"
    tmp_dir: DirectoryPath = DirectoryPath("/tmp")
    as_of_date: Optional[date] = None
    username: Optional[EmailStr] = None
    password: Optional[SecretStr] = None
    pce_identifier: Optional[SecretStr] = None
    timezone: TimeZoneName = TimeZoneName("Europe/Paris")
    last_days: int = 365
    reset: bool = False

    @model_validator(mode="after")
    def validate_properties(self):
        if self.data_source not in ["json", "excel", "test"]:
            raise ValueError(f"Invalid data_source{self.data_source} (expected values: json, excel, test)")
        if self.data_source != "test" and self.username is None:
            raise ValueError("Missing username")
        if self.data_source != "test" and self.password is None:
            raise ValueError("Missing password")
        if self.data_source != "test" and self.pce_identifier is None:
            raise ValueError("Missing pce_identifier")
        if self.data_source == "excel" and self.tmp_dir is None or not Path(self.tmp_dir).is_dir():
            raise ValueError(f"Invalid tmp_dir {self.tmp_dir}")
        return self


# ----------------------------------
class Grdf(BaseModel):
    scan_interval: Optional[int] = 480
    devices: list[Device]


# ----------------------------------
class HomeAssistant(BaseModel):
    host: str
    port: int
    endpoint: str = "/api/websocket"
    token: SecretStr


# ----------------------------------
class Period(BaseModel):
    start_date: date
    end_date: Optional[date] = None


# ----------------------------------
class Value(Period):
    value: float


# ----------------------------------
class ValueArray(Period):
    name: Optional[str] = None
    value_array: Optional[DateArray] = None

    @model_validator(mode="after")
    def set_value_array(self):
        if self.value_array is None:
            self.value_array = DateArray(
                name=self.name, start_date=self.start_date, end_date=self.end_date
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
ValueUnit = TypeVar("ValueUnit")
BaseUnit = TypeVar("BaseUnit")


# ----------------------------------
class Unit(BaseModel, Generic[ValueUnit, BaseUnit]):
    value_unit: Optional[ValueUnit] = None
    base_unit: Optional[BaseUnit] = None


# ----------------------------------
class Price(Unit[ValueUnit, BaseUnit]):  # pylint: disable=too-few-public-methods
    vat_id: Optional[str] = None


# ----------------------------------
class PriceValue(Price[ValueUnit, BaseUnit], Value):
    pass


# ----------------------------------
class PriceValueArray(Price[ValueUnit, BaseUnit], ValueArray):
    pass


# ----------------------------------
class ConsumptionPriceArray(PriceValueArray[PriceUnit, QuantityUnit]):  # pylint: disable=too-few-public-methods
    pass


# ----------------------------------
class SubscriptionPriceArray(PriceValueArray[PriceUnit, TimeUnit]):  # pylint: disable=too-few-public-methods
    pass


# ----------------------------------
class TransportPriceArray(PriceValueArray[PriceUnit, TimeUnit]):  # pylint: disable=too-few-public-methods
    pass


# ----------------------------------
class EnergyTaxesPriceArray(PriceValueArray[PriceUnit, QuantityUnit]):  # pylint: disable=too-few-public-methods
    pass


# ----------------------------------
class Pricing(BaseModel):
    vat: Optional[list[VatRate]] = None
    consumption_prices: list[PriceValue[PriceUnit, QuantityUnit]]
    subscription_prices: Optional[list[PriceValue[PriceUnit, TimeUnit]]] = None
    transport_prices: Optional[list[PriceValue[PriceUnit, TimeUnit]]] = None
    energy_taxes: Optional[list[PriceValue[PriceUnit, QuantityUnit]]] = None

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
            if "value_unit" not in prices[0]:
                prices[0]["value_unit"] = "€"
            if "base_unit" not in prices[0]:
                if price_list in ["consumption_prices", "energy_taxes"]:
                    prices[0]["base_unit"] = "kWh"
                else:
                    raise ValueError(
                        "Missing base_unit in first element of ['transport_prices', 'subscription_prices']"
                    )

            for i in range(len(prices) - 1):
                if "end_date" not in prices[i]:
                    prices[i]["end_date"] = prices[i + 1]["start_date"]
                if "value_unit" not in prices[i + 1]:
                    prices[i + 1]["value_unit"] = prices[i]["value_unit"]
                if "base_unit" not in prices[i + 1]:
                    prices[i + 1]["base_unit"] = prices[i]["base_unit"]
                if "vat_id" not in prices[i + 1] and "vat_id" in prices[i]:
                    prices[i + 1]["vat_id"] = prices[i]["vat_id"]

        return values


# ----------------------------------
class ConsumptionQuantityArray(Unit[QuantityUnit, TimeUnit], ValueArray):
    pass


# ----------------------------------
class CostArray(Unit[PriceUnit, TimeUnit], ValueArray):
    pass
