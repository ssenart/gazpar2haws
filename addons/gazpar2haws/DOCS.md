# Home Assistant Add-on: Gazpar2HAWS add-on

## Configuration

The configuration permits to define multiple devices if you have multiple GrDF meters (meter1 and meter2 in the example above).

```yaml
scan_interval: 480
devices:
  - name: meter1
    username:
    password:
    pce_identifier:
    timezone: Europe/Paris
    last_days: 365
    reset: false
  - name: meter2
    username:
    password:
    pce_identifier:
    timezone: Europe/Paris
    last_days: 720
    reset: false
```

| Name                     | Description                                                                                                                                      | Required | Default value |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ------------- |
| scan_interval            | Period in minutes to refresh meter data (0 means one single refresh and stop)                                                                    | No       | 480 (8 hours) |
| devices[].name           | Name of the device in Home Assistant                                                                                                             | Yes      | -             |
| devices[].username       | GrDF account user name                                                                                                                           | Yes      | -             |
| devices[].password       | GrDF account password (avoid using special characters)                                                                                           | Yes      | -             |
| devices[].pce_identifier | GrDF meter PCE identifier                                                                                                                        | Yes      | -             |
| devices[].timezone       | Timezone of the GrDF data                                                                                                                        | No       | Europe/Paris  |
| devices[].last_days      | Number of days of history data to retrieve                                                                                                       | No       | 365 days      |
| devices[].reset          | Rebuild the history. If true, the data will be reset before the first data retrieval. If false, the data will be kept and new data will be added | No       | false         |

## Cost configuration

Gazpar2HAWS is able to compute and publish cost history to Home Assistant.

The cost computation is based in gas prices defined in the configuration files.

The pricing configuration is broken into 5 sections:
- vat: Value added tax definition.
- consumption_prices: All the gas price history in €/kWh.
- subscription_prices: The subscription prices in €/month (or year).
- transport_prices: Transport prices, either fixed (€/month or €/year) or based on consumption (€/kWh).
- energy_taxes: Various taxes on energy in €/kWh.

Below, many examples illustrates how to use pricing configuration for use cases from the simplest to the most complex.


Example 1: A fixed consumption price
---

The given price applies at the given date, after and before.

The default unit is € per kWh.

**Formula:**
```math
cost[€] = quantity[kWh] * price[€/kWh]
```


```yaml
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
```

Example 2: A fixed consumption price in another unit
---

*price_unit* is the monetary unit (default: €).
*quantity_unit* is the energy unit (default: kWh).

**Formula:**
```math
cost[€] = \frac{quantity[kWh] * price[¢/MWh] * converter\_factor[¢->€]} {converter\_factor[MWh->kWh]}
```


```yaml
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 7790.0 # Unit is now ¢/MWh.
    price_unit: "¢"
    quantity_unit: "MWh"
```

Example 3: Multiple prices over time
---

```yaml
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
  - start_date: "2024-01-01"
    quantity_value: 0.06888 # Default unit is €/kWh.
```

Price is 0.07790 before 2024-01-01.

Price is 0.06888 on 2024-01-01 and after.


Example 4: Price is given excluding tax
---

The *normal* value added tax (*vat*) rate is 20%.

```yaml
vat:
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
```

**Formula:**
```math
cost[€] = quantity[kWh] * price[€/kWh] * (1 + vat[normal])
```

Example 5: Subscription price
---

A fixed montly subscription is due over consumption.

Subscription *vat* tax may be different than the consumption *vat* tax.

```yaml
vat:
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
  - id: reduced
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.0550
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
subscription_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    time_value: 19.83
    price_unit: "€"
    time_unit: "month"
    vat_id: "reduced"
```

**Formula:**
```math
cost[€] = quantity[kWh] * cons\_price[€/kWh] * (1 + vat[normal]) + sub\_price * (1 + vat[reduced])
```


Example 6: Transport price
---

A fixed yearly transport may be charged as well.

