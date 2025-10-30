# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gazpar2HAWS is a gateway that reads gas meter data from GrDF (French gas provider) and sends it to Home Assistant using WebSocket interface. It enables uploading historical data and keeping it updated with the latest readings, compatible with Home Assistant Energy Dashboard.

## Development Commands

### Setup and Installation

```bash
# Install dependencies using Poetry
poetry install

# Activate Poetry virtual environment
poetry shell
```

### Testing

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_pricer.py

# Run a specific test
pytest tests/test_pricer.py::TestPricer::test_get_consumption_price_array_inside
```

### Linting and Formatting

```bash
# Run all linters
pylint gazpar2haws
flake8 gazpar2haws
mypy gazpar2haws

# Format code
black gazpar2haws
isort gazpar2haws

# Run ruff (includes linting and formatting)
ruff check gazpar2haws
```

### Running the Application

```bash
# Run with default configuration files
python -m gazpar2haws

# Run with custom configuration and secrets files
python -m gazpar2haws --config /path/to/configuration.yaml --secrets /path/to/secrets.yaml
```

### Docker

```bash
# Build Docker image
docker compose -f docker/docker-compose.yaml build

# Run container
docker compose -f docker/docker-compose.yaml up -d
```

## Architecture

### Core Components

The application follows a layered architecture with three main components:

1. **Bridge** ([bridge.py](gazpar2haws/bridge.py)) - Main orchestrator that coordinates the data flow
   - Manages the periodic scan loop (controlled by `scan_interval`)
   - Handles WebSocket connection lifecycle to Home Assistant
   - Processes SIGINT/SIGTERM for graceful shutdown
   - Supports multiple GrDF devices (each with its own Gazpar instance)

2. **Gazpar** ([gazpar.py](gazpar2haws/gazpar.py)) - Data retrieval and processing layer
   - Fetches gas consumption data from GrDF using PyGazpar library
   - Extracts volume (m³) and energy (kWh) from meter readings
   - Computes costs using the Pricer when pricing configuration is provided
   - Manages incremental updates by querying HA for last statistics
   - Publishes data as cumulative statistics to Home Assistant

3. **HomeAssistantWS** ([haws.py](gazpar2haws/haws.py)) - WebSocket client for Home Assistant
   - Implements Home Assistant WebSocket API protocol
   - Handles authentication with Bearer token
   - Imports statistics using `recorder/import_statistics`
   - Queries existing statistics using `recorder/statistics_during_period`

### Data Flow

1. Bridge initiates periodic scan
2. For each device, Gazpar:
   - Queries HA for last known statistics (date and cumulative value)
   - Fetches missing data from GrDF via PyGazpar
   - Extracts volume and energy readings
   - If pricing config exists, computes costs using Pricer
   - Publishes cumulative statistics to HA (not incremental values)
3. Bridge disconnects from HA and waits for next scan interval

### Pricing System

The Pricer ([pricer.py](gazpar2haws/pricer.py)) implements a sophisticated cost calculation system:

- **CompositePriceValue**: Represents prices with both quantity and time components (e.g., €/kWh + €/month)
- **VAT support**: Multiple VAT rates (reduced, normal) applied to different price components
- **Time-varying prices**: Prices change over time, with automatic interpolation
- **Unit conversion**: Automatic conversion between price units (€, ¢), quantity units (Wh, kWh, MWh), and time units (day, week, month, year)
- **Formula**: `cost = quantity × (consumption_price + energy_taxes) + subscription_price + transport_price` (all with VAT applied)

### Data Model

The model ([model.py](gazpar2haws/model.py)) uses Pydantic for configuration validation and defines:

- **DateArray**: Sparse array indexed by date for efficient time-series operations
- **ValueArray**: Base class for all time-series data with unit conversion
- **Pricing components**: VatRate, ConsumptionPriceArray, SubscriptionPriceArray, TransportPriceArray, EnergyTaxesPriceArray
- **Configuration**: Device, Grdf, HomeAssistant, Logging, Pricing

### Configuration System

Configuration uses YAML with secret interpolation:

- `configuration.yaml`: Main config with `!secret` references
- `secrets.yaml`: Sensitive values with `${ENV_VAR}` placeholders
- Loaded via ConfigLoader ([config_utils.py](gazpar2haws/config_utils.py))

## Key Implementation Details

### Statistics Publishing

Home Assistant statistics are published as **cumulative sums**, not deltas:
- Query last known cumulative value from HA
- Add new incremental readings to create new cumulative values
- Publish cumulative statistics with exact timestamp of reading date

### Timezone Handling

All timestamps are localized to the configured timezone (default: `Europe/Paris`) before publishing to Home Assistant.

### Data Sources

PyGazpar supports multiple data sources:
- `JsonWebDataSource` (default): Fetches data from GrDF web API
- `ExcelWebDataSource`: Downloads Excel files from GrDF
- `TestDataSource`: For testing

### PCE Identifier Gotcha

PCE identifiers must be quoted in YAML to preserve leading zeros. Unquoted values like `0123456789` are interpreted as numbers and lose the leading zero.

## Testing

Tests are organized by module and use pytest:
- Test configuration files in `tests/config/`
- Excel-based test data in `tests/XLPricer.xlsx`
- Multiple pricing examples in `tests/config/example_*.yaml`

When modifying the Pricer, update the Excel test file and corresponding YAML examples to ensure pricing formulas remain correct.
