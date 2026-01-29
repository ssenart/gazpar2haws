import tempfile
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, model_validator
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
    """Pricing configuration with flexible component names.

    The 'vat' field is reserved for VAT rates.
    All other fields are treated as pricing components (e.g., consumption_prices,
    subscription_prices, my_custom_tax, carbon_fee, etc.).
    """
    model_config = ConfigDict(extra='allow')

    vat: Optional[list[VatRate]] = None

    @model_validator(mode="before")
    @classmethod
    def propagates_properties(cls, values):
        """Propagate properties through all pricing component lists."""
        # Default units for all price types
        default_units = {
            "price_unit": "€",
            "quantity_unit": "kWh",
            "time_unit": "month",
        }

        # Process all fields except 'vat'
        for component_name, prices in list(values.items()):
            if component_name == "vat":
                continue

            if not isinstance(prices, list) or len(prices) == 0:
                continue

            if "start_date" not in prices[0]:
                raise ValueError(f"Missing start_date in first element of {component_name}")

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

            # Convert to CompositePriceValue objects
            values[component_name] = [CompositePriceValue(**p) if isinstance(p, dict) else p for p in prices]

        return values

    @model_validator(mode="after")
    def validate_components(self):
        """Validate that at least one pricing component exists with quantity_value."""
        components = self.get_components()

        if not components:
            raise ValueError("At least one pricing component is required")

        # At least one quantity-based component required
        has_quantity = any(
            any(p.quantity_value is not None for p in prices)
            for prices in components.values()
        )
        if not has_quantity:
            raise ValueError("At least one component must have quantity_value defined")

        return self

    def get_components(self) -> dict[str, list[CompositePriceValue]]:
        """Get all pricing components (all fields except 'vat')."""
        components = {}

        # Get extra fields (all fields except 'vat')
        if hasattr(self, '__pydantic_extra__') and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if isinstance(value, list) and len(value) > 0:
                    components[key] = value

        return components


# ----------------------------------
class ConsumptionQuantityArray(Unit[QuantityUnit, TimeUnit], ValueArray):
    pass


# ----------------------------------
class CostArray(Unit[PriceUnit, TimeUnit], ValueArray):
    pass


# ----------------------------------
class CostBreakdown(BaseModel):
    """Detailed breakdown of costs with individual components and total.

    The 'total' field contains the sum of all component costs.
    All other fields are individual component costs (e.g., consumption_prices_cost,
    subscription_prices_cost, my_custom_tax_cost, etc.).
    """
    model_config = ConfigDict(extra='allow')

    total: CostArray

    def get_component_costs(self) -> dict[str, CostArray]:
        """Get all component cost arrays (all fields except 'total')."""
        components = {}

        # Get extra fields (all fields except 'total')
        if hasattr(self, '__pydantic_extra__') and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if isinstance(value, CostArray):
                    components[key] = value

        return components

    def __getattr__(self, name: str) -> CostArray:
        """Provide backward compatibility for legacy attribute access.

        Maps legacy names (consumption, subscription, transport, energy_taxes)
        to their corresponding component names (consumption_prices, etc.).
        """
        # Legacy name mapping
        legacy_map = {
            "consumption": "consumption_prices",
            "subscription": "subscription_prices",
            "transport": "transport_prices",
        }

        # Try legacy mapping first
        if name in legacy_map:
            component_name = legacy_map[name]
            components = self.get_component_costs()
            if component_name in components:
                return components[component_name]

        # Try direct component name (e.g., energy_taxes)
        components = self.get_component_costs()
        if name in components:
            return components[name]

        # If not found, raise AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
