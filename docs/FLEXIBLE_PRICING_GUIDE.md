# Flexible Pricing Components Guide

## Overview

Starting with version 0.5.0, gazpar2haws supports **flexible pricing components** with custom names. You can now define any pricing component names that make sense for your configuration, instead of being limited to the four hardcoded names.

## Backward Compatibility

**Important:** This feature is 100% backward compatible. If you have existing configurations using the traditional field names (`consumption_prices`, `subscription_prices`, `transport_prices`, `energy_taxes`), they will continue to work exactly as before without any changes required.

## Traditional Format (Still Supported)

The traditional format with fixed field names continues to work:

```yaml
pricing:
  vat:
    - id: std_rate
      start_date: 2023-01-01
      rate: 0.2

  consumption_prices:
    - start_date: 2023-01-01
      quantity_value: 0.08
      vat_id: std_rate

  subscription_prices:
    - start_date: 2023-01-01
      time_value: 12.0
      vat_id: std_rate

  transport_prices:
    - start_date: 2023-01-01
      quantity_value: 0.02

  energy_taxes:
    - start_date: 2023-01-01
      quantity_value: 0.01
```

## New Flexible Format

You can now use any component names you want:

```yaml
pricing:
  vat:
    - id: std_rate
      start_date: 2023-01-01
      rate: 0.2

  # Custom component names
  my_consumption:
    - start_date: 2023-01-01
      quantity_value: 0.08
      vat_id: std_rate

  my_subscription:
    - start_date: 2023-01-01
      time_value: 12.0
      vat_id: std_rate

  distribution_cost:
    - start_date: 2023-01-01
      quantity_value: 0.02

  carbon_tax:
    - start_date: 2023-01-01
      quantity_value: 0.005

  renewable_energy_fee:
    - start_date: 2023-01-01
      quantity_value: 0.003
```

## Key Features

### 1. Unlimited Components

You can define as many pricing components as you need, not just 4:

```yaml
pricing:
  base_consumption: [...]
  peak_consumption: [...]
  off_peak_consumption: [...]
  network_fee: [...]
  distribution_fee: [...]
  green_energy_surcharge: [...]
  carbon_tax: [...]
  # ... and more!
```

### 2. Meaningful Names

Use names that reflect your actual billing structure:

- **France:** `acheminement`, `fourniture`, `taxes`
- **Germany:** `grundpreis`, `arbeitspreis`, `netzentgelt`
- **Custom:** `peak_rate`, `off_peak_rate`, `demand_charge`

### 3. Automatic Sensor Creation

Home Assistant sensors are automatically created for each component:

- Traditional: `sensor.gazpar_consumption_cost`, `sensor.gazpar_subscription_cost`
- Custom: `sensor.gazpar_my_consumption_cost`, `sensor.gazpar_carbon_tax_cost`

Component names are converted to friendly names automatically:
- `my_consumption` → "Gazpar2HAWS My Consumption Cost"
- `carbon_tax` → "Gazpar2HAWS Carbon Tax Cost"

### 4. Backward Compatible Sensor Names

When using traditional field names, sensor names remain unchanged:
- `consumption_prices` → `sensor.gazpar_consumption_cost` (not `consumption_prices_cost`)
- `subscription_prices` → `sensor.gazpar_subscription_cost`
- `transport_prices` → `sensor.gazpar_transport_cost`
- `energy_taxes` → `sensor.gazpar_energy_taxes_cost`

## Validation Rules

### Required: At Least One Quantity-Based Component

You must have at least one component with `quantity_value` defined (consumption-based pricing):

```yaml
# ❌ Invalid - only time-based components
pricing:
  subscription:
    - start_date: 2023-01-01
      time_value: 10.0

# ✅ Valid - has quantity-based component
pricing:
  consumption:
    - start_date: 2023-01-01
      quantity_value: 0.08
  subscription:
    - start_date: 2023-01-01
      time_value: 10.0
```

### Component Name Format

Component names must be alphanumeric with underscores or hyphens:

```yaml
# ✅ Valid names
my_consumption: [...]
peak-rate: [...]
component1: [...]

# ❌ Invalid names
my component: [...]    # spaces not allowed
my.consumption: [...]  # dots not allowed
```

### Reserved Name

The name `vat` is reserved and cannot be used as a component name:

```yaml
# ❌ Invalid - 'vat' is reserved
vat:  # This is for VAT rates
  - id: std_rate
    rate: 0.2
vat:  # ❌ Cannot use as component name
  - start_date: 2023-01-01
    quantity_value: 0.1
```

## Migration Examples

### Example 1: From 4 Components to Custom Names

**Before (v0.4.x):**
```yaml
pricing:
  consumption_prices:
    - start_date: 2023-01-01
      quantity_value: 0.08
  subscription_prices:
    - start_date: 2023-01-01
      time_value: 12.0
  transport_prices:
    - start_date: 2023-01-01
      quantity_value: 0.02
  energy_taxes:
    - start_date: 2023-01-01
      quantity_value: 0.01
```

**After (v0.5.0 - Option 1: No change needed):**
```yaml
# Keep the same configuration - it still works!
pricing:
  consumption_prices: [...]
  subscription_prices: [...]
  transport_prices: [...]
  energy_taxes: [...]
```

**After (v0.5.0 - Option 2: Use custom names):**
```yaml
pricing:
  energy_consumption:
    - start_date: 2023-01-01
      quantity_value: 0.08
  monthly_subscription:
    - start_date: 2023-01-01
      time_value: 12.0
  network_costs:
    - start_date: 2023-01-01
      quantity_value: 0.02
  government_taxes:
    - start_date: 2023-01-01
      quantity_value: 0.01
```

### Example 2: Adding More Than 4 Components

```yaml
pricing:
  # Base consumption (required - has quantity_value)
  base_consumption:
    - start_date: 2023-01-01
      end_date: 2023-06-01
      quantity_value: 0.06
    - start_date: 2023-06-01
      quantity_value: 0.065

  # Peak pricing (optional)
  peak_surcharge:
    - start_date: 2023-01-01
      quantity_value: 0.02

  # Monthly fees (optional)
  subscription_fee:
    - start_date: 2023-01-01
      time_value: 8.50

  # Infrastructure costs (optional)
  distribution_network:
    - start_date: 2023-01-01
      quantity_value: 0.015

  transmission_network:
    - start_date: 2023-01-01
      quantity_value: 0.01

  # Taxes and surcharges (optional)
  carbon_tax:
    - start_date: 2023-01-01
      quantity_value: 0.005

  renewable_energy_contribution:
    - start_date: 2023-01-01
      quantity_value: 0.003
```

## Accessing Cost Components Programmatically

### In Python Code

```python
from gazpar2haws.configuration import Configuration
from gazpar2haws.pricer import Pricer

# Load configuration
config = Configuration.load("configuration.yaml", "secrets.yaml")

# Access components
components = config.pricing.get_components()
print(f"Available components: {list(components.keys())}")

# Compute costs
pricer = Pricer(config.pricing)
cost_breakdown = pricer.compute(quantities, price_unit)

# Access component costs
for component_name, cost_array in cost_breakdown.get_component_costs().items():
    print(f"{component_name}: {cost_array.value_array[date]}")

# Backward compatible access (if using traditional names)
if config.pricing.consumption_prices:
    print(f"Consumption: {cost_breakdown.consumption.value_array[date]}")
```

## Home Assistant Integration

### Sensors Created

For each pricing component, a sensor is created in Home Assistant:

**Traditional names:**
- `sensor.gazpar_consumption_cost`
- `sensor.gazpar_subscription_cost`
- `sensor.gazpar_transport_cost`
- `sensor.gazpar_energy_taxes_cost`
- `sensor.gazpar_total_cost`

**Custom names:**
- `sensor.gazpar_<component_name>_cost`
- `sensor.gazpar_total_cost`

### Example Lovelace Card

```yaml
type: entities
title: Gas Costs Breakdown
entities:
  - entity: sensor.gazpar_base_consumption_cost
    name: Base Consumption
  - entity: sensor.gazpar_peak_surcharge_cost
    name: Peak Surcharge
  - entity: sensor.gazpar_subscription_fee_cost
    name: Subscription
  - entity: sensor.gazpar_carbon_tax_cost
    name: Carbon Tax
  - type: divider
  - entity: sensor.gazpar_total_cost
    name: Total Cost
```

## Best Practices

1. **Use descriptive names:** Choose names that clearly describe what each component represents
2. **Keep backward compatibility:** If you have existing automations or dashboards, consider keeping traditional names
3. **Group related components:** Use consistent naming patterns (e.g., `tax_carbon`, `tax_vat`)
4. **Document your structure:** Add comments in your YAML to explain each component

## FAQ

**Q: Do I need to change my existing configuration?**
A: No! Existing configurations with traditional field names continue to work without any changes.

**Q: Can I mix traditional and custom names?**
A: Yes, you can use both:
```yaml
pricing:
  consumption_prices: [...]  # Traditional
  my_custom_fee: [...]       # Custom
```

**Q: Will my Home Assistant sensors change names?**
A: Only if you change your component names. Traditional field names maintain their original sensor names.

**Q: How many components can I have?**
A: As many as you need! There's no fixed limit.

**Q: Can I use different component names in different environments?**
A: Yes, component names are part of your configuration, so you can use different names for different installations.

## See Also

- [Configuration Guide](../README.md)
- [Implementation Plan](../IMPLEMENTATION_PLAN_FLEXIBLE_PRICING.md)
- [GitHub Issue #108](https://github.com/ssenart/gazpar2haws/issues/108)
