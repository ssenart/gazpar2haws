# Implementation Plan: Flexible Pricing Components

## Objective
Allow users to define custom pricing component names (e.g., `my_consumption`, `carbon_tax`, `distribution_cost`) instead of being limited to 4 hardcoded names (`consumption_prices`, `subscription_prices`, `transport_prices`, `energy_taxes`), while maintaining full backward compatibility.

## Design Approach

### Core Strategy: Hybrid Dict-Based Model
- Convert `Pricing` class from fixed fields to `components: dict[str, list[CompositePriceValue]]`
- Use Pydantic `@model_validator(mode="before")` to automatically convert legacy field names to components dict
- Provide backward compatibility properties for legacy code access
- Dynamically create Home Assistant sensors based on actual component names

### Backward Compatibility Guarantee
Users keeping existing field names (`consumption_prices`, etc.) will experience **ZERO breaking changes**:
- Configuration loads unchanged
- Sensor names remain identical
- No migration required

## Critical Files to Modify

### 1. `gazpar2haws/model.py` (lines 231-298)
**Current structure:**
- 4 hardcoded fields: `consumption_prices`, `subscription_prices`, `transport_prices`, `energy_taxes`
- Fixed validator loop over hardcoded list (lines 248-253)
- Fixed `CostBreakdown` with 4 cost arrays (lines 294-298)

**Changes needed:**
- Replace fixed fields with `components: dict[str, list[CompositePriceValue]]`
- Add `convert_legacy_fields` validator to convert old format to new
- Update `propagates_properties` validator to work with dict
- Add validation: at least one quantity-based component, valid component names, reserved name check
- Add backward compatibility properties (e.g., `@property consumption_prices`)
- Transform `CostBreakdown` to use `components: dict[str, CostArray]` + `total`
- Add `__getattr__` to CostBreakdown for legacy component access

### 2. `gazpar2haws/pricer.py` (lines 74-218)
**Current structure:**
- Lines 74-145: Individual processing for each of 4 components with conditional logic
- Lines 148-218: Individual cost calculation for each component

**Changes needed:**
- Replace hardcoded processing with single loop: `for component_name, composite_prices in self._pricing.components.items()`
- Each iteration: call `get_composite_price_array()`, create `CostArray`, calculate cost
- Accumulate all component costs to total
- Return `CostBreakdown(components=component_costs, total=total_cost)`

### 3. `gazpar2haws/gazpar.py` (lines 95-320)
**Current structure:**
- Hardcoded sensor name definitions (lines 95-99)
- Hardcoded sensor management (lines 129-183)
- Hardcoded cost publishing (lines 300-324)

**Changes needed:**
- Generate sensor names dynamically: `{device_name}_{component_name}_cost`
- For backward compatibility: map legacy field names to legacy sensor names
  - `consumption_prices` → `consumption_cost` (not `consumption_prices_cost`)
- Add helper method `_generate_friendly_name()` to convert component names to friendly names
- Loop over `cost_breakdown.components.items()` to publish all costs
- Update sensor cleanup, lookup, and publishing logic to handle dynamic components

### 4. `addons/gazpar2haws/rootfs/app/run.sh` (lines 17-25)
**Current structure:**
- Hardcoded jq extraction for each of 4 components
- Manual JSON construction with fixed keys

**Changes needed:**
- Detect format: check if `components` key exists
- If new format: extract `components` dict directly
- If legacy format: extract individual fields (Pydantic validator will convert)
- Simplest approach: let Pydantic handle conversion automatically

### 5. `tests/test_pricer.py`
**Changes needed:**
- Update `test_compute()` (lines 315-348): assert on `cost_breakdown.components` dict
- Test legacy property access still works: `cost_breakdown.consumption`
- All example tests should continue working unchanged (use helper methods)

**New tests to add:**
- `test_flexible_pricing.py`: New components format, custom names, validation rules
- `test_backward_compatibility.py`: Legacy configs load correctly, produce same results

## Implementation Steps

### Step 1: Data Model Transformation (model.py)

1. **Update Pricing class:**
```python
class Pricing(BaseModel):
    vat: Optional[list[VatRate]] = None
    components: dict[str, list[CompositePriceValue]]
```

2. **Add legacy conversion validator:**
```python
@model_validator(mode="before")
@classmethod
def convert_legacy_fields(cls, values):
    if "components" in values:
        return values  # New format

    # Convert legacy fields to components dict
    components = {}
    for field_name in ["consumption_prices", "subscription_prices",
                       "transport_prices", "energy_taxes"]:
        if field_name in values and values[field_name] is not None:
            components[field_name] = values.pop(field_name)

    if components:
        values["components"] = components
    return values
```

