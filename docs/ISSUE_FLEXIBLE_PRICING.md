## Summary

Currently, the configuration supports only 4 hardcoded price component keywords under `pricing`:
- `consumption_prices` (required)
- `subscription_prices` (optional)
- `transport_prices` (optional)
- `energy_taxes` (optional)

This proposal enables users to define **custom price component names** while maintaining full backward compatibility.

## Motivation

1. **Flexibility** - Energy markets vary by country and may have different cost structures
2. **Localization** - Users can use names in their native language (e.g., `taxes_énergie`, `transport_kosten`)
3. **Extensibility** - Users can add new price components without code changes (e.g., `carbon_tax`, `grid_maintenance`, `renewable_surcharge`)
4. **Clarity** - Meaningful names like `distribution_cost` are more descriptive than generic keywords

## Proposed Solution

### Hybrid Approach

Implement a flexible system with these principles:

1. **At least one quantity-based component is required** - Ensures basic cost calculation works
2. **Unlimited custom component names** - Users can add any components they need
3. **Backward compatible** - Existing configurations continue to work unchanged
4. **Consistent processing** - All components use the same data structure and logic

### Configuration Example

#### New Flexible Format
```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01"
      value: 0.20

  # Users can name components however they want
  my_consumption:
    - start_date: "2023-06-01"
      quantity_value: 0.07790
      price_unit: "€"
      quantity_unit: "kWh"
      vat_id: normal

  my_subscription:
    - start_date: "2023-06-01"
      time_value: 19.83
      price_unit: "€"
      time_unit: "month"
      vat_id: normal

  carbon_tax:
    - start_date: "2023-06-01"
      quantity_value: 0.01
      price_unit: "€"
      quantity_unit: "kWh"

  distribution_cost:
    - start_date: "2023-06-01"
      time_value: 34.38
      price_unit: "€"
      time_unit: "year"
```

#### Backward Compatible - Existing Format Still Works
```yaml
pricing:
  # Old naming still works exactly as before
  consumption_prices:
    - start_date: "2023-06-01"
      quantity_value: 0.07790
  subscription_prices:
    - start_date: "2023-06-01"
      time_value: 19.83
```

## Implementation Changes

### Files to Modify

1. **gazpar2haws/model.py** (lines 230-277)
   - Change `Pricing` class from fixed fields to dynamic dict
   - Update validator to process all components generically
   - Add validation that at least one quantity-based component exists

2. **gazpar2haws/pricer.py** (lines 37-218)
   - Replace hardcoded processing with loop over all components
   - Maintain same calculation logic for each component
   - Sum all components into total cost

3. **gazpar2haws/gazpar.py** (lines 85-320)
   - Dynamically create Home Assistant sensors based on component names
   - Sensor naming: `sensor.{device_name}_{component_name}_cost`
   - Add total cost sensor as before

4. **config/configuration.yaml** & **tests/config/configuration.yaml**
   - Update examples to show both old and new formats
   - Document the flexibility in comments

### Validation Rules

- Reserved name: `vat` (cannot be used as a price component)
- At least one component must have `quantity_value` defined (quantity-based pricing)
- Component names must be valid Python identifiers (alphanumeric + underscore)
- Each component must be a list of `CompositePriceValue` objects

## Backward Compatibility Guarantee

✅ **Users who keep existing names see ZERO breaking changes**

- Configuration files using `consumption_prices`, `subscription_prices`, `transport_prices`, `energy_taxes` continue to work
- Home Assistant sensor names remain unchanged
- No migration required for existing users
- Existing functionality is preserved exactly as-is

## Home Assistant Impact

### Current Sensors
```
sensor.gazpar2haws_consumption_cost
sensor.gazpar2haws_subscription_cost
sensor.gazpar2haws_transport_cost
sensor.gazpar2haws_energy_taxes_cost
sensor.gazpar2haws_total_cost
```

### With Custom Names
```
sensor.gazpar2haws_my_consumption_cost
sensor.gazpar2haws_my_subscription_cost
sensor.gazpar2haws_carbon_tax_cost
sensor.gazpar2haws_distribution_cost_cost
sensor.gazpar2haws_total_cost
```

The `total_cost` sensor always sums all components.

## Benefits

1. **No breaking changes** - Existing users unaffected
2. **International friendly** - Users can use localized names
3. **Future-proof** - New pricing models supported without code changes
4. **Simpler code** - Generic processing replaces hardcoded logic
5. **Better UX** - Sensors in Home Assistant have meaningful names

## Open Questions

1. Should we enforce a maximum number of components for performance?
2. Should component names be limited to certain characters/length?
3. Should we provide component name suggestions/templates in docs?

## Related

- Feature request from user: "Let the user decide to put any name he wants"
- Enhances configurability introduced in #102, #104
