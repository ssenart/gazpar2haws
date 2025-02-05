"""Test the date_array module."""

from datetime import date

from gazpar2haws.date_array import DateArray


def test_date_array():

    date_array = DateArray(start_date=date(2021, 1, 1), end_date=date(2021, 1, 31))

    assert len(date_array) == 31

    assert date_array.is_aligned_with(date_array)

    date_array2 = DateArray(start_date=date(2021, 1, 1), end_date=date(2021, 1, 31))

    assert date_array.is_aligned_with(date_array2)

    date_array3 = DateArray(start_date=date(2021, 1, 1), end_date=date(2021, 1, 30))

    assert not date_array.is_aligned_with(date_array3)

    date_array4 = DateArray(start_date=date(2021, 1, 1), end_date=date(2021, 1, 31), initial_value=1)

    date_array5 = date_array + date_array4

    assert len(date_array5) == 31

    date_array6 = date_array - date_array4

    assert len(date_array6) == 31

    date_array7 = date_array * date_array4

    assert len(date_array7) == 31

    date_array8 = date_array / date_array4

    assert len(date_array8) == 31

    date_array9 = date_array + 1

    for i in range(31):
        assert date_array9[i] == 1  # pylint: disable=unsubscriptable-object

    date_array10 = date_array9 * 5

    for i in range(31):
        assert date_array10[i] == 5


def test_slice():

    date_array = DateArray(start_date=date(2021, 1, 1), end_date=date(2021, 1, 31), initial_value=1)

    date_array_slice = date_array[date(2021, 1, 1):date(2021, 1, 11)]

    assert len(date_array_slice) == 10

    date_array_slice2 = date_array[date(2021, 1, 1):date(2021, 1, 2)]

    assert len(date_array_slice2) == 1
