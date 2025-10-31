# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Table of Contents

- [Project Overview](#project-overview)
- [Development Commands](#development-commands)
  - [Setup and Installation](#setup-and-installation)
  - [Testing](#testing-1)
  - [Linting and Formatting](#linting-and-formatting)
  - [Running the Application](#running-the-application)
  - [Docker](#docker)
  - [DevContainer Add-on Testing](#devcontainer-add-on-testing)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [Data Flow](#data-flow)
  - [Pricing System](#pricing-system)
  - [Data Model](#data-model)
  - [Configuration System](#configuration-system)
- [Key Implementation Details](#key-implementation-details)
  - [Statistics Publishing](#statistics-publishing)
  - [Timezone Handling](#timezone-handling)
  - [Statistics Reset Mechanism](#statistics-reset-mechanism)
  - [Data Sources](#data-sources)
  - [PCE Identifier Gotcha](#pce-identifier-gotcha)
  - [Pricing Configuration Format (v0.4.0)](#pricing-configuration-format-v040)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release management](#release-management)
- [Configuration Files and Documentation Maintenance](#configuration-files-and-documentation-maintenance)
  - [Configuration Files](#configuration-files)
  - [Documentation Files](#documentation-files)
  - [Version Update Checklist](#version-update-checklist)
  - [Property Naming Conventions](#property-naming-conventions)
  - [Breaking Changes Protocol](#breaking-changes-protocol)
  - [Cross-Reference Validation](#cross-reference-validation)
  - [Common Maintenance Scenarios](#common-maintenance-scenarios)
  - [File Location Quick Reference](#file-location-quick-reference)

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

#### Prerequisites: Test Container

Before running unit tests, you must launch the Home Assistant test container. This provides a local Home Assistant instance with WebSocket interface for integration testing.

```bash
# Start the Home Assistant test container
cd tests/containers
docker compose up -d

# Verify the container is running and healthy
docker compose ps

# View logs if needed
docker compose logs -f

# Stop the container when done
docker compose down
```

The test container:
- Runs Home Assistant on port **6123** (mapped from internal 8123)
- Uses configuration from `tests/containers/config/`
- Provides a WebSocket interface at `ws://localhost:6123/api/websocket`
- Includes a health check that verifies Home Assistant is ready
- Persists data in `tests/containers/config/home-assistant_v2.db`

**Access URLs:**
- Web UI: http://localhost:6123
- WebSocket API: ws://localhost:6123/api/websocket

#### Running Tests

```bash
# Run all tests (ensure test container is running first)
pytest

# Run a specific test file
pytest tests/test_pricer.py

# Run a specific test
pytest tests/test_pricer.py::TestPricer::test_get_composite_price_array

# Run tests with verbose output
pytest -v

# Run tests that require Home Assistant WebSocket
pytest tests/test_haws.py
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

### DevContainer Add-on Testing

The project includes a DevContainer configuration for testing the Home Assistant add-on in a complete Home Assistant environment. This is the recommended approach for add-on development and testing.

**Location**: `.devcontainer/devcontainer.json`

**Prerequisites:**
- Docker Desktop installed and running
- Visual Studio Code with "Remote - Containers" extension installed
- The devcontainer must be launched from VS Code (not command line)

**Setup and Usage:**

1. **Open in DevContainer**:
   - Open the project folder in VS Code
   - When prompted (or via Command Palette: "Dev Containers: Reopen in Container"), click "Reopen in Container"
   - First launch will take several minutes to build the container

2. **Start Home Assistant**:
   - Once inside the container, open the VS Code integrated terminal
   - Run the task: `Terminal → Run Task → Start Home Assistant`
   - Alternatively, run from terminal: `supervisor_run`
   - This launches Home Assistant with Supervisor, bootstrapping the environment

3. **Access Home Assistant**:
   - Web UI: http://localhost:7123
   - The add-on will be automatically detected as a local add-on in the `/addons` directory
   - Configure and test the add-on through Home Assistant UI or via CLI

4. **CLI Commands Inside DevContainer**:
   - `supervisor_run` - Starts Home Assistant with Supervisor
   - `ha` - Home Assistant CLI (requires Supervisor running first)
   - `ha addon logs gazpar2haws` - View add-on logs
   - `ha addon restart gazpar2haws` - Restart the add-on
   - `ha addon config gazpar2haws` - View add-on configuration

5. **Port Mappings**:
   - Home Assistant Web UI: `7123:8123`
   - Supervisor API: `7357:4357`
   - These are configured in `devcontainer.json`

**Testing the Add-on:**

1. Configure the add-on through Home Assistant UI:
   - Add-ons → Gazpar2HAWS → Configuration
   - Fill in GrDF credentials and pricing configuration
   - Click Save

2. Start the add-on:
   - Add-ons → Gazpar2HAWS → Start
   - View logs to monitor execution

3. Verify functionality:
   - Check that entities are created: `sensor.gazpar2haws_volume`, `sensor.gazpar2haws_energy`, etc.
   - Verify statistics appear in Home Assistant Energy Dashboard
   - Check logs for errors: `ha addon logs gazpar2haws`

4. Develop and iterate:
   - Modify code locally
   - Restart the add-on to test changes
   - View logs in real-time from the VS Code terminal

**DevContainer Configuration Details:**

- **Base Image**: `ghcr.io/home-assistant/devcontainer:addons` - Includes Supervisor and Home Assistant
- **Bootstrap Command**: Runs `devcontainer_bootstrap` after container starts
- **Privileged Mode**: Required for Docker operations inside container
- **Volume Mount**: `/var/lib/docker` for Docker-in-Docker support
- **VSCode Extensions**: ShellCheck and Prettier pre-installed
- **Environment**: `WORKSPACE_DIRECTORY` points to `/workspace`

**Troubleshooting:**

- If Home Assistant fails to start, check logs: `docker logs homeassistant`
- If the add-on doesn't appear, ensure it's in the correct directory structure
- To rebuild the container: `Dev Containers: Rebuild Container`
- To start fresh: `Dev Containers: Rebuild Container` then `Dev Containers: Reopen in Container`

**Cleanup:**

When done testing:
- Exit the container: `Dev Containers: Reopen Folder Locally`
- Stop the container via Docker Desktop or: `docker compose -f .devcontainer/docker-compose.yaml down`

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
   - Publishes data as cumulative statistics to Home Assistant:
     - `sensor.${name}_volume` - Volume in m³
     - `sensor.${name}_energy` - Energy in kWh
     - `sensor.${name}_consumption_cost` - Consumption cost breakdown
     - `sensor.${name}_subscription_cost` - Subscription cost breakdown
     - `sensor.${name}_transport_cost` - Transport cost breakdown
     - `sensor.${name}_energy_taxes_cost` - Energy taxes cost breakdown
     - `sensor.${name}_total_cost` - Total cost (sum of all cost components)

3. **HomeAssistantWS** ([haws.py](gazpar2haws/haws.py)) - WebSocket client for Home Assistant
   - Implements Home Assistant WebSocket API protocol
   - Handles authentication with Bearer token
   - Imports statistics using `recorder/import_statistics`
   - Queries existing statistics using `recorder/statistics_during_period`

### Data Flow

1. Bridge initiates periodic scan
2. For each device, Gazpar:
   - Queries HA for last known statistics (date and cumulative value) for all 7 entities
   - Fetches missing data from GrDF via PyGazpar
   - Extracts volume and energy readings
   - If pricing config exists, computes cost breakdown using Pricer (5 components)
   - Publishes cumulative statistics to HA (not incremental values):
     - Volume and energy entities (always published)
     - Cost breakdown entities (if pricing configured): consumption, subscription, transport, energy_taxes, total
3. Bridge disconnects from HA and waits for next scan interval

### Pricing System

The Pricer ([pricer.py](gazpar2haws/pricer.py)) implements a sophisticated cost calculation system:

- **CompositePriceValue**: Represents prices with both quantity and time components (e.g., €/kWh + €/month)
- **CompositePriceArray**: Vectorized form holding both quantity_value_array and time_value_array
- **CostBreakdown**: Result structure with separate consumption, subscription, transport, energy_taxes, and total cost arrays
- **VAT support**: Multiple VAT rates (reduced, normal) applied to different price components
- **Time-varying prices**: Prices change over time, with automatic interpolation
- **Unit conversion**: Automatic conversion between price units (€, ¢), quantity units (Wh, kWh, MWh), and time units (day, week, month, year)
- **Formula**: `cost = quantity × (consumption_price + energy_taxes) + subscription_price + transport_price` (all with VAT applied)

### Data Model

The model ([model.py](gazpar2haws/model.py)) uses Pydantic for configuration validation and defines:

- **DateArray**: Sparse array indexed by date for efficient time-series operations
- **ValueArray**: Base class for all time-series data with unit conversion
- **CompositePriceValue**: Input model with optional quantity_value/quantity_unit and time_value/time_unit fields
- **CompositePriceArray**: Output model with quantity_value_array and time_value_array DateArrays
- **CostBreakdown**: Output model with consumption, subscription, transport, energy_taxes, and total CostArrays
- **Configuration**: Device, Grdf, HomeAssistant, Logging, Pricing

### Configuration System

Configuration uses YAML with secret interpolation:

- `configuration.yaml`: Main config with `!secret` references
- `secrets.yaml`: Sensitive values with `${ENV_VAR}` placeholders
- Loaded via ConfigLoader ([config_utils.py](gazpar2haws/config_utils.py))

## Key Implementation Details

### Statistics Publishing

Home Assistant statistics are published as **cumulative sums**, not deltas:
- Query last known cumulative value from HA for each entity
- Add new incremental readings to create new cumulative values
- Publish cumulative statistics with exact timestamp of reading date

**Published Entities:**

Always published:
- `sensor.${name}_volume` (m³)
- `sensor.${name}_energy` (kWh)

Published when pricing configuration is provided:
- `sensor.${name}_consumption_cost` (€) - Variable cost from gas consumption
- `sensor.${name}_subscription_cost` (€) - Fixed subscription fees
- `sensor.${name}_transport_cost` (€) - Transport fees (fixed or variable)
- `sensor.${name}_energy_taxes_cost` (€) - Energy taxes
- `sensor.${name}_total_cost` (€) - Sum of all cost components

Where `${name}` is the device name from configuration (default: `gazpar2haws`)

### Timezone Handling

All timestamps are localized to the configured timezone (default: `Europe/Paris`) before publishing to Home Assistant.

### Statistics Reset Mechanism

The application provides a mechanism to reset all statistics to zero and clear historical data from Home Assistant. This is controlled by the `reset` configuration flag in the device configuration.

**Implementation Location:**
- Configuration flag: [gazpar.py:67](gazpar2haws/gazpar.py#L67) - `self._reset = device_config.reset`
- Reset logic: [gazpar.py:100-116](gazpar2haws/gazpar.py#L100-L116) - In `Gazpar.publish()` method
- WebSocket API: [haws.py:215-227](gazpar2haws/haws.py#L215-L227) - `HomeAssistantWS.clear_statistics()`

**How It Works:**

1. **Configuration**: Set `reset: true` in the device configuration under `devices` section
2. **Execution**: On the next scan cycle, before fetching new data:
   - All 7 entity statistics are cleared from Home Assistant using `recorder/clear_statistics` API
   - Entities cleared:
     - `sensor.{name}_volume`
     - `sensor.{name}_energy`
     - `sensor.{name}_consumption_cost`
     - `sensor.{name}_subscription_cost`
     - `sensor.{name}_transport_cost`
     - `sensor.{name}_energy_taxes_cost`
     - `sensor.{name}_total_cost`
3. **Counter Reset**: After clearing, `find_last_date_and_value()` returns `last_value = 0` for all entities
4. **Data Republishing**: New data is fetched from GrDF and published with cumulative values starting from zero

**Usage Notes:**
- This is a **one-time operation** - the reset flag should be removed after the first successful run
- Clears **all historical statistics** from Home Assistant for the specified device
- Useful for:
  - Fixing data corruption or incorrect historical imports
  - Starting fresh with new pricing configurations
  - Correcting meter reading offsets
- If reset fails, an exception is raised and logged

**WebSocket API Call:**
```python
{
    "type": "recorder/clear_statistics",
    "statistic_ids": [list of entity IDs]
}
```

### Data Sources

PyGazpar supports multiple data sources:
- `JsonWebDataSource` (default): Fetches data from GrDF web API
- `ExcelWebDataSource`: Downloads Excel files from GrDF
- `TestDataSource`: For testing

### PCE Identifier Gotcha

PCE identifiers must be quoted in YAML to preserve leading zeros. Unquoted values like `0123456789` are interpreted as numbers and lose the leading zero.

### Pricing Configuration Format (v0.4.0)

The pricing configuration uses the composite price model:

**YAML Properties:**
- `quantity_value`: Numeric value for quantity-based pricing (e.g., 0.07790 for €/kWh)
- `quantity_unit`: Energy unit (Wh, kWh, MWh) - default: kWh
- `time_value`: Numeric value for time-based pricing (e.g., 19.83 for €/month)
- `time_unit`: Time unit (day, week, month, year) - default: month
- `price_unit`: Monetary unit (€, ¢) - default: €
- `vat_id`: Reference to VAT rate ID

**Price Type Guidelines:**
- **consumption_prices**: Use `quantity_value` + `quantity_unit` (kWh)
- **subscription_prices**: Use `time_value` + `time_unit` (month/year)
- **transport_prices**: Use either `time_value` (fixed fee) OR `quantity_value` (per kWh)
- **energy_taxes**: Use `quantity_value` + `quantity_unit` (kWh)

**Deprecated (v0.3.x):**
- `value` → replaced by `quantity_value` or `time_value`
- `value_unit` → replaced by `price_unit`
- `base_unit` → replaced by `quantity_unit` or `time_unit`

## Testing

Tests are organized by module and use pytest:
- Test configuration files in `tests/config/`
- Excel-based test data in `tests/XLPricer.xlsx`
- Multiple pricing examples in `tests/config/example_*.yaml`
- Home Assistant test container in `tests/containers/`

**Test Container Setup:**

Integration tests that interact with Home Assistant WebSocket API require a local Home Assistant instance. The test container is configured in `tests/containers/docker-compose.yaml`:

- **Purpose**: Provides a ready-to-use Home Assistant instance for WebSocket integration testing
- **Port**: 6123 (accessible at http://localhost:6123)
- **WebSocket**: ws://localhost:6123/api/websocket
- **Configuration**: Pre-configured with test data in `tests/containers/config/`
- **Database**: Persistent SQLite database for statistics storage
- **Health Check**: Ensures container is ready before running tests

Start the container before running integration tests (see Development Commands → Testing section above).

**Test Categories:**

- **Unit Tests**: Pricer, model validation, date array operations (no container needed)
- **Integration Tests**: WebSocket communication, statistics import/export (requires container)
  - `tests/test_haws.py` - Home Assistant WebSocket tests
  - Tests for `clear_statistics()`, `import_statistics()`, `get_last_statistic()`

When modifying the Pricer, update the Excel test file and corresponding YAML examples to ensure pricing formulas remain correct.

## Documentation

Keep updated README.md and CLAUDE.md regarding to any changes in the code.

## Release management

Always suggest to update the CHANGELOG.md with any changes in the code.

## Configuration Files and Documentation Maintenance

When making changes to the pricing model, configuration format, or published entities, multiple files across the repository need to be updated to maintain consistency. This section documents all locations that require maintenance.

### Configuration Files

Configuration files exist in multiple locations for different deployment scenarios:

#### 1. Main Configuration (Standalone/Docker)

**Location**: `config/`

Files to update:
- **`config/configuration.yaml`** - Example configuration with real pricing data
- **`config/configuration.template.yaml`** - Template with placeholders for Docker deployments
- **`config/secrets.template.yaml`** - Template for sensitive values (rarely needs updates)

**When to update**: Any pricing model changes, new configuration options, or default value changes.

**Example changes needed**:
- Property name changes (e.g., `value` → `quantity_value`)
- New configuration sections
- Updated examples reflecting current pricing structure

#### 2. Add-on Configuration (Home Assistant Add-on)

**Location**: `addons/gazpar2haws/`

Files to update:
- **`addons/gazpar2haws/config.yaml`** - Add-on configuration and schema
  - Version number (line 3)
  - Options section with example pricing (lines 31-64)
  - Schema section defining allowed properties (lines 80-115)
- **`addons/gazpar2haws/DOCS.md`** - Comprehensive pricing examples and documentation
  - All pricing examples (Examples 1-8+)
  - Transport price description
  - "What's New" section for new versions
- **`addons/gazpar2haws/README.md`** - Brief description (rarely needs updates)
- **`addons/gazpar2haws/rootfs/app/config/configuration.template.yaml`** - Uses env vars, usually no changes needed

**When to update**: Version releases, pricing model changes, new features affecting configuration.

**Critical**: The add-on config.yaml contains BOTH example configuration AND JSON schema definitions. Both must be updated together.

#### 3. Test Configuration

**Location**: `tests/config/`

Files to update:
- **`tests/config/example_1.yaml`** through **`tests/config/example_6bis.yaml`** - Test configurations for different pricing scenarios
- **`tests/XLPricer.xlsx`** - Excel spreadsheet with expected pricing calculations

**When to update**: Any changes to pricing formulas, new price types, or unit conversions.

### Documentation Files

#### 1. User Documentation

**`README.md`** - Main project documentation
- Installation instructions
- Configuration examples
- Entity descriptions (7 entities in v0.4.0)
- Pricing section with all price types
- Migration guides
- FAQ section structure
- Links to other documentation files

**`FAQ.md`** - Frequently Asked Questions
- Common configuration issues
- Migration questions
- Troubleshooting steps
- References to specific GitHub issues

**`CHANGELOG.md`** - Version history
- Added/Changed/Fixed/Removed sections
- Breaking changes clearly marked
- Issue references with [#XX] format
- Migration notes for breaking changes

#### 2. Developer Documentation

**`CLAUDE.md`** (this file) - Developer guidance
- Architecture overview
- Data flow descriptions
- Pricing system details
- Configuration format specifications
- Testing guidelines
- Maintenance procedures

**`TODO.md`** - Planned improvements
- Test coverage gaps
- Priority-based task organization
- Specific test cases needed
- Implementation schedule

#### 3. Add-on Documentation

**`addons/gazpar2haws/DOCS.md`** - Add-on user guide
- Detailed pricing examples (8+ examples)
- Configuration parameter descriptions
- Formulas showing cost calculations
- "What's New" sections for version updates

### Version Update Checklist

When releasing a new version, ensure ALL of the following are updated:

1. **Version Numbers**:
   - `pyproject.toml` - Python package version
   - `addons/gazpar2haws/config.yaml` - Add-on version (line 3)
   - `CHANGELOG.md` - Add new version entry at top

2. **Configuration Examples** (if pricing format changed):
   - `config/configuration.yaml` - Update example pricing
   - `config/configuration.template.yaml` - Update template
   - `addons/gazpar2haws/config.yaml` - Options section (lines 31-64)
   - All `tests/config/example_*.yaml` files

3. **Schema Definitions** (if pricing format changed):
   - `addons/gazpar2haws/config.yaml` - Schema section (lines 80-115)

4. **Documentation Examples** (if pricing format changed):
   - `README.md` - Pricing section examples
   - `addons/gazpar2haws/DOCS.md` - All 8+ examples
   - `FAQ.md` - Add migration questions if breaking changes

5. **Architecture Documentation** (if entities or data flow changed):
   - `README.md` - Entity list, architecture section
   - `CLAUDE.md` - Published entities, data flow, architecture
   - `addons/gazpar2haws/DOCS.md` - "What's New" section

6. **Test Data** (if pricing formulas changed):
   - `tests/XLPricer.xlsx` - Update expected calculations
   - `tests/config/example_*.yaml` - Add new test scenarios

### Property Naming Conventions

When adding new configuration properties:

- Use **snake_case** for all YAML properties
- Use descriptive names that indicate the property's purpose
- Group related properties with common prefixes:
  - `quantity_*` for energy/volume-based values
  - `time_*` for duration-based values
  - `price_*` for monetary units
  - `*_unit` for unit specifications
  - `*_id` for references to other sections

### Breaking Changes Protocol

When introducing breaking changes to configuration:

1. **CHANGELOG.md**: Mark section with "BREAKING" and provide migration table
2. **README.md**: Add migration guide with before/after examples
3. **FAQ.md**: Add Q&A about the migration
4. **DOCS.md**: Add "What's New" section explaining changes
5. **Model validation**: Consider adding deprecation warnings before full removal
6. **Version bump**: Use semantic versioning (breaking change = major version bump)

### Cross-Reference Validation

After making changes, verify consistency across:

- Entity names match in README.md, CLAUDE.md, DOCS.md, and gazpar.py
- Property names match in all configuration examples and schema definitions
- Formulas match between DOCS.md examples and Pricer implementation
- Version numbers match across all files
- Migration guides reference the correct property mappings

### Common Maintenance Scenarios

**Scenario 1: Adding a new price type**
1. Update `model.py` - Add Pydantic model
2. Update `pricer.py` - Add calculation logic
3. Update `gazpar.py` - Add entity and publishing logic
4. Update all config files (config/, addons/, tests/)
5. Update schema in `addons/gazpar2haws/config.yaml`
6. Add example in `addons/gazpar2haws/DOCS.md`
7. Update entity lists in README.md, CLAUDE.md
8. Add test case in `tests/XLPricer.xlsx`

**Scenario 2: Renaming configuration properties**
1. Update `model.py` - Change property names
2. Update all config files with new property names
3. Update schema definitions in add-on config.yaml
4. Update all documentation examples
5. Add migration guide to README.md
6. Add deprecation warnings if possible
7. Update CHANGELOG.md with breaking change notice
8. Add FAQ entry about migration

**Scenario 3: Changing published entities**
1. Update `gazpar.py` - Sensor name definitions and publishing logic
2. Update entity lists in README.md, CLAUDE.md, DOCS.md
3. Update "What's New" section in DOCS.md
4. Update CHANGELOG.md
5. Consider impact on existing Home Assistant installations

### File Location Quick Reference

```
Configuration Files:
├── config/configuration.yaml              # Main example config
├── config/configuration.template.yaml     # Docker template
├── config/secrets.template.yaml           # Secrets template
├── addons/gazpar2haws/config.yaml        # Add-on config + schema
└── tests/config/example_*.yaml           # Test configurations

Documentation Files:
├── README.md                              # Main user docs
├── CLAUDE.md                              # Developer guide
├── FAQ.md                                 # User questions
├── CHANGELOG.md                           # Version history
├── TODO.md                                # Planned improvements
└── addons/gazpar2haws/DOCS.md            # Add-on user guide

Test Data:
└── tests/XLPricer.xlsx                   # Expected pricing calculations
```