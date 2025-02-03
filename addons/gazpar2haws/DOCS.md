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
- transport_prices: The fixed prices in €/month (or year) to transport the gas.
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
    value: 0.07790 # Default unit is €/kWh.
```

Example 2: A fixed consumption price in another unit
---

*value_unit* is the price unit (default: €).
*base_unit* is the denominator unit (default: kWh).

**Formula:**
```math
cost[€] = \frac{quantity[kWh] * price[¢/MWh] * converter\_factor[¢->€]} {converter\_factor[MWh->kWh]}
```


```yaml
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 7790.0 # Unit is now ¢/MWh.
    value_unit: "¢"
    base_unit: "MWh"
```

Example 3: Multiple prices over time
---

```yaml
consumption_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.07790 # Default unit is €/kWh.
  - start_date: "2024-01-01"
    value: 0.06888 # Default unit is €/kWh.
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
    value: 0.07790 # Default unit is €/kWh.
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
    value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
subscription_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 19.83
    value_unit: "€"
    base_unit: "month"
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
    value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
transport_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 34.38
    value_unit: "€"
    base_unit: "year"
    vat_id: reduced
```
**Formula:**
```math
cost[€] = quantity[kWh] * cons\_price[€/kWh] * (1 + vat[normal]) + trans\_price * (1 + vat[reduced])
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
    value: 0.07790 # Default unit is €/kWh.
    vat_id: "normal" # Reference to the vat rate that is applied for this period.
energy_taxes:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.00837
    value_unit: "€"
    base_unit: "kWh"
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
    value: 0.07790
    value_unit: "€"
    base_unit: "kWh"
    vat_id: normal
  - start_date: "2023-07-01"
    value: 0.05392
  - start_date: "2023-08-01"
    value: 0.05568
  - start_date: "2023-09-01"
    value: 0.05412
  - start_date: "2023-10-01"
    value: 0.06333
  - start_date: "2023-11-01"
    value: 0.06716
  - start_date: "2023-12-01"
    value: 0.07235
  - start_date: "2024-01-01"
    value: 0.06888
  - start_date: "2024-02-01"
    value: 0.05972
  - start_date: "2024-03-01"
    value: 0.05506
  - start_date: "2024-04-01"
    value: 0.04842
  - start_date: "2025-01-01"
    value: 0.07807
subscription_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 19.83
    value_unit: "€"
    base_unit: "month"
    vat_id: reduced
  - start_date: "2023-07-01"
    value: 20.36
transport_prices:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 34.38
    value_unit: "€"
    base_unit: "year"
    vat_id: reduced
energy_taxes:
  - start_date: "2023-06-01" # Date of the price. Format is "YYYY-MM-DD".
    value: 0.00837
    value_unit: "€"
    base_unit: "kWh"
    vat_id: normal
  - start_date: "2024-01-01"
    value: 0.01637
```
