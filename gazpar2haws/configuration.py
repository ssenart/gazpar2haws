from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import date
import yaml
from enum import Enum
from gazpar2haws import config_utils


class LoggingLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TimeUnit(str, Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class PriceUnit(str, Enum):
    EURO = "€"
    CENT = "¢"


class QuantityUnit(str, Enum):
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


class Rate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    rate: float


class ConsumptionPrice(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    price: float
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    quantity_unit: Optional[QuantityUnit] = QuantityUnit.KWH
    vat_id: Optional[str] = None


class SubscriptionPrice(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    price: float
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    time_unit: Optional[TimeUnit] = TimeUnit.MONTH
    vat_id: Optional[str] = None


class TransportPrice(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    price: float
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    time_unit: Optional[TimeUnit] = TimeUnit.YEAR
    vat_id: Optional[str] = None


class EnergyTaxes(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    price: float
    price_unit: Optional[PriceUnit] = PriceUnit.EURO
    quantity_unit: Optional[QuantityUnit] = QuantityUnit.KWH
    vat_id: Optional[str] = None


class Pricing(BaseModel):
    value_added_tax: dict[str, list[Rate]]
    consumption_prices: list[ConsumptionPrice]
    subscription_prices: list[SubscriptionPrice]
    transport_prices: list[TransportPrice]
    energy_taxes: list[EnergyTaxes]

    @model_validator(mode="before")
    @classmethod
    def set_end_dates(cls, values):
        for price_list in ['consumption_prices', 'subscription_prices', 'transport_prices', 'energy_taxes']:
            prices = values.get(price_list, [])
            for i in range(len(prices) - 1):
                prices[i]['end_date'] = prices[i + 1]['start_date']
        return values


class Configuration(BaseModel):

    logging: Logging
    grdf: Grdf
    homeassistant: HomeAssistant
    pricing: Pricing

    @classmethod
    def load(cls, config_file: str, secrets_file: str):

        # Load configuration
        config = config_utils.ConfigLoader(config_file, secrets_file)
        config.load_secrets()
        config.load_config()

        return cls(**config.dict())