3. **Update propagates_properties validator:**
   - Change loop from `for price_list in [...]` to `for component_name, prices in components.items()`
   - Same logic, just iterate over dict instead of fixed list

4. **Add validation rules:**
```python
@model_validator(mode="after")
def validate_components(self):
    if not self.components:
        raise ValueError("At least one pricing component is required")

    if "vat" in self.components:
        raise ValueError("'vat' is reserved and cannot be a component name")

    # Validate component names (alphanumeric + underscore)
    for name in self.components.keys():
        if not name.replace("_", "").isalnum():
            raise ValueError(f"Component name '{name}' must be alphanumeric with underscores")

    # At least one quantity-based component required
    has_quantity = any(
        any(p.quantity_value is not None for p in prices)
        for prices in self.components.values()
    )
    if not has_quantity:
        raise ValueError("At least one component must have quantity_value defined")

    return self
```

5. **Add backward compatibility properties:**
```python
@property
def consumption_prices(self) -> Optional[list[CompositePriceValue]]:
    return self.components.get("consumption_prices")
# ... repeat for other legacy fields
```

6. **Update CostBreakdown:**
```python
class CostBreakdown(BaseModel):
    components: dict[str, CostArray]
    total: CostArray

    def __getattr__(self, name: str) -> CostArray:
        # Map legacy names: consumption → consumption_prices component
        legacy_map = {
            "consumption": "consumption_prices",
            "subscription": "subscription_prices",
            "transport": "transport_prices",
            "energy_taxes": "energy_taxes",
        }
        if name in legacy_map:
            component_name = legacy_map[name]
            if component_name in self.components:
                return self.components[component_name]
            # Return empty CostArray for missing components
            return CostArray(...)  # With zeros
        raise AttributeError(f"No attribute '{name}'")
```

### Step 2: Pricer Refactoring (pricer.py)

Replace hardcoded processing (lines 74-218) with generic loop:

```python
def compute(self, quantities: ConsumptionQuantityArray, price_unit: PriceUnit) -> CostBreakdown:
    # ... existing setup code ...

    # Get VAT arrays
    if self._pricing.vat is not None and len(self._pricing.vat) > 0:
        vat_rate_array_by_id = self.get_vat_rate_array_by_id(...)
    else:
        vat_rate_array_by_id = {}

    # Process all components dynamically
    component_costs = {}
    total_cost_array = None

    for component_name, composite_prices in self._pricing.components.items():
        # Get composite price array
        composite_array = self.get_composite_price_array(
            start_date=start_date,
            end_date=end_date,
            composite_prices=composite_prices,
            vat_rate_array_by_id=vat_rate_array_by_id,
            target_price_unit=price_unit,
            target_quantity_unit=quantities.value_unit,
            target_time_unit=quantities.base_unit,
        )

        # Calculate cost
        component_cost = CostArray(
            name=f"{component_name}_cost",
            start_date=start_date,
            end_date=end_date,
            value_unit=price_unit,
            base_unit=quantities.base_unit,
        )
        component_cost.value_array = (
            quantity_array * composite_array.quantity_value_array
            + composite_array.time_value_array
        )

        component_costs[component_name] = component_cost

        # Accumulate to total
        if total_cost_array is None:
            total_cost_array = component_cost.value_array.copy()
        else:
            total_cost_array = total_cost_array + component_cost.value_array

    # Create total cost
    total_cost = CostArray(
        name="total_cost",
        start_date=start_date,
        end_date=end_date,
        value_unit=price_unit,
        base_unit=quantities.base_unit,
    )
    total_cost.value_array = total_cost_array

    return CostBreakdown(components=component_costs, total=total_cost)
```

### Step 3: Home Assistant Integration (gazpar.py)

1. **Dynamic sensor name generation:**
```python
# Generate component sensor names dynamically
component_sensor_names = {}
if self._pricing_config is not None:
    for component_name in self._pricing_config.components.keys():
        # Use legacy sensor names for backward compatibility
        sensor_suffix = self._get_legacy_sensor_suffix(component_name)
        sensor_name = f"sensor.{self._name}_{sensor_suffix}"
        component_sensor_names[component_name] = sensor_name

def _get_legacy_sensor_suffix(self, component_name: str) -> str:
    """Map legacy field names to legacy sensor suffixes for backward compatibility."""
    legacy_map = {
        "consumption_prices": "consumption_cost",
        "subscription_prices": "subscription_cost",
        "transport_prices": "transport_cost",
        "energy_taxes": "energy_taxes_cost",
    }
    return legacy_map.get(component_name, f"{component_name}_cost")
```

