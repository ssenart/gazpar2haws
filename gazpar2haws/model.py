from datetime import date

from pydantic import BaseModel, model_validator

from gazpar2haws.date_array import DateArray
from gazpar2haws.configuration import PriceUnit, QuantityUnit, TimeUnit

from typing import Optional


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
    quantity_array: Optional[DateArray] = None
    quantity_unit: QuantityUnit

    @model_validator(mode="after")
    def set_quantity_array(self):
        self.quantity_array = DateArray(start_date=self.start_date, end_date=self.end_date)
        return self


class ConsumptionPriceArray(BaseModel):
    start_date: date
    end_date: date
    price_array: Optional[DateArray] = None
    price_unit: PriceUnit
    quantity_unit: QuantityUnit
    vat_id: str

    @model_validator(mode="after")
    def set_quantity_array(self):
        self.quantity_array = DateArray(start_date=self.start_date, end_date=self.end_date)
        return self


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
