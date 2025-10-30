# Frequently Asked Questions (FAQ)

This document answers common questions about Gazpar2HAWS based on GitHub issues and user feedback.

---

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Configuration Issues](#configuration-issues)
- [Data & Statistics](#data--statistics)
- [Cost Calculation](#cost-calculation)
- [Home Assistant Integration](#home-assistant-integration)
- [Docker & Add-on](#docker--add-on)
- [Troubleshooting](#troubleshooting)
- [Migration & Upgrades](#migration--upgrades)

---

## General Questions

### Is Gazpar2HAWS an official GrDF application?

**No.** Gazpar2HAWS is an unofficial, community-developed tool that uses the GrDF web interface to retrieve your gas consumption data. It is not affiliated with, endorsed by, or supported by GrDF (Gaz Réseau Distribution France).

### What is the difference between home-assistant-gazpar, Gazpar2MQTT, and Gazpar2HAWS?

- **[home-assistant-gazpar](https://github.com/ssenart/home-assistant-gazpar)**: A Home Assistant custom integration that runs inside HA and creates sensors for gas consumption.

- **[Gazpar2MQTT](https://github.com/ssenart/gazpar2mqtt)**: Provides the same functionality as home-assistant-gazpar but runs as a standalone application, Docker container, or HA add-on. It publishes data via MQTT.

- **[Gazpar2HAWS](https://github.com/ssenart/gazpar2haws)**: Uses the Home Assistant Recorder integration to create historical statistics directly. Key advantages:
  - Timestamps readings to exact observation dates (not publication dates)
  - Can reconstruct complete history up to 3 years in the past
  - Calculates and publishes detailed energy costs
  - Compatible with Home Assistant Energy Dashboard
  - No MQTT broker required

### How often is data updated?

- **From GrDF**: Gas readings are typically available 2-5 days after the actual consumption date (sometimes longer).
- **From Gazpar2HAWS**: You configure the `scan_interval` (in minutes). Set to `0` for a single retrieval at startup.
- **Historical data**: Gazpar2HAWS timestamps readings to their actual observation dates, not when they were retrieved.

### Can I use this without Home Assistant?

No. Gazpar2HAWS is specifically designed to integrate with Home Assistant via the WebSocket API and Recorder integration.

---

## Installation & Setup

### What are the installation options?

1. **Standalone Python application**: Run directly with Python and Poetry
2. **Docker container**: Use Docker Compose with the provided configuration
3. **Home Assistant add-on**: Install from the add-on store (requires Supervisor)

See [README.md](README.md) for detailed installation instructions for each method.

### What are the system requirements?

- **For standalone**: Python 3.11 or higher, Poetry
- **For Docker**: Docker and Docker Compose
- **For HA add-on**: Home Assistant with Supervisor
- **For all**: Active Home Assistant instance with WebSocket API access

### Do I need a long-lived access token?

**Yes.** You need to create a long-lived access token in Home Assistant:
1. Go to your Home Assistant profile
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Copy the token and add it to your `secrets.yaml`

---

## Configuration Issues

### My PCE identifier has a leading zero (e.g., "0123456789") but the application uses "123456789" without it. Why?

**Issue:** [#38](https://github.com/ssenart/gazpar2haws/issues/38)

**Cause:** Your PCE identifier is not quoted in the YAML configuration file, so it's interpreted as a number instead of a string.

**Solution:** Quote your PCE identifier in `configuration.yaml`:
```yaml
grdf:
  devices:
    - pce_identifier: "0123456789"  # ✓ Quoted - preserves leading zero
      # NOT: pce_identifier: 0123456789  # ✗ Will lose leading zero
```

### The 'reset' parameter is ignored in my configuration

**Issue:** [#47](https://github.com/ssenart/gazpar2haws/issues/47)

**Cause:** This was a bug in v0.1.12 and earlier where the reset parameter wasn't properly read from the add-on configuration.

**Solution:** Upgrade to v0.1.13 or later.

### Error: "HA endpoint configuration is missing"

**Issue:** [#36](https://github.com/ssenart/gazpar2haws/issues/36)

**Cause:** The `homeassistant` section is missing or incomplete in your configuration file.

**Solution:** Ensure your `configuration.yaml` includes:
```yaml
homeassistant:
  host: "!secret homeassistant.host"
  port: "!secret homeassistant.port"
  token: "!secret homeassistant.token"
```

And your `secrets.yaml` includes:
```yaml
homeassistant.host: "localhost"
homeassistant.port: "8123"
homeassistant.token: "your-long-lived-access-token"
```

### How do I use environment variables in configuration?

In `secrets.yaml`, use `${VARIABLE_NAME}` syntax:
```yaml
grdf.username: "${GRDF_USERNAME}"
grdf.password: "${GRDF_PASSWORD}"
homeassistant.token: "${HA_TOKEN}"
```

Then set environment variables before running:
```bash
export GRDF_USERNAME="your-email@example.com"
export GRDF_PASSWORD="your-password"
export HA_TOKEN="your-token"
```

For Docker, use the `environment` section in `docker-compose.yaml`.

### What does "as_of_date" do?

**Issue:** [#70](https://github.com/ssenart/gazpar2haws/issues/70)

**as_of_date** is primarily used for testing purposes. It allows you to simulate running the application at a specific date in the past.

**Note:** This property was removed from the default configuration template in v0.3.2. Only use it if you're testing or debugging.

---

## Data & Statistics

### Error: "GrDF send missing data with type='Absence de Données'"

**Issue:** [#37](https://github.com/ssenart/gazpar2haws/issues/37)

**Cause:** GrDF sometimes returns records with type "Absence de Données" (data absence) instead of actual consumption data.

**Solution:** This was fixed in v0.1.12. The application now properly handles missing data entries. Upgrade to the latest version.

### Data is retrieved up to application start date instead of current date

**Issue:** [#64](https://github.com/ssenart/gazpar2haws/issues/64)

**Cause:** Bug in v0.3.0 and earlier where `as_of_date` was incorrectly calculated.

**Solution:** Upgrade to v0.3.1 or later, which fixes the date calculation.

### Why are my readings several days old?

This is normal GrDF behavior. Gas meter readings are:
- Collected by the meter daily at midnight
- Transmitted to GrDF over the network (can take 1-2 days)
- Processed and made available via the web interface (adds another 1-3 days)

Gazpar2HAWS retrieves the data as soon as it's available from GrDF but timestamps it to the actual reading date.

### Can I retrieve historical data?

**Yes.** Use the `last_days` parameter in your device configuration:
```yaml
grdf:
  devices:
    - last_days: 1095  # Retrieve up to 3 years of history
```

**Note:** This only retrieves data on the first run or when `reset: true`. On subsequent runs, it only fetches new data.

### The last meter value is imported multiple times

**Issue:** [#6](https://github.com/ssenart/gazpar2haws/issues/6)

**Cause:** Bug in v0.1.1 and earlier with timestamp handling.

**Solution:** Upgrade to v0.1.2 or later. Also verify your timezone is correctly configured:
```yaml
grdf:
  devices:
    - timezone: Europe/Paris
```

### Using reset=false causes meter to restart from zero

**Issue:** [#3](https://github.com/ssenart/gazpar2haws/issues/3)

**Cause:** Bug in cumulative sum calculation in early versions.

**Solution:** Upgrade to v0.1.2 or later.

---

## Cost Calculation

### How do I configure pricing?

See the extensive pricing examples in [README.md](README.md#cost-configuration). Basic example:

```yaml
pricing:
  vat:
    - id: normal
      start_date: "2023-06-01"
      value: 0.20  # 20% VAT
  consumption_prices:
    - start_date: "2023-06-01"
      quantity_value: 0.07790  # €/kWh
      vat_id: "normal"
```

### I upgraded to v0.4.0 and my pricing configuration doesn't work

**Issue:** [#83](https://github.com/ssenart/gazpar2haws/issues/83)

**Cause:** v0.4.0 introduced a **breaking change** in the pricing configuration format.

**Solution:** Migrate your configuration from the old format to the new format:

**Old format (v0.3.x):**
```yaml
consumption_prices:
  - start_date: "2023-06-01"
    value: 0.07790
    value_unit: "€"
    base_unit: "kWh"
```

**New format (v0.4.0+):**
```yaml
consumption_prices:
  - start_date: "2023-06-01"
    quantity_value: 0.07790  # Renamed from 'value'
    price_unit: "€"          # Renamed from 'value_unit'
    quantity_unit: "kWh"     # Renamed from 'base_unit'
```

See [README.md Migration Guide](README.md#migration-from-v03x-to-v040) for complete migration instructions.

### What are the new cost entities in v0.4.0?

Starting from v0.4.0, Gazpar2HAWS publishes **5 separate cost entities** instead of just 1:

- `sensor.${name}_consumption_cost` - Variable cost from gas consumption
- `sensor.${name}_subscription_cost` - Fixed subscription fees
- `sensor.${name}_transport_cost` - Transport fees
- `sensor.${name}_energy_taxes_cost` - Energy taxes
- `sensor.${name}_total_cost` - Sum of all cost components

This allows detailed cost analysis in Home Assistant.

### Can I use quantity-based transport pricing?

**Yes**, starting from v0.4.0. You can now define transport prices either:

**As a fixed time-based fee:**
```yaml
transport_prices:
  - start_date: "2023-06-01"
    time_value: 34.38
    price_unit: "€"
    time_unit: "year"
```

**As a variable quantity-based fee:**
```yaml
transport_prices:
  - start_date: "2023-06-01"
    quantity_value: 0.00194
    price_unit: "€"
    quantity_unit: "kWh"
```

### How is the cost calculated?

The complete formula is:
```
cost[€] = quantity[kWh] × (consumption_price[€/kWh] + energy_taxes[€/kWh]) × (1 + vat)
        + subscription_price[€/month] × (1 + vat)
        + transport_price[€/year or €/kWh] × (1 + vat)
```

Each component can have different VAT rates and supports time-varying prices.

---

## Home Assistant Integration

### What entities are created in Home Assistant?

For each device, the following entities are created:

**Always created:**
- `sensor.${name}_volume` - Volume in m³
- `sensor.${name}_energy` - Energy in kWh

**Created when pricing is configured:**
- `sensor.${name}_consumption_cost` - Consumption cost in €
- `sensor.${name}_subscription_cost` - Subscription cost in €
- `sensor.${name}_transport_cost` - Transport cost in €
- `sensor.${name}_energy_taxes_cost` - Energy taxes in €
- `sensor.${name}_total_cost` - Total cost in €

Where `${name}` is the device name from your configuration (default: `gazpar2haws`).

### Can I use these entities in the Energy Dashboard?

**Yes.** The volume and energy entities are fully compatible with the Home Assistant Energy Dashboard:

1. Go to **Settings → Dashboards → Energy**
2. Add a gas source
3. Select `sensor.${name}_energy` as the gas consumption entity
4. Select `sensor.${name}_total_cost` as the cost entity (optional)

### Using HassIO, I get connection errors

**Issues:** [#13](https://github.com/ssenart/gazpar2haws/issues/13), [#15](https://github.com/ssenart/gazpar2haws/issues/15)

**Cause:** HassIO/Home Assistant Supervisor uses different WebSocket endpoints and authentication.

**Solution:** When running as a HassIO add-on:
- Use `host: localhost` (not the external IP)
- Use `port: 8123`
- The WebSocket endpoint is automatically adjusted to `/core/websocket`
- Authorization header is automatically included

These issues were fixed in v0.1.4 and v0.1.5.

### No entities appear in Home Assistant

**Possible causes:**

1. **WebSocket connection issue**: Check logs for connection errors
2. **Authentication failure**: Verify your long-lived access token is valid
3. **Recorder not enabled**: Ensure Home Assistant Recorder integration is active
4. **Configuration error**: Check logs for configuration parsing errors

**Debugging steps:**
1. Check the application logs (see [Troubleshooting](#troubleshooting))
2. Verify you can connect to HA WebSocket manually
3. Test with `last_days: 7` to retrieve a small amount of data
4. Enable debug logging: `logging.level: debug`

### Timezone issues causing duplicate imports

**Issue:** [#9](https://github.com/ssenart/gazpar2haws/issues/9)

**Cause:** Incorrect timezone configuration causing timestamp mismatches.

**Solution:** Ensure your timezone matches your location:
```yaml
grdf:
  devices:
    - timezone: Europe/Paris  # Use your actual timezone
```

Fixed in v0.1.2.

---

## Docker & Add-on

### How do I install the Docker version?

1. Clone the repository:
   ```bash
   git clone https://github.com/ssenart/gazpar2haws.git
   cd gazpar2haws
   ```

2. Configure environment variables in `docker/docker-compose.yaml` or create a `.env` file

3. Start the container:
   ```bash
   docker compose -f docker/docker-compose.yaml up -d
   ```

### How do I install the Home Assistant add-on?

**Issue:** [#4](https://github.com/ssenart/gazpar2haws/issues/4)

1. Add the repository to your Home Assistant add-on store
2. Install the Gazpar2HAWS add-on
3. Configure the add-on with your GrDF and Home Assistant credentials
4. Start the add-on

See the add-on documentation for detailed instructions.

### DockerHub version is always one version behind

**Issue:** [#50](https://github.com/ssenart/gazpar2haws/issues/50)

**Cause:** Bug in the GitHub Actions workflow for versioning.

**Solution:** This was fixed in v0.1.14. The version displayed in logs now correctly matches the release version.

### Addon configuration format is wrong

**Issue:** [#57](https://github.com/ssenart/gazpar2haws/issues/57)

**Cause:** The add-on configuration format didn't match the standalone configuration format.

**Solution:** Starting from v0.2.0, the add-on configuration format matches the file-based configuration format. Update your add-on configuration to use the new format.

See [#55](https://github.com/ssenart/gazpar2haws/issues/55) for the format change details.

### Where are the logs in Docker?

```bash
# View live logs
docker compose -f docker/docker-compose.yaml logs -f

# View logs from file (if configured)
docker compose exec gazpar2haws cat /path/to/log/gazpar2haws.log
```

---

## Troubleshooting

### Application doesn't work - where do I start?

1. **Check the logs** - This is the most important step:
   - Standalone: Check the log file path configured in `configuration.yaml`
   - Docker: `docker compose logs -f`
   - HA Add-on: Check add-on logs in Home Assistant

2. **Enable debug logging**:
   ```yaml
   logging:
     level: debug
   ```

3. **Verify configuration** syntax with a YAML validator

4. **Test with minimal configuration** - Try with just one device and `last_days: 7`

### Common log messages and their meanings

**"Starting Gazpar2HAWS version X.X.X"**
- ✓ Application started successfully
- Check this version matches what you expect

**"Connected to Home Assistant"**
- ✓ WebSocket connection established
- ✓ Authentication successful

**"No volume data to publish"** or **"No energy data to publish"**
- Either no new data available from GrDF
- Or all available data has already been imported
- This is normal after the initial import

**"Error while importing statistics to Home Assistant"**
- ✗ Failed to send data to Home Assistant
- Check Home Assistant Recorder is running
- Verify your access token is valid

**"Error while resetting the sensor in Home Assistant"**
- ✗ Failed to clear existing statistics
- Check your access token has sufficient permissions

### How do I report a bug?

If you've identified a bug:

1. Create a GitHub issue at https://github.com/ssenart/gazpar2haws/issues

2. Include the following information:
   - **Setup type**: Standalone, Docker, or HA add-on
   - **Version**: Check logs for "Starting Gazpar2HAWS version X.X.X"
   - **Installation type**: New installation or upgrade (from which version?)
   - **Description**: What's happening vs. what you expect
   - **Logs**: Complete log file from start to error (remove secrets!)

3. For configuration issues, include your configuration file (with secrets removed)

### Application crashes with "Fatal error"

**Issue:** [#32](https://github.com/ssenart/gazpar2haws/issues/32)

**Cause:** Introduction of `as_of_date` feature caused crashes in test mode.

**Solution:** Fixed in v0.1.11. Upgrade to the latest version.

### How do I reset all data and start over?

Two options:

**Option 1: Use reset parameter (recommended)**
```yaml
grdf:
  devices:
    - reset: true  # Clears all statistics on next run
```

After running once, set it back to `false`.

**Option 2: Manual deletion in Home Assistant**
1. Go to Developer Tools → Statistics
2. Find your sensors (e.g., `sensor.gazpar2haws_volume`)
3. Delete the statistics
4. Restart Gazpar2HAWS

---

## Migration & Upgrades

### How do I upgrade from v0.3.x to v0.4.0?

v0.4.0 introduces **breaking changes** in the pricing configuration format.

**Step 1: Update pricing configuration**

Replace old properties with new ones:
- `value` → `quantity_value` or `time_value`
- `value_unit` → `price_unit`
- `base_unit` → `quantity_unit` or `time_unit`

See the [complete migration guide](README.md#migration-from-v03x-to-v040) in README.md with detailed examples.

**Step 2: Update the application**
- Docker: `docker compose pull && docker compose up -d`
- Standalone: `git pull && poetry install`
- Add-on: Update from Home Assistant UI

**Step 3: Verify**
- Check logs for any configuration errors
- Verify new cost entities appear in Home Assistant
- Confirm cost calculations match expectations

### Do I need to reset data when upgrading?

**No.** In most cases, you don't need to reset data when upgrading. Historical data is preserved.

**Exception**: If release notes specifically mention data format changes requiring a reset.

### Can I downgrade to an older version?

**Not recommended.** Database schema or data format changes may not be backward compatible.

If you must downgrade:
1. Backup your Home Assistant database
2. Use `reset: true` to clear statistics
3. Downgrade the application
4. Let it reimport historical data

### What happened to PyGazpar updates?

PyGazpar is the underlying library used to fetch data from GrDF. Gazpar2HAWS regularly updates to the latest PyGazpar version:

- **v0.3.3**: Upgraded to PyGazpar 1.3.1 ([#77](https://github.com/ssenart/gazpar2haws/issues/77))
- **v0.3.0**: Upgraded to PyGazpar 1.3.0 ([#60](https://github.com/ssenart/gazpar2haws/issues/60))
- **v0.1.3**: Upgraded to PyGazpar 1.2.6 ([#11](https://github.com/ssenart/gazpar2haws/issues/11))

Always use the latest version for best compatibility with GrDF.

---

## Additional Resources

- **GitHub Repository**: https://github.com/ssenart/gazpar2haws
- **Issue Tracker**: https://github.com/ssenart/gazpar2haws/issues
- **README**: Detailed installation and configuration guide
- **CHANGELOG**: Complete version history with all changes
- **CLAUDE.md**: Developer documentation and architecture
- **TODO.md**: Planned improvements and test coverage tasks

---

## Contributing

Found an issue not covered here? Please:
1. Check the [GitHub issues](https://github.com/ssenart/gazpar2haws/issues)
2. If it's a new issue, create a detailed bug report
3. If you have a solution, submit a pull request!

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

**Last Updated:** 2025-10-30
**Current Version:** 0.4.0
**Next Review:** When v0.5.0 is released
