from __future__ import annotations

import datetime as dt
from typing import Optional, overload

import numpy as np
from pydantic import BaseModel, ConfigDict, model_validator


class DateArray(BaseModel):  # pylint: disable=too-few-public-methods
    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_date: dt.date
    end_date: dt.date
    array: Optional[np.ndarray] = None
    initial_value: Optional[float] = None

    @model_validator(mode="after")
    def set_array(self):
        if self.array is None:
            if self.initial_value is not None:
                self.array = np.full((self.end_date - self.start_date).days + 1, self.initial_value)
            else:
                self.array = np.zeros((self.end_date - self.start_date).days + 1)
        return self

    # ----------------------------------
    def get(self, date: dt.date) -> float:

        if self.array is None:
            raise ValueError("Array is not initialized")

        return self.array[(date - self.start_date).days]

    # ----------------------------------
    def cumsum(self) -> DateArray:

        if self.array is None:
            raise ValueError("Array is not initialized")

        result = DateArray(start_date=self.start_date, end_date=self.end_date)
        result.array = np.cumsum(self.array)
        return result

    # ----------------------------------
    def is_aligned_with(self, other: DateArray) -> bool:

        return (
            self.start_date == other.start_date and self.end_date == other.end_date and len(self) == len(other)
        )  # pylint: disable=protected-access

    # ----------------------------------
    @overload
    def __getitem__(self, index: int) -> float: ...

    @overload
    def __getitem__(self, date: dt.date) -> float: ...

    @overload
    def __getitem__(self, date_slice: slice) -> np.ndarray: ...

    def __getitem__(self, key):
        if self.array is None:
            raise ValueError("Array is not initialized")
        if isinstance(key, int):
            return self.array[key]
        if isinstance(key, dt.date):
            return self.get(key)
        if isinstance(key, slice):
            start_date: dt.date = key.start  # type: ignore
            end_date: dt.date = key.stop  # type: ignore
            start_index: int = (start_date - self.start_date).days
            end_index: int = (end_date - self.start_date).days + 1
            return self.array[start_index:end_index]
        raise TypeError("Key must be a date or a slice of dates")

    # ----------------------------------
    @overload
    def __setitem__(self, index: int, value: float): ...

    @overload
    def __setitem__(self, date: dt.date, value: float): ...

    @overload
    def __setitem__(self, date_slice: slice, value: float): ...

    def __setitem__(self, key, value: float):
        if self.array is None:
            raise ValueError("Array is not initialized")
        if isinstance(key, int):
            self.array[key] = value
        elif isinstance(key, dt.date):
            self.array[(key - self.start_date).days] = value
        elif isinstance(key, slice):
            start_date: dt.date = key.start  # type: ignore
            end_date: dt.date = key.stop  # type: ignore
            start_index: int = (start_date - self.start_date).days
            end_index: int = (end_date - self.start_date).days + 1
            self.array[start_index:end_index] = value
        else:
            raise TypeError("Key must be a date or a slice of dates")

    # ----------------------------------
    def __len__(self) -> int:

        if self.array is None:
            raise ValueError("Array is not initialized")

        return len(self.array)

    # ----------------------------------
    def __iter__(self):
        self._index = 0  # pylint: disable=attribute-defined-outside-init
        return self

    # ----------------------------------
    def __next__(self):
        if self._index < len(self.array):
            current_date = self.start_date + dt.timedelta(days=self._index)
            result = (current_date, self.array[self._index])
            self._index += 1
            return result
        raise StopIteration

    # ----------------------------------
    @overload
    def __add__(self, other: DateArray) -> DateArray: ...

    @overload
    def __add__(self, other: float) -> DateArray: ...

    def __add__(self, other) -> DateArray:

        if self.array is None:
            raise ValueError("Array is not initialized")

        if isinstance(other, (int, float)):
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array + other
            return result
        if isinstance(other, DateArray):
            if other.array is None:
                raise ValueError("Array is not initialized")
            if not self.is_aligned_with(other):
                raise ValueError("Date arrays are not aligned")
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array + other.array  # pylint: disable=protected-access
            return result

        raise TypeError("Other must be a date array or a number")

    # ----------------------------------
    @overload
    def __sub__(self, other: DateArray) -> DateArray: ...

    @overload
    def __sub__(self, other: float) -> DateArray: ...

    def __sub__(self, other) -> DateArray:

        if self.array is None:
            raise ValueError("Array is not initialized")

        if isinstance(other, (int, float)):
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array - other
            return result
        if isinstance(other, DateArray):
            if other.array is None:
                raise ValueError("Array is not initialized")
            if not self.is_aligned_with(other):
                raise ValueError("Date arrays are not aligned")
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array - other.array  # pylint: disable=protected-access
            return result

        raise TypeError("Other must be a date array or a number")

    # ----------------------------------
    @overload
    def __mul__(self, other: DateArray) -> DateArray: ...

    @overload
    def __mul__(self, other: float) -> DateArray: ...

    def __mul__(self, other) -> DateArray:

        if self.array is None:
            raise ValueError("Array is not initialized")

        if isinstance(other, (int, float)):
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array * other
            return result
        if isinstance(other, DateArray):
            if other.array is None:
                raise ValueError("Array is not initialized")
            if not self.is_aligned_with(other):
                raise ValueError("Date arrays are not aligned")
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array * other.array  # pylint: disable=protected-access
            return result

        raise TypeError("Other must be a date array or a number")

    # ----------------------------------
    @overload
    def __truediv__(self, other: DateArray) -> DateArray: ...

    @overload
    def __truediv__(self, other: float) -> DateArray: ...

    def __truediv__(self, other) -> DateArray:

        if self.array is None:
            raise ValueError("Array is not initialized")

        if isinstance(other, (int, float)):
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array / other
            return result
        if isinstance(other, DateArray):
            if other.array is None:
                raise ValueError("Array is not initialized")
            if not self.is_aligned_with(other):
                raise ValueError("Date arrays are not aligned")
            result = DateArray(start_date=self.start_date, end_date=self.end_date)
            result.array = self.array / other.array  # pylint: disable=protected-access
            return result

        raise TypeError("Other must be a date array or a number")

    # ----------------------------------
    def __repr__(self) -> str:

        return f"DateArray(start_date={self.start_date}, end_date={self.end_date}, array={self.array})"
