"""Tests for flexible pricing components."""

from datetime import date

from gazpar2haws.configuration import Configuration
from gazpar2haws.date_array import DateArray
from gazpar2haws.model import (
    ConsumptionQuantityArray,
    PriceUnit,
    QuantityUnit,
    TimeUnit,
)
from gazpar2haws.pricer import Pricer


class TestFlexiblePricing:
    """Test flexible pricing with custom component names."""

    def test_custom_component_names(self):
        """Test that custom component names work correctly."""
        config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

        # Verify components are accessible
        components = config.pricing.get_components()
        assert "consumption_prices" in components
        assert "subscription_prices" in components
        assert "transport_prices" in components
        assert "energy_taxes" in components

    def test_cost_breakdown_component_access(self):
        """Test that cost breakdown components can be accessed via get_component_costs()."""
        config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")
        pricer = Pricer(config.pricing)

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        # Create quantities
        quantities = ConsumptionQuantityArray(
            start_date=start_date,
            end_date=end_date,
            value_array=DateArray(start_date=start_date, end_date=end_date, initial_value=1.0),
            value_unit=QuantityUnit.KWH,
            base_unit=TimeUnit.DAY,
        )

        # Compute costs
        cost_breakdown = pricer.compute(quantities, PriceUnit.EURO)

        # Verify components accessible via get_component_costs()
        component_costs = cost_breakdown.get_component_costs()
        assert "consumption_prices" in component_costs
        assert "subscription_prices" in component_costs
        assert "transport_prices" in component_costs
        assert "energy_taxes" in component_costs

        # Verify each component cost has correct structure
        for _, cost_array in component_costs.items():
            assert cost_array.start_date == start_date
            assert cost_array.end_date == end_date
            assert cost_array.value_unit == "€"
            assert len(cost_array.value_array) == 6

    def test_backward_compatible_property_access(self):
        """Test that legacy property access still works on CostBreakdown."""
        config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")
        pricer = Pricer(config.pricing)

        start_date = date(2023, 8, 20)
        end_date = date(2023, 8, 25)

        # Create quantities
        quantities = ConsumptionQuantityArray(
            start_date=start_date,
            end_date=end_date,
            value_array=DateArray(start_date=start_date, end_date=end_date, initial_value=1.0),
            value_unit=QuantityUnit.KWH,
            base_unit=TimeUnit.DAY,
        )

        # Compute costs
        cost_breakdown = pricer.compute(quantities, PriceUnit.EURO)

        # Verify legacy property access works
        assert cost_breakdown.consumption is not None
        assert cost_breakdown.subscription is not None
        assert cost_breakdown.transport is not None
        assert cost_breakdown.energy_taxes is not None

        # Verify these are the same as accessing via get_component_costs()
        component_costs = cost_breakdown.get_component_costs()
        assert (
            cost_breakdown.consumption.value_array[start_date]
            == component_costs["consumption_prices"].value_array[start_date]
        )
        assert (
            cost_breakdown.subscription.value_array[start_date]
            == component_costs["subscription_prices"].value_array[start_date]
        )
        assert (
            cost_breakdown.transport.value_array[start_date]
            == component_costs["transport_prices"].value_array[start_date]
        )
        assert (
            cost_breakdown.energy_taxes.value_array[start_date]
            == component_costs["energy_taxes"].value_array[start_date]
        )

    def test_pricing_validation_requires_quantity_component(self):
        """Test that at least one quantity-based component is required."""
        from pydantic import ValidationError

        from gazpar2haws.model import Pricing

        # This should fail - no quantity-based component
        try:
            Pricing(
                subscription_prices=[
                    {
                        "start_date": date(2023, 1, 1),
                        "time_value": 10.0,
                    }
                ]
            )
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "At least one component must have quantity_value defined" in str(e)

    def test_pricing_validation_requires_at_least_one_component(self):
        """Test that at least one pricing component is required."""
        from pydantic import ValidationError

        from gazpar2haws.model import Pricing

        # This should fail - no components
        try:
            Pricing()
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "At least one pricing component is required" in str(e)