```yaml
vat:
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
  - id: reduced
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.0550
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
transport_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    time_value: 34.38
    price_unit: "€"
    time_unit: "year"
    vat_id: reduced
```
**Formula:**
```math
cost[€] = quantity[kWh] * cons\_price[€/kWh] * (1 + vat[normal]) + trans\_price[€/year] * (1 + vat[reduced])
```

Example 6bis: Transport price (based on consumption)
---

**NEW in v0.4.0:** Transport can now be charged per kWh consumed instead of a fixed fee.

```yaml
vat:
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
  - id: reduced
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.0550
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
transport_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.00194 # €/kWh instead of €/year
    price_unit: "€"
    quantity_unit: "kWh"
    vat_id: reduced
```

**Formula:**
```math
cost[€] = quantity[kWh] * (cons\_price[€/kWh] * (1 + vat[normal]) + quantity[kWh] * trans\_price[€/kWh] * (1 + vat[reduced]))
```

Example 7: Energy taxes
---

Consumption may be taxed by additional taxes (known as energy taxes).

```yaml
vat:
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20 # It is the tax rate in [0, 1.0] <==> [0% - 100%].
  - id: reduced
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.0550
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
energy_taxes:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.00837
    price_unit: "€"
    quantity_unit: "kWh"
    vat_id: normal
```
**Formula:**
```math
cost[€] = quantity[kWh] * (cons\_price[€/kWh] + ener\_taxes[€/kWh])* (1 + vat[normal])
```

Example 8: All in one
---

In the price list, the first item properties are propagated to the next items in the list. If their values does not change, it is not required to repeat them.

```yaml
vat:
  - id: reduced
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.0550
  - id: normal
    start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.20
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.07790
    price_unit: "€"
    quantity_unit: "kWh"
    vat_id: normal
  - start_date: "2023-07-01"
    quantity_value: 0.05392
  - start_date: "2023-08-01"
    quantity_value: 0.05568
  - start_date: "2023-09-01"
    quantity_value: 0.05412
  - start_date: "2023-10-01"
    quantity_value: 0.06333
  - start_date: "2023-11-01"
    quantity_value: 0.06716
  - start_date: "2023-12-01"
    quantity_value: 0.07235
  - start_date: "2024-01-01"
    quantity_value: 0.06888
  - start_date: "2024-02-01"
    quantity_value: 0.05972
  - start_date: "2024-03-01"
    quantity_value: 0.05506
  - start_date: "2024-04-01"
    quantity_value: 0.04842
  - start_date: "2025-01-01"
    quantity_value: 0.07807
subscription_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    time_value: 19.83
    price_unit: "€"
    time_unit: "month"
    vat_id: reduced
  - start_date: "2023-07-01"
    time_value: 20.36
transport_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    time_value: 34.38
    price_unit: "€"
    time_unit: "year"
    vat_id: reduced
energy_taxes:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    quantity_value: 0.00837
    price_unit: "€"
    quantity_unit: "kWh"
    vat_id: normal
  - start_date: "2024-01-01"
    quantity_value: 0.01637
```

## What's New in v0.4.0

### Enhanced Cost Breakdown

Starting from v0.4.0, Gazpar2HAWS publishes **5 separate cost entities** instead of just 1:

- `sensor.${name}_consumption_cost` - Variable cost from gas consumption
- `sensor.${name}_subscription_cost` - Fixed subscription fees
- `sensor.${name}_transport_cost` - Transport fees
- `sensor.${name}_energy_taxes_cost` - Energy taxes
- `sensor.${name}_total_cost` - Sum of all cost components

This allows detailed cost analysis in Home Assistant dashboards and the Energy Dashboard.

### New Configuration Format

**BREAKING CHANGE:** The pricing configuration format has changed:

