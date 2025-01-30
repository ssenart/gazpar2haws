from datetime import date
from enum import Enum

from pydantic import BaseModel, model_validator

from gazpar2haws.date_array import DateArray


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


class Flow(BaseModel):
    date: date
    quantity: float
    unit: str


class ValueAddedTax(BaseModel):
    rate: float


class Rate(BaseModel):
    start_date: date
    end_date: date
    rate: float


class VATRate(BaseModel):
    id: str


class VATRateRepository(BaseModel):
    rateById: dict[VATRate, list[Rate]]


class ConsumptionQuantityArray(BaseModel):
    start_date: date
    end_date: date
    quantity_array: DateArray | None = None
    quantity_unit: QuantityUnit

    @model_validator(mode="after")
    def set_quantity_array(self):
        self.quantity_array = DateArray(_start_date=self.start_date, _end_date=self.end_date)
        return self


class ConsumptionPrice(BaseModel):
    start_date: date
    end_date: date
    price: float
    price_unit: PriceUnit
    quantity_unit: QuantityUnit
    vat_level: VATRate


class SubscriptionPrice(BaseModel):
    start_date: date
    end_date: date
    price: float
    price_unit: PriceUnit
    time_unit: TimeUnit
    vat_level: VATRate


class TransportPrice(BaseModel):
    start_date: date
    end_date: date
    price: float
    price_unit: PriceUnit
    time_unit: TimeUnit
    vat_level: VATRate


class EnergyTaxes(BaseModel):
    start_date: date
    end_date: date
    price: float
    price_unit: PriceUnit
    quantity_unit: QuantityUnit
    vat_level: VATRate