2. **Update sensor reset, lookup, and publishing:**
   - Loop over `component_sensor_names.items()` instead of hardcoded list
   - Same logic, just dynamic iteration

3. **Publish costs dynamically:**
```python
# Publish each component cost
for component_name, component_cost in cost_breakdown.components.items():
    sensor_name = component_sensor_names[component_name]
    friendly_name = self._generate_friendly_name(component_name)

    await self.publish_date_array(
        sensor_name,
        friendly_name,
        None,
        self._convert_euro_symbol_to_iso4217(component_cost.value_unit),
        component_cost.value_array,
        last_date_and_value[sensor_name][1],
    )
```

4. **Add friendly name generator:**
```python
def _generate_friendly_name(self, component_name: str) -> str:
    """Convert component name to friendly sensor name."""
    # Legacy names get legacy friendly names
    legacy_friendly = {
        "consumption_prices": "Gazpar2HAWS Consumption Cost",
        "subscription_prices": "Gazpar2HAWS Subscription Cost",
        "transport_prices": "Gazpar2HAWS Transport Cost",
        "energy_taxes": "Gazpar2HAWS Energy Taxes Cost",
    }
    if component_name in legacy_friendly:
        return legacy_friendly[component_name]

    # Custom names: convert snake_case to Title Case
    words = component_name.replace("_", " ").title()
    return f"Gazpar2HAWS {words} Cost"
```

### Step 4: Shell Script Update (run.sh)

Simplest approach - let Pydantic handle conversion:

```bash
# Extract pricing section as-is (supports both formats)
PRICING_JSON=$(jq --raw-output '. | { pricing: . }' $CONFIG_PATH)
PRICING_CONFIG=$(echo $PRICING_JSON | yq -P)
```

The model validator will automatically convert legacy fields to components dict.

### Step 5: Testing

1. **Update existing tests (test_pricer.py):**
   - `test_compute()`: Add assertions for `cost_breakdown.components` dict
   - Verify legacy property access works: `cost_breakdown.consumption`
   - Helper methods should work unchanged

2. **Add new test file (test_flexible_pricing.py):**
   - Test new components format loads correctly
   - Test custom component names work
   - Test validation rules (at least one quantity, valid names, reserved names)
   - Test mixed quantity/time components

3. **Add backward compatibility tests:**
   - Test legacy configs load unchanged
   - Test legacy configs produce same cost calculations
   - Test legacy property access on Pricing and CostBreakdown

### Step 6: Documentation

1. **README.md:** Add flexible pricing examples
2. **MIGRATIONS.md:** Document the change with migration examples
3. **FAQ.md:** Answer common questions about custom components
4. **Configuration examples:** Add `config/examples/flexible_pricing_*.yaml`

## Verification Steps

### Unit Tests
```bash
pytest tests/test_pricer.py -v
pytest tests/test_flexible_pricing.py -v
```

### Integration Test
1. Create test config with custom components
2. Run gazpar2haws with new config
3. Verify sensors created in Home Assistant with correct names
4. Verify cost calculations are accurate

### Backward Compatibility Test
1. Use existing `tests/config/configuration.yaml` unchanged
2. Run all existing tests - should pass
3. Verify sensor names remain: `consumption_cost`, `subscription_cost`, etc.

### Type Safety
```bash
mypy gazpar2haws/ --strict
```

## Risk Mitigation

### High-Risk Areas
1. **Backward compatibility:** Mitigated by comprehensive validator and property access
2. **Sensor naming changes:** Mitigated by legacy name mapping
3. **Type safety:** Mitigated by proper type hints and runtime validation

### Success Criteria
- [ ] All existing tests pass unchanged
- [ ] New flexible pricing tests pass
- [ ] Legacy configs load without changes
- [ ] Custom component names work
- [ ] Sensors created dynamically
- [ ] Documentation complete
- [ ] Type checking passes

## Estimated Implementation Time
- Data model changes: 2-3 hours
- Pricer refactoring: 1-2 hours
- Home Assistant integration: 2-3 hours
- Shell script: 30 minutes
- Testing: 2-3 hours
- Documentation: 1-2 hours
**Total: 1-2 days**

## Related GitHub Issue
Issue #108: https://github.com/ssenart/gazpar2haws/issues/108
