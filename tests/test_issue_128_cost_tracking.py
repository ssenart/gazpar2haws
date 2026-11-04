"""Regression tests for GitHub issue #128 ("Suivi des coûts incorrect ?").

Each test encodes the expected (correct) behaviour. On the current code, the
tests marked as bugs are expected to FAIL, which confirms the issue.
"""

from datetime import date

import pytest

from gazpar2haws.date_array import DateArray
from gazpar2haws.model import (
    ConsumptionQuantityArray,
    PriceUnit,
    Pricing,
    QuantityUnit,
    TimeUnit,
)
from gazpar2haws.pricer import Pricer


def _zero_quantities(start: date, end: date) -> ConsumptionQuantityArray:
    """Zero consumption, so that the computed cost is only the fixed (time-based) part."""
    return ConsumptionQuantityArray(
        start_date=start,
        end_date=end,
        value_array=DateArray(start_date=start, end_date=end, initial_value=0.0),
        value_unit=QuantityUnit.KWH,
        base_unit=TimeUnit.DAY,
    )


def _subscription_pricing(subscription_entries: list[dict]) -> Pricing:
    """Pricing with a single consumption entry (required) and the given subscription entries."""
    return Pricing.model_validate(
        {
            "consumption_prices": [
                {"start_date": "2026-01-01", "quantity_value": 0.1, "price_unit": "€", "quantity_unit": "kWh"}
            ],
            "subscription_prices": subscription_entries,
        }
    )


def _daily_subscription_cost(pricing: Pricing, day: date) -> float:
    quantities = _zero_quantities(day, day)
    breakdown = Pricer(pricing).compute(quantities, PriceUnit.EURO)
    return float(breakdown.total.value_array[day])  # type: ignore


class TestIssue128SubscriptionDayCount:
    """Issue #128, point 1: a €/month subscription is divided by the day count of the wrong month."""

    def test_monthly_subscription_uses_days_of_the_month_being_priced(self):
        """A 30 €/month subscription costs 30/30 € per day in November, not 30/31 € (October's count)."""
        pricing = _subscription_pricing(
            [{"start_date": "2026-10-01", "time_value": 30.0, "price_unit": "€", "time_unit": "month"}]
        )

        # November 2026 has 30 days: the daily cost must be 30 / 30.
        assert _daily_subscription_cost(pricing, date(2026, 11, 15)) == _approx(30.0 / 30.0)

    def test_monthly_subscription_uses_days_of_october_for_october(self):
        """Control case: October 2026 has 31 days, so the daily cost is 30 / 31 (passes today)."""
        pricing = _subscription_pricing(
            [{"start_date": "2026-10-01", "time_value": 30.0, "price_unit": "€", "time_unit": "month"}]
        )

        assert _daily_subscription_cost(pricing, date(2026, 10, 15)) == _approx(30.0 / 31.0)


class TestIssue128PriceListOrder:
    """Issue #128, point 2 (suspected): the price list order changes the result.

    The add-on UI shows the subscription list newest first (2026-10-29 above 2026-10-01).
    model.py derives end dates from the next entry, so it assumes an ascending list.
    """

    ASCENDING = [
        {"start_date": "2026-10-01", "time_value": 32.32, "price_unit": "€", "time_unit": "month"},
        {"start_date": "2026-10-29", "time_value": 28.45, "price_unit": "€", "time_unit": "month"},
    ]
    DESCENDING = list(reversed(ASCENDING))

    def test_same_result_whatever_the_list_order(self):
        """The same prices in a different order must give the same daily costs."""
        start, end = date(2026, 10, 25), date(2026, 11, 5)
        quantities = _zero_quantities(start, end)

        asc = Pricer(_subscription_pricing(self.ASCENDING)).compute(quantities, PriceUnit.EURO)
        desc = Pricer(_subscription_pricing(self.DESCENDING)).compute(quantities, PriceUnit.EURO)

        for day in (date(2026, 10, 25), date(2026, 10, 30), date(2026, 11, 1), date(2026, 11, 5)):
            assert desc.total.value_array[day] == _approx(asc.total.value_array[day])  # type: ignore

    def test_november_uses_current_subscription_price(self):
        """From 2026-10-29 the price is 28.45 €/month, so November costs 28.45 / 30 € per day."""
        pricing = _subscription_pricing(self.DESCENDING)

        assert _daily_subscription_cost(pricing, date(2026, 11, 1)) == _approx(28.45 / 30.0)


def _approx(value: float):
    return pytest.approx(value, abs=1e-9)
