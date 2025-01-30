from __future__ import annotations

import datetime as dt

import numpy as np

from pydantic import BaseModel, model_validator


class DateArray(BaseModel):

    start_date: dt.date
    end_date: dt.date
    array: np.ndarray | None = None

    @model_validator(mode="after")
    def set_array(self):
        self.array = np.zeros((self.end_date - self.start_date).days + 1)
        return self

    def get(self, date: dt.date) -> float:

        if self.array is None:
            raise ValueError("Array is not initialized")

        return self.array[(date - self.start_date).days]

    def __getitem__(self, date: dt.date) -> float:

        return self.get(date)

    def __setitem__(self, date: dt.date, value: float):

        if self.array is None:
            raise ValueError("Array is not initialized")

        self.array[(date - self.start_date).days] = value

    def __len__(self) -> int:

        if self.array is None:
            raise ValueError("Array is not initialized")

        return len(self.array)

    def is_aligned_with(self, other: DateArray) -> bool:

        return self.start_date == other.start_date and self.end_date == other.end_date and len(self) == len(other)  # pylint: disable=protected-access

    def __add__(self, other: DateArray) -> DateArray:

        if self.array is None or other.array is None:
            raise ValueError("Array is not initialized")

        if not self.is_aligned_with(other):
            raise ValueError("Date arrays are not aligned")

        result = DateArray(start_date=self.start_date, end_date=self.end_date)

        result.array = self.array + other.array  # pylint: disable=protected-access

        return result

    def __sub__(self, other: DateArray) -> DateArray:

        if self.array is None or other.array is None:
            raise ValueError("Array is not initialized")

        if not self.is_aligned_with(other):
            raise ValueError("Date arrays are not aligned")

        result = DateArray(start_date=self.start_date, end_date=self.end_date)

        result.array = self.array - other.array

        return result

    def __mul__(self, other: DateArray) -> DateArray:

        if self.array is None or other.array is None:
            raise ValueError("Array is not initialized")

        if not self.is_aligned_with(other):
            raise ValueError("Date arrays are not aligned")

        result = DateArray(start_date=self.start_date, end_date=self.end_date)

        result.array = self.array * other.array

        return result

    def __truediv__(self, other: DateArray) -> DateArray:

        if self.array is None or other.array is None:
            raise ValueError("Array is not initialized")

        if not self.is_aligned_with(other):
            raise ValueError("Date arrays are not aligned")

        result = DateArray(start_date=self.start_date, end_date=self.end_date)

        result.array = self.array / other.array

        return result
