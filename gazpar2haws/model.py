import tempfile
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, EmailStr, SecretStr, model_validator
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
    tmp_dir: Optional[str] = None  # If None, will use system temp directory
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

        # Set tmp_dir to system temp directory if not specified
        if self.tmp_dir is None:
            self.tmp_dir = tempfile.gettempdir()

        # Validate tmp_dir exists for excel data source
        if self.data_source == "excel" and not Path(self.tmp_dir).is_dir():
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
class CompositePriceValue(Period):
    price_unit: Optional[PriceUnit] = None  # € or ¢ (applies to both components)
    vat_id: Optional[str] = None

    # Quantity component (€/kWh)
    quantity_value: Optional[float] = None
    quantity_unit: Optional[QuantityUnit] = None

    # Time component (€/month)
    time_value: Optional[float] = None
    time_unit: Optional[TimeUnit] = None


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
class CompositePriceArray(Period):  # pylint: disable=too-few-public-methods
    name: Optional[str] = None
    price_unit: Optional[PriceUnit] = None
    vat_id: Optional[str] = None

    # Quantity component (€/kWh) - vectorized
    quantity_value_array: Optional[DateArray] = None
    quantity_unit: Optional[QuantityUnit] = None

    # Time component (€/month) - vectorized
    time_value_array: Optional[DateArray] = None
    time_unit: Optional[TimeUnit] = None

    @model_validator(mode="after")
    def set_value_arrays(self):
        if self.quantity_value_array is None:
            self.quantity_value_array = DateArray(
                name=f"{self.name}_quantity", start_date=self.start_date, end_date=self.end_date
            )  # pylint: disable=attribute-defined-outside-init
        if self.time_value_array is None:
            self.time_value_array = DateArray(
                name=f"{self.name}_time", start_date=self.start_date, end_date=self.end_date
            )  # pylint: disable=attribute-defined-outside-init
        return self


# ----------------------------------
class Pricing(BaseModel):
    vat: Optional[list[VatRate]] = None
    consumption_prices: list[CompositePriceValue]
    subscription_prices: Optional[list[CompositePriceValue]] = None
    transport_prices: Optional[list[CompositePriceValue]] = None
    energy_taxes: Optional[list[CompositePriceValue]] = None

    @model_validator(mode="before")
    @classmethod
    def propagates_properties(cls, values):
        # Default units for all price types
        default_units = {
            "price_unit": "€",
            "quantity_unit": "kWh",
            "time_unit": "month",
        }

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

            # Apply defaults to first entry
            for key, default_value in default_units.items():
                if key not in prices[0]:
                    prices[0][key] = default_value

            # Propagate properties through the list
            for i in range(len(prices) - 1):
                if "end_date" not in prices[i]:
                    prices[i]["end_date"] = prices[i + 1]["start_date"]
                for key, default_value in default_units.items():
                    if key not in prices[i + 1]:
                        prices[i + 1][key] = prices[i][key]
                if "vat_id" not in prices[i + 1] and "vat_id" in prices[i]:
                    prices[i + 1]["vat_id"] = prices[i]["vat_id"]

        return values


# ----------------------------------
class ConsumptionQuantityArray(Unit[QuantityUnit, TimeUnit], ValueArray):
    pass


# ----------------------------------
class CostArray(Unit[PriceUnit, TimeUnit], ValueArray):
    pass


# ----------------------------------
class CostBreakdown(BaseModel):
    """Detailed breakdown of costs with individual components and total."""

    consumption: CostArray
    subscription: CostArray
    transport: CostArray
    energy_taxes: CostArray
    total: CostArray
