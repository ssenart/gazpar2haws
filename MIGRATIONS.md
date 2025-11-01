# Migration Guides

This document provides step-by-step instructions for upgrading Gazpar2HAWS between versions. If you're upgrading from an older version to the latest, you may need to follow migration steps for each intermediate version.

## Table of Contents

- [Upgrading from v0.3.x to v0.4.0](#upgrading-from-v03x-to-v040)
  - [What Changed](#what-changed)
  - [Breaking Changes](#breaking-changes)
  - [Migration Examples](#migration-examples)
  - [Migration Steps](#migration-steps)
  - [Automatic Sensor Migration](#automatic-sensor-migration)
  - [Validation Checklist](#validation-checklist)

---

## Upgrading from v0.3.x to v0.4.0

### What Changed

Version 0.4.0 introduces a new **composite price model** that provides significantly more flexibility in pricing configuration:

**New Features:**
- **Enhanced Cost Breakdown**: Separate entities for each cost component (consumption, subscription, transport, energy_taxes) plus total cost
- **Composite Prices**: Each price can have both a quantity component (€/kWh) and a time component (€/month)
- **Flexible Transport Pricing**: Transport can now be based on consumption (€/kWh) in addition to time-based (€/year)
- **Better Cost Analysis**: Track which components contribute most to your bill

**Example of New Entities:**
```
sensor.gazpar2haws_volume              (unchanged)
sensor.gazpar2haws_energy              (unchanged)
sensor.gazpar2haws_consumption_cost    (NEW)
sensor.gazpar2haws_subscription_cost   (NEW)
sensor.gazpar2haws_transport_cost      (NEW)
sensor.gazpar2haws_energy_taxes_cost   (NEW)
sensor.gazpar2haws_total_cost          (NEW)
```

### Breaking Changes

The pricing configuration format has changed to support the composite price model. The old properties are **deprecated** and must be migrated to the new format.

#### Deprecated Properties (v0.3.x)

- `value` - **Deprecated**: Use `quantity_value` or `time_value` instead
- `value_unit` - **Deprecated**: Use `price_unit` instead
- `base_unit` - **Deprecated**: Use `quantity_unit` or `time_unit` instead

#### New Properties (v0.4.0)

- `price_unit` - The monetary unit (€ or ¢) - applies to both components
- `quantity_value` - The numeric value for the quantity component (e.g., €/kWh)
- `quantity_unit` - The unit for quantity-based pricing (Wh, kWh, MWh)
- `time_value` - The numeric value for the time component (e.g., €/month)
- `time_unit` - The unit for time-based pricing (day, week, month, year)

#### Quick Reference Table

| Price Type | Old Format | New Format | Example |
|------------|------------|------------|---------|
| Consumption | `value: 0.07790` `base_unit: kWh` | `quantity_value: 0.07790` `quantity_unit: kWh` | €/kWh pricing |
| Subscription | `value: 19.83` `base_unit: month` | `time_value: 19.83` `time_unit: month` | €/month fee |
| Transport (fixed) | `value: 34.38` `base_unit: year` | `time_value: 34.38` `time_unit: year` | €/year fee |
| Transport (variable) | Not available | `quantity_value: 0.00194` `quantity_unit: kWh` | **NEW**: €/kWh fee |
| Energy Taxes | `value: 0.00837` `base_unit: kWh` | `quantity_value: 0.00837` `quantity_unit: kWh` | €/kWh tax |

---

### Migration Examples

#### Example 1: Simple Consumption Price

**Before (v0.3.x):**
```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01"
      value: 0.07790  # €/kWh
```

**After (v0.4.0):**
```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01"
      quantity_value: 0.07790  # €/kWh
```

**Explanation**: The `value` property is replaced by `quantity_value` since consumption is based on quantity (kWh).

---

#### Example 2: Consumption Price with Custom Units

**Before (v0.3.x):**
```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01"
      value: 7790.0
      value_unit: "¢"     # cents
      base_unit: "MWh"    # megawatt-hour
```

**After (v0.4.0):**
```yaml
pricing:
  consumption_prices:
    - start_date: "2023-06-01"
      quantity_value: 7790.0
      price_unit: "¢"      # cents
      quantity_unit: "MWh" # megawatt-hour
```

**Explanation**:
- `value` → `quantity_value`
- `value_unit` → `price_unit`
- `base_unit` → `quantity_unit`

---

#### Example 3: Subscription Price

**Before (v0.3.x):**
```yaml
pricing:
  subscription_prices:
    - start_date: "2023-06-01"
      value: 19.83
      value_unit: "€"
      base_unit: "month"
      vat_id: "reduced"
```

**After (v0.4.0):**
```yaml
pricing:
  subscription_prices:
    - start_date: "2023-06-01"
      time_value: 19.83
      price_unit: "€"
      time_unit: "month"
      vat_id: "reduced"
```

**Explanation**:
- `value` → `time_value` (since subscription is time-based)
- `value_unit` → `price_unit`
- `base_unit` → `time_unit`

---

#### Example 4: Transport Price (Fixed Fee)

**Before (v0.3.x):**
```yaml
pricing:
  transport_prices:
    - start_date: "2023-06-01"
      value: 34.38
      value_unit: "€"
      base_unit: "year"
      vat_id: "reduced"
```

**After (v0.4.0):**
```yaml
pricing:
  transport_prices:
    - start_date: "2023-06-01"
      time_value: 34.38
      price_unit: "€"
      time_unit: "year"
      vat_id: "reduced"
```

**Explanation**: Transport as a fixed annual fee uses the time component.

---

#### Example 5: Transport Price (Based on Consumption)

**New capability in v0.4.0 - not available in v0.3.x:**

```yaml
pricing:
  transport_prices:
    - start_date: "2024-01-01"
      quantity_value: 0.00194
      price_unit: "€"
      quantity_unit: "kWh"
      vat_id: "reduced"
```

**Explanation**: Transport can now be quantity-based (€/kWh) instead of only time-based.

---

#### Example 6: Energy Taxes

**Before (v0.3.x):**
```yaml
pricing:
  energy_taxes:
    - start_date: "2023-06-01"
      value: 0.00837
      value_unit: "€"
      base_unit: "kWh"
      vat_id: "normal"
```

**After (v0.4.0):**
```yaml
pricing:
  energy_taxes:
    - start_date: "2023-06-01"
      quantity_value: 0.00837
      price_unit: "€"
      quantity_unit: "kWh"
      vat_id: "normal"
```

**Explanation**: Energy taxes are quantity-based, so use `quantity_value` and `quantity_unit`.

---

#### Example 7: Complete Configuration Migration

**Before (v0.3.x):**
```yaml
pricing:
  vat:
    - id: reduced
      start_date: "2023-06-01"
      value: 0.0550
    - id: normal
      start_date: "2023-06-01"
      value: 0.20
  consumption_prices:
    - start_date: "2023-06-01"
      value: 0.07790
      value_unit: "€"
      base_unit: "kWh"
      vat_id: "normal"
  subscription_prices:
    - start_date: "2023-06-01"
      value: 19.83
      value_unit: "€"
      base_unit: "month"
      vat_id: "reduced"
  transport_prices:
    - start_date: "2023-06-01"
      value: 34.38
      value_unit: "€"
      base_unit: "year"
      vat_id: "reduced"
  energy_taxes:
    - start_date: "2023-06-01"
      value: 0.00837
      value_unit: "€"
      base_unit: "kWh"
      vat_id: "normal"
```

**After (v0.4.0):**
```yaml
pricing:
  vat:
    - id: reduced
      start_date: "2023-06-01"
      value: 0.0550
    - id: normal
      start_date: "2023-06-01"
      value: 0.20
  consumption_prices:
    - start_date: "2023-06-01"
      quantity_value: 0.07790
      quantity_unit: "kWh"  # Optional - default is kWh
      price_unit: "€"       # Optional - default is €
      vat_id: "normal"
  subscription_prices:
    - start_date: "2023-06-01"
      time_value: 19.83
      time_unit: "month"    # Optional - default is month
      price_unit: "€"       # Optional - default is €
      vat_id: "reduced"
  transport_prices:
    - start_date: "2023-06-01"
      time_value: 34.38
      time_unit: "year"
      price_unit: "€"
      vat_id: "reduced"
  energy_taxes:
    - start_date: "2023-06-01"
      quantity_value: 0.00837
      quantity_unit: "kWh"  # Optional - default is kWh
      price_unit: "€"       # Optional - default is €
      vat_id: "normal"
```

**Note**: The unit properties are optional. If omitted, the defaults are:
- `price_unit`: € (euro)
- `quantity_unit`: kWh (kilowatt-hour)
- `time_unit`: month

---

### Migration Steps

**Step 1: Backup your configuration file**
```bash
cp configuration.yaml configuration.yaml.backup
```

**Step 2: Update pricing section**

Use the examples above as a guide:
- Replace `value` with `quantity_value` or `time_value` depending on the price type
- Replace `value_unit` with `price_unit`
- Replace `base_unit` with `quantity_unit` or `time_unit` depending on the price type

**Reference the Quick Reference Table above** to determine which format to use for each price type.

**Step 3: Validate your configuration**
- Start the application and check the logs for any parsing errors
- The application will report if any deprecated properties are found
- Check for syntax errors: `python -m yaml config/configuration.yaml`

**Step 4: Test with a short period first**
```yaml
grdf:
  devices:
    - last_days: 7  # Temporarily set to 7 days
```

- Verify that cost calculations match your expectations
- Once validated, restore your original `last_days` value

**Step 5: Deploy updated configuration**
- If using Docker: Rebuild and restart container
- If using HA add-on: Update configuration through UI and restart add-on
- If using standalone: Stop application, update file, restart

---

### Automatic Sensor Migration

When you upgrade from v0.3.x to v0.4.0, Gazpar2HAWS **automatically handles migration of historical cost data** from the old sensor to the new one.

#### What Happens Automatically

**Old Sensor:** `sensor.{name}_cost`
**New Sensor:** `sensor.{name}_total_cost`

On the first run with v0.4.0:

1. **Detection**: The application checks if your old `sensor.{name}_cost` has historical data in Home Assistant
2. **Smart Logic**:
   - If old sensor exists AND new doesn't exist → **AUTO-MIGRATE** all historical data
   - If both sensors exist → **SKIP** to prevent data loss (you can manually delete old sensor)
   - If only new sensor exists → **SKIP** (normal operation, no migration needed)
3. **Data Transfer**: All historical statistics from the old sensor are copied to the new sensor
4. **Old Sensor**: Remains in Home Assistant for reference (can be manually hidden or deleted)

#### No Action Required

You **do not need to do anything** - the migration happens automatically during the first run with v0.4.0 when pricing configuration is enabled.

**Check the logs** after the first run:
```
INFO gazpar2haws.haws: Starting automatic migration: sensor.gazpar2haws_cost → sensor.gazpar2haws_total_cost
INFO gazpar2haws.haws: Successfully migrated 365 statistics entries from sensor.gazpar2haws_cost to sensor.gazpar2haws_total_cost
```

#### Troubleshooting Automatic Migration

**Problem**: "Both old sensor and new sensor exist. Skipping migration..."

**Cause**: The new sensor was created before migration ran

**Solution**:
1. Check if you manually created `sensor.{name}_total_cost`
2. If yes, you can safely delete the old `sensor.{name}_cost` sensor
3. Or, if needed, manually query the old sensor's data and import it to the new one

---

**Problem**: "No historical data found in sensor.gazpar2haws_cost - nothing to migrate"

**Cause**: The old sensor exists but has no historical data

**Solution**: This is normal. The application will continue with normal operation.

---

**Problem**: "Error during statistic migration... Continuing without migration"

**Cause**: WebSocket or HA communication issue during migration attempt

**Solution**:
1. Check your Home Assistant logs for connectivity issues
2. Verify the HA token is valid
3. Restart the application/add-on
4. The application continues safely - old data is preserved in the old sensor for manual recovery

---

### Validation Checklist

After migration, verify:

- [ ] Configuration file syntax is valid (no YAML errors)
- [ ] Application starts without errors in the logs
- [ ] All deprecated properties (`value`, `value_unit`, `base_unit`) are removed
- [ ] New properties (`quantity_value` or `time_value`, `price_unit`, `quantity_unit` or `time_unit`) are used
- [ ] All price types have appropriate component (quantity for consumption/taxes, time for subscription)
- [ ] Transport prices use either time component (fixed) or quantity component (variable), not both
- [ ] VAT references still exist and match declared VAT IDs
- [ ] New cost breakdown entities appear in Home Assistant:
  - `sensor.{name}_consumption_cost`
  - `sensor.{name}_subscription_cost`
  - `sensor.{name}_transport_cost`
  - `sensor.{name}_energy_taxes_cost`
  - `sensor.{name}_total_cost`
- [ ] Cost values in Home Assistant match your expectations
- [ ] Automatic sensor migration completed successfully (check logs for migration messages)
- [ ] Historical data from old `sensor.{name}_cost` has been copied to new `sensor.{name}_total_cost`
- [ ] New `sensor.{name}_total_cost` contains all historical data from before the upgrade

---

### Troubleshooting Migration Issues

#### Problem: "Configuration parsing error: unknown field 'value'"

**Cause**: Old v0.3.x properties still in configuration

**Solution**: Replace all `value` properties with `quantity_value` or `time_value` as appropriate for the price type.

---

#### Problem: "Deprecated property detected: value_unit"

**Cause**: Using old `value_unit` property instead of `price_unit`

**Solution**: Rename `value_unit` to `price_unit` in all price lists.

---

#### Problem: "Deprecated property detected: base_unit"

**Cause**: Using old `base_unit` property instead of `quantity_unit` or `time_unit`

**Solution**:
- For consumption/energy_taxes: Change `base_unit` to `quantity_unit`
- For subscription/transport: Change `base_unit` to `time_unit`

---

#### Problem: Cost calculations are very different from v0.3.x

**Cause**: Likely mismatch between quantity and time components

**Solution**: Verify each price type uses correct component:
- Consumption: Only `quantity_value`, no `time_value`
- Subscription: Only `time_value`, no `quantity_value`
- Transport: Either `quantity_value` OR `time_value`, not both
- Energy_taxes: Only `quantity_value`, no `time_value`

---

#### Problem: Home Assistant shows old cost entity but not new breakdown entities

**Cause**: New entities might not be created if pricing configuration has errors

**Solution**:
1. Check application logs for parsing errors
2. Validate configuration with a YAML linter
3. Verify all required properties are present and correctly named
4. Restart the application/add-on

---

## Future Migration Guides

When upgrading to future versions, additional migration guides will be documented here.