| Old Property (v0.3.x) | New Property (v0.4.0) | Used In |
|-----------------------|-----------------------|---------|
| `value` | `quantity_value` | consumption_prices, energy_taxes |
| `value` | `time_value` | subscription_prices, transport_prices |
| `value_unit` | `price_unit` | All price types |
| `base_unit` | `quantity_unit` | consumption_prices, energy_taxes |
| `base_unit` | `time_unit` | subscription_prices, transport_prices |

### Quantity-Based Transport Pricing

Transport prices can now be configured either as:
- **Fixed time-based**: `time_value` + `time_unit` (e.g., €/year)
- **Variable quantity-based**: `quantity_value` + `quantity_unit` (e.g., €/kWh) - NEW!

### Migration from v0.3.x

If you're upgrading from v0.3.x, you **must** update your pricing configuration to the new format.

**See [MIGRATIONS.md](https://github.com/ssenart/gazpar2haws/blob/main/MIGRATIONS.md)** for comprehensive migration instructions including:
- Step-by-step migration guide
- Before/after examples for each price type
- Quick reference table
- Troubleshooting common migration issues
- Validation checklist

## Creating Entities from Statistics (Workaround)

By design, Gazpar2HAWS publishes data as **cumulative statistics** in Home Assistant, not as regular state entities. This is the recommended approach for historical energy/gas data as it's optimized for the Energy Dashboard and historical analysis.

However, if you need regular Home Assistant entities (with states) that reflect the current meter readings, you can create them using SQL queries to read from the statistics database.

### SQL Configuration Workaround

Add the following SQL template sensors to your Home Assistant `configuration.yaml`:

```yaml
sql:
  - name: gazpar2haws_energy
    db_url: !secret recorder.db_url
    query: >
      SELECT state FROM statistics
      JOIN statistics_meta ON statistics.metadata_id = statistics_meta.id
      WHERE statistics_meta.statistic_id = 'sensor.gazpar2haws_energy'
      ORDER BY statistics.start DESC LIMIT 1
    column: 'state'
    unit_of_measurement: 'kWh'
    icon: mdi:fire
    device_class: energy
    state_class: total_increasing
  - name: gazpar2haws_volume
    db_url: !secret recorder.db_url
    query: >
      SELECT state FROM statistics
      JOIN statistics_meta ON statistics.metadata_id = statistics_meta.id
      WHERE statistics_meta.statistic_id = 'sensor.gazpar2haws_volume'
      ORDER BY statistics.start DESC LIMIT 1
    column: 'state'
    unit_of_measurement: 'm³'
    icon: mdi:fire
    device_class: gas
    state_class: total_increasing
```

This creates two new entities:
- `sensor.gazpar2haws_energy` - Latest energy reading (kWh)
- `sensor.gazpar2haws_volume` - Latest volume reading (m³)

These entities will automatically update whenever new statistics are added by Gazpar2HAWS.

### Alternative: Create Additional Cost Entities

You can adapt the same pattern to create entities for cost statistics:

```yaml
sql:
  - name: gazpar2haws_total_cost
    db_url: !secret recorder.db_url
    query: >
      SELECT state FROM statistics
      JOIN statistics_meta ON statistics.metadata_id = statistics_meta.id
      WHERE statistics_meta.statistic_id = 'sensor.gazpar2haws_total_cost'
      ORDER BY statistics.start DESC LIMIT 1
    column: 'state'
    unit_of_measurement: '€'
    icon: mdi:cash
    device_class: monetary
    state_class: total_increasing
```

### Why Statistics Instead of Entities?

Gazpar2HAWS uses statistics because:
- **Optimized for historical data**: Statistics are designed for time-series energy/gas data
- **Energy Dashboard compatible**: Works seamlessly with Home Assistant's Energy Dashboard
- **Database efficient**: Stores cumulative values more efficiently than state history
- **Accurate billing**: Preserves exact meter readings with timestamps for cost calculations
- **No duplicate data**: Avoids redundantly storing data in both states and statistics

If you need entities for automations or other purposes, this SQL workaround is the recommended approach.
