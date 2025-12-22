# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Table of Contents

- [Project Overview](#project-overview)
- [Getting Started & Development Setup](#getting-started--development-setup)
  - [Setup and Installation](#setup-and-installation)
  - [Linting and Formatting](#linting-and-formatting)
- [Deployment Methods](#deployment-methods)
  - [Running the Application Locally](#running-the-application-locally)
  - [Docker Compose (Standalone)](#docker-compose-standalone)
  - [Home Assistant Add-on (DevContainer)](#home-assistant-add-on-devcontainer)
- [Testing](#testing)
  - [Test Container Prerequisites](#test-container-prerequisites)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Add-on Testing with DevContainer](#add-on-testing-with-devcontainer)
  - [When to Use Which Testing Approach](#when-to-use-which-testing-approach)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [Data Flow](#data-flow)
  - [Pricing System](#pricing-system)
  - [Data Model](#data-model)
  - [Configuration System](#configuration-system)
- [Implementation Details](#implementation-details)
  - [Statistics Publishing](#statistics-publishing)
  - [Timezone Handling](#timezone-handling)
  - [Statistics Reset Mechanism](#statistics-reset-mechanism)
  - [Data Sources](#data-sources)
  - [PCE Identifier Gotcha](#pce-identifier-gotcha)
  - [Pricing Configuration Format (v0.4.0)](#pricing-configuration-format-v040)
- [CI/CD Pipelines](#cicd-pipelines)
  - [Pipeline Overview](#pipeline-overview)
  - [CI Pipeline](#ci-pipeline)
  - [Create Release Pipeline](#create-release-pipeline)
  - [Publish to DockerHub Pipeline](#publish-to-dockerhub-pipeline)
  - [Version Management with GitVersion](#version-management-with-gitversion)
  - [Reusable Actions](#reusable-actions)
  - [Running Pipelines Manually](#running-pipelines-manually)
- [Maintenance & Release](#maintenance--release)
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

## Getting Started & Development Setup

### Setup and Installation

```bash
# Install dependencies using Poetry
poetry install

# Activate Poetry virtual environment
poetry shell
```

### Linting and Formatting

**Before committing code, run ALL of these linting and formatting tools to ensure code quality:**

```bash
# Run all linters individually
poetry run pylint gazpar2haws
poetry run flake8 gazpar2haws
poetry run mypy gazpar2haws
poetry run ruff check gazpar2haws

# Format code
poetry run black gazpar2haws
poetry run isort gazpar2haws

# Or run all tests to verify everything passes
poetry run pytest tests/ -v
```

**Quality Assurance Checklist Before Committing:**
- ✓ Run `poetry run pylint gazpar2haws` - Must achieve 10.00/10 score
- ✓ Run `poetry run flake8 gazpar2haws` - Must have no errors
- ✓ Run `poetry run mypy gazpar2haws` - Must have no type errors
- ✓ Run `poetry run black gazpar2haws` - Code must be formatted correctly
- ✓ Run `poetry run isort gazpar2haws` - Imports must be sorted correctly
- ✓ Run `poetry run ruff check gazpar2haws` - All checks must pass
- ✓ Run `poetry run pytest tests/ -v` - All tests must pass

## Deployment Methods

This section covers different ways to run the Gazpar2HAWS application depending on your use case.

### Running the Application Locally

To run the application directly on your machine:

```bash
# Run with default configuration files
python -m gazpar2haws

# Run with custom configuration and secrets files
python -m gazpar2haws --config /path/to/configuration.yaml --secrets /path/to/secrets.yaml
```

### Docker Compose (Standalone)

To run the application in a Docker container for standalone deployment:

```bash
# Build Docker image
docker compose -f docker/docker-compose.yaml build

# Run container
docker compose -f docker/docker-compose.yaml up -d
```

### Home Assistant Add-on (DevContainer)

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

## Testing

This section covers the different testing approaches available in the project. Understanding when to use each approach is important for effective development.

### Test Container Prerequisites

Before running integration tests, you must launch the Home Assistant test container. This provides a local Home Assistant instance with WebSocket interface for integration testing.

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

### Unit Tests

Unit tests validate individual components without external dependencies.

```bash
# Run all unit tests (no container needed)
pytest

# Run a specific test file
pytest tests/test_pricer.py

# Run a specific test
pytest tests/test_pricer.py::TestPricer::test_get_composite_price_array

# Run tests with verbose output
pytest -v
```

**Unit test categories:**
- Pricer calculations and cost breakdown
- Model validation and data structures
- Date array operations
- Configuration parsing

### Integration Tests

Integration tests interact with Home Assistant via WebSocket API and require the test container to be running.

```bash
# Start test container first
cd tests/containers && docker compose up -d

# Run integration tests
pytest tests/test_haws.py

# Run all tests including integration tests
pytest -v
```

**Integration test categories:**
- WebSocket communication with Home Assistant
- Statistics import and export
- `clear_statistics()` functionality
- `get_last_statistic()` retrieval
- Configuration file handling

### Add-on Testing with DevContainer

Testing the add-on in a full Home Assistant environment provides the most realistic testing scenario. See the [Home Assistant Add-on (DevContainer)](#home-assistant-add-on-devcontainer) section under Deployment Methods for complete instructions.

### When to Use Which Testing Approach

**Use Unit Tests when:**
- Developing core business logic (pricer, models, utilities)
- Testing edge cases and error handling
- You want fast feedback (no container startup needed)
- Making changes to configuration parsing
- You don't need to test Home Assistant integration

**Use Integration Tests when:**
- Testing WebSocket communication
- Verifying statistics are correctly imported/exported to Home Assistant
- Testing the reset mechanism
- Ensuring the application can connect to and query Home Assistant

**Use DevContainer Add-on Testing when:**
- Testing the complete add-on deployment
- Verifying add-on appears in Home Assistant UI
- Testing add-on configuration through Home Assistant UI
- Validating entities and statistics in Home Assistant
- End-to-end testing with real Home Assistant instance
- Debugging issues with add-on lifecycle

**Example workflow:**
1. Develop locally with unit tests
2. When you need HA integration, run integration tests with test container
3. Before publishing, test the complete add-on with DevContainer

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

- **CompositePriceValue**: Represents prices with both quantity and time components (e.g., EUR/kWh + EUR/month)
- **CompositePriceArray**: Vectorized form holding both quantity_value_array and time_value_array
- **CostBreakdown**: Result structure with separate consumption, subscription, transport, energy_taxes, and total cost arrays
- **VAT support**: Multiple VAT rates (reduced, normal) applied to different price components
- **Time-varying prices**: Prices change over time, with automatic interpolation
- **Unit conversion**: Automatic conversion between quantity units (Wh, kWh, MWh), and time units (day, week, month, year)
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

## Implementation Details

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
- `sensor.${name}_consumption_cost` (EUR) - Variable cost from gas consumption
- `sensor.${name}_subscription_cost` (EUR) - Fixed subscription fees
- `sensor.${name}_transport_cost` (EUR) - Transport fees (fixed or variable)
- `sensor.${name}_energy_taxes_cost` (EUR) - Energy taxes
- `sensor.${name}_total_cost` (EUR) - Sum of all cost components

Where `${name}` is the device name from configuration (default: `gazpar2haws`)

**Note on Statistics vs Entities:** Gazpar2HAWS intentionally publishes cumulative statistics rather than regular state entities. This design choice is optimal for:
- Historical energy/gas data tracking
- Home Assistant Energy Dashboard integration
- Efficient database storage of time-series data
- Accurate cost calculations with precise timestamps

If you need Home Assistant entities (states) for automations or dashboards, see the [SQL Workaround](#creating-entities-from-statistics-workaround) section in the add-on documentation (`addons/gazpar2haws/DOCS.md`).

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

### Pricing Configuration Format (v0.5.0)

The pricing configuration uses the composite price model:

**YAML Properties:**
- `quantity_value`: Numeric value for quantity-based pricing (e.g., 0.07790 for EUR/kWh)
- `quantity_unit`: Energy unit (Wh, kWh, MWh) - default: kWh
- `time_value`: Numeric value for time-based pricing (e.g., 19.83 for EUR/month)
- `time_unit`: Time unit (day, week, month, year) - default: month
- `price_unit`: Monetary unit (EUR, USD, ...) - default: EUR
- `vat_id`: Reference to VAT rate ID

**Price Type Guidelines:**
- **consumption_prices**: Use `quantity_value` + `quantity_unit` (kWh)
- **subscription_prices**: Use `time_value` + `time_unit` (month/year)
- **transport_prices**: Use either `time_value` (fixed fee) OR `quantity_value` (per kWh)
- **energy_taxes**: Use `quantity_value` + `quantity_unit` (kWh)

**Deprecated (v0.4.x):**
- `time_unit` → Possible values `€` and `¢` replaced by `EUR` or other [ISO-4217 codes](https://en.wikipedia.org/wiki/ISO_4217#Active_codes)

**Deprecated (v0.3.x):**
- `value` → replaced by `quantity_value` or `time_value`
- `value_unit` → replaced by `price_unit`
- `base_unit` → replaced by `quantity_unit` or `time_unit`

## CI/CD Pipelines

This project uses GitHub Actions for continuous integration, testing, building, and release automation. The pipelines are defined in `.github/workflows/` and use reusable composite actions for modularity.

### Pipeline Overview

The project has three main workflows:

1. **CI Pipeline** (`.github/workflows/ci.yaml`) - Automated testing on every push and PR
2. **Create Release Pipeline** (`.github/workflows/create-release.yaml`) - Creates releases and publishes packages
3. **Publish to DockerHub Pipeline** (`.github/workflows/publish-to-dockerhub.yaml`) - Publishes Docker images

**Trigger Branches:**
- `main` - Production releases
- `develop` - Development releases and pre-releases
- `release/*` - Release candidates
- `feature/*` - Feature development
- Pull requests - Always run CI

### CI Pipeline

**Location:** `.github/workflows/ci.yaml`

**Triggered on:**
- Push to `main`, `develop`, `release/*`, `feature/*`
- All pull requests
- Manual workflow dispatch (with options to skip lint/tests)

**Jobs:**

1. **Prepare** (`prepare`)
   - Computes package version using GitVersion
   - Outputs: `package-version`, `target_python_versions`, `default_python_version`
   - Tests: Python 3.10, 3.11, 3.12, 3.13

2. **Lint** (`lint`)
   - Runs Python linting on default Python version (3.13)
   - Uses action: `./.github/workflows/python-lint`
   - Runs: PyLint, Flake8, Black, Isort, Mypy, Ruff
   - Skippable via input: `skip-lint`

3. **Test** (`test`)
   - Runs pytest against all target Python versions
   - Uses action: `./.github/workflows/python-test`
   - Starts HA test container
   - Waits for healthy status (30 attempts, 5s intervals)
   - Runs: `pytest tests/`
   - Skippable via input: `skip-tests`

**Conditional Execution:**
```yaml
if: ${{ !github.event.inputs.skip-lint }}  # Lint job
if: ${{ !github.event.inputs.skip-tests }}  # Test job
```

**To run CI manually:**
1. Go to GitHub Actions → CI
2. Click "Run workflow"
3. Select branch and optional inputs
4. Click green "Run workflow" button

### Create Release Pipeline

**Location:** `.github/workflows/create-release.yaml`

**Triggered on:** Manual workflow dispatch only

**Purpose:** Creates a new release, bumps versions, and publishes packages to PyPI and DockerHub

**Inputs:**
- `package-version` (optional) - Specific version to release (auto-computed if empty)
- `is_final` (optional, default: true) - Whether this is a final release (affects pre-release flag)

**Jobs:**

1. **Prepare** (`prepare`)
   - Computes version using GitVersion (if not provided)
   - Selects version from input or computed value
   - Outputs: `package-version`, `default_python_version`

2. **Build** (`build`)
   - Bumps version in:
     - `pyproject.toml` (Poetry)
     - `addons/gazpar2haws/config.yaml` (Add-on version)
     - `addons/gazpar2haws/build.yaml` (Add-on build version)
   - Commits and pushes version bumps
   - Creates Git tag with version number
   - Builds package with Poetry: `poetry build`
   - Uploads artifact: `dist/`

3. **Publish to PyPI** (`publish-to-pypi`)
   - Runs only on `main`, `develop`, or `release/*` branches
   - Uses trusted publishing (no explicit tokens needed)
   - Publishes to official PyPI: https://pypi.org/p/gazpar2haws
   - Downloads build artifact and publishes

4. **Publish to TestPyPI** (`publish-to-testpypi`)
   - Runs on any other branches (feature branches)
   - Publishes to test PyPI: https://test.pypi.org/p/gazpar2haws
   - Used for testing releases before production

5. **Publish to DockerHub** (`publish-to-dockerhub`)
   - Checks out the tag created in Build job
   - Publishes Docker image: `ssenart/gazpar2haws`
   - Tags: version number and optionally `latest`
   - Builds for multiple platforms: `linux/amd64`, `linux/arm64`

**How to create a release:**
1. Go to GitHub → Actions → Create Release
2. Click "Run workflow"
3. Select branch (usually `main` or `develop`)
4. Enter optional version (leave blank for auto-compute)
5. Toggle `is_final` if needed (true = production, false = pre-release)
6. Click green "Run workflow"
7. Monitor job execution in Actions tab
8. Pipeline automatically:
   - Bumps version numbers
   - Creates Git tag
   - Builds Python package
   - Publishes to PyPI (or TestPyPI)
   - Builds and publishes Docker images

### Publish to DockerHub Pipeline

**Location:** `.github/workflows/publish-to-dockerhub.yaml`

**Triggered on:** Manual workflow dispatch only

**Purpose:** Allows publishing specific versions to DockerHub without full release process

**Inputs:**
- `package-version` (optional) - Specific version to publish (auto-computed if empty)
- `is_latest` (optional, default: true) - Whether to tag as `latest`

**Jobs:**

1. **Prepare** (`prepare`)
   - Computes version using GitVersion (if not provided)
   - Selects version from input or computed value

2. **Publish to DockerHub** (`publish-to-dockerhub`)
   - Logs in to DockerHub with credentials
   - Extracts metadata and creates tags
   - Sets up QEMU for multi-platform builds
   - Builds and pushes Docker image
   - Platforms: `linux/amd64`, `linux/arm64`
   - Tags: `<version>`, optionally `latest`

**Credentials Required:**
- `DOCKERHUB_USERNAME` - GitHub secret
- `DOCKERHUB_PASSWORD` - GitHub secret (use token, not password)

### Version Management with GitVersion

**Configuration:** `gitversion.yaml`

**How it works:**
- Uses GitVersion tool to compute semantic version based on branch
- Converts to PEP440 format for Python
- Supports pre-release versions with labels

**Version Format by Branch:**
```
main (master):           X.Y.Z                    (final release)
develop:                 X.Y.Za<commits>         (alpha pre-release)
release/<name>:          X.Y.Zb<commits>         (beta pre-release)
feature/<name>:          X.Y.Z.dev<commits>      (development version)
```

**Examples:**
- `main` branch, 3 commits after tag 1.0.0 → `1.0.0`
- `develop` branch, 5 commits after tag → `1.1.0a5`
- `release/1.1.0` → `1.1.0b0`
- `feature/new-feature`, 10 commits → `1.1.0.dev10`

**Configuration Details:**
- Assembly format: `{MajorMinorPatch}{PreReleaseLabel}{CommitsSinceVersionSource}`
- Pre-release labels:
  - `develop`: `a` (alpha)
  - `release/*`: `b` (beta)
  - `feature/*`: `.dev` (development)
  - `main`: `` (empty = final)

### Reusable Actions

The project uses composite GitHub Actions for modularity:

**1. compute-version** (`.github/workflows/compute-version/action.yaml`)
- Purpose: Compute semantic version using GitVersion
- Output: `pep440-version` - Python-formatted version
- Used by: CI, Create Release, Publish to DockerHub pipelines

**2. python-lint** (`.github/workflows/python-lint/action.yaml`)
- Purpose: Run all Python linters
- Inputs: `python-version`
- Tools: PyLint, Flake8, Black, Isort, Mypy, Ruff
- Used by: CI pipeline

**3. python-test** (`.github/workflows/python-test/action.yaml`)
- Purpose: Run pytest with HA test container
- Inputs: `python-version`
- Steps:
  1. Set up Python
  2. Install Poetry and project
  3. Start HA test container
  4. Wait for healthy status
  5. Run pytest
- Used by: CI pipeline

**4. git-tag** (`.github/workflows/git-tag/action.yaml`)
- Purpose: Create and push Git tag
- Inputs: `tag-name`
- Steps:
  1. Delete existing local tag (if any)
  2. Delete existing remote tag (if any)
  3. Create new local tag
  4. Push to remote
- Used by: Create Release pipeline

**5. publish-to-dockerhub** (`.github/workflows/publish-to-dockerhub/action.yaml`)
- Purpose: Build and push Docker image to DockerHub
- Inputs: `image`, `version`, `is_latest`, `username`, `password`
- Steps:
  1. Set up Docker with buildx
  2. Extract metadata and tags
  3. Log in to DockerHub
  4. Set up QEMU (multi-platform)
  5. Build and push image
  6. Platforms: `linux/amd64`, `linux/arm64`
- Used by: Create Release, Publish to DockerHub pipelines

### Running Pipelines Manually

**Via GitHub Web UI:**
1. Go to GitHub repository
2. Click Actions tab
3. Select workflow (CI, Create Release, or Publish to DockerHub)
4. Click "Run workflow" button
5. Select branch
6. Fill in optional inputs
7. Click green "Run workflow" button
8. Monitor execution in Actions tab

**Via GitHub CLI:**
```bash
# List available workflows
gh workflow list

# Run specific workflow
gh workflow run ci.yaml --ref main

# Run workflow with inputs
gh workflow run create-release.yaml --ref main \
  -f package-version=1.2.3 \
  -f is_final=true

# View workflow runs
gh run list

# View specific run
gh run view <run-id>

# View run logs
gh run view <run-id> --log
```

**Workflow Constraints:**
- CI pipeline: Runs automatically on push/PR, or manually
- Create Release: Manual workflow only (controlled release process)
- Publish to DockerHub: Manual workflow only
- All workflows are read-only except Create Release (which has write permissions for commits/tags)

### Pipeline Secrets Configuration

**Required Secrets:**
- `DOCKERHUB_USERNAME` - DockerHub account username
- `DOCKERHUB_PASSWORD` - DockerHub account token (not password)

**To set up secrets:**
1. Go to GitHub Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD`
4. Save

**PyPI Publishing:**
- Uses trusted publishing with OIDC
- No secrets needed for official PyPI
- TestPyPI also uses trusted publishing

## Maintenance & Release

When making changes to the pricing model, configuration format, or published entities, multiple files across the repository need to be updated to maintain consistency. This section documents all locations that require maintenance.

**Key documentation to update:**
- Keep **README.md** updated with any user-facing changes
- Keep **CLAUDE.md** (this file) updated with architecture, implementation, and development changes
- Always update **CHANGELOG.md** with a new version entry documenting Added/Changed/Fixed/Removed items

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

**Core Documentation Updates:**
1. **MIGRATIONS.md**: Add comprehensive migration guide with:
   - Before/after configuration examples
   - Step-by-step migration instructions
   - Validation checklist
   - Troubleshooting section

2. **CHANGELOG.md**: Mark "Migration" section and reference MIGRATIONS.md

3. **README.md**: Add brief "What's New" section and warning banner linking to MIGRATIONS.md

4. **FAQ.md**: Add Q&A about the migration, linking to MIGRATIONS.md for details

**Add-on Documentation Updates (MUST NOT FORGET):**
5. **addons/gazpar2haws/README.md**: Update migration guide link if needed
6. **addons/gazpar2haws/DOCS.md**:
   - Update all configuration examples to new format
   - Add "Migration from vX.X.x" section with reference to MIGRATIONS.md
   - Update pricing examples showing new property names
7. **addons/gazpar2haws/config.yaml**: Update:
   - Version number (line 3)
   - Options section with example pricing (new format)
   - Schema section with new property definitions

**Code & Configuration Updates:**
8. **Model validation**: Consider adding deprecation warnings before full removal
9. **Version bump**: Use semantic versioning (breaking change = major version bump)

### Cross-Reference Validation

After making changes, verify consistency across:

- Entity names match in README.md, CLAUDE.md, DOCS.md, and gazpar.py
- Property names match in all configuration examples and schema definitions
- Formulas match between DOCS.md examples and Pricer implementation
- Version numbers match across all files
- Migration guides reference the correct property mappings
- **ADD-ON DOCUMENTATION**: Always check `addons/gazpar2haws/` folder for:
  - `README.md` - Links to migration guides and documentation
  - `DOCS.md` - Configuration examples and explanations
  - `config.yaml` - Options section (examples) and schema section (validation)

### Add-on Documentation Maintenance Reminder

**⚠️ CRITICAL: Do NOT forget add-on documentation when making changes!**

The `addons/gazpar2haws/` folder must be kept in sync with main documentation:

1. **README.md** - Links to MIGRATIONS.md, FAQ.md, etc.
2. **DOCS.md** - Configuration examples MUST match main documentation format
3. **config.yaml** - Schema definitions MUST match configuration requirements
4. **DOCS.md migration sections** - MUST reference MIGRATIONS.md for detailed steps

**Checklist before releasing:**
- [ ] Main README.md updated with new content
- [ ] MIGRATIONS.md created/updated if breaking changes
- [ ] FAQ.md updated with Q&A if needed
- [ ] `addons/gazpar2haws/README.md` checked and updated
- [ ] `addons/gazpar2haws/DOCS.md` examples match new format
- [ ] `addons/gazpar2haws/config.yaml` options and schema match
- [ ] Version number updated in `addons/gazpar2haws/config.yaml` line 3
- [ ] All links verified (no broken references between docs)

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
2. Update all config files with new property names:
   - `config/configuration.yaml`
   - `config/configuration.template.yaml`
   - `addons/gazpar2haws/config.yaml` (options AND schema sections)
3. Update schema definitions in `addons/gazpar2haws/config.yaml`
4. Update all documentation examples:
   - `README.md`
   - `addons/gazpar2haws/DOCS.md` (all pricing examples)
5. Create/update migration guide in MIGRATIONS.md
6. Add brief "What's New" to README.md with link to MIGRATIONS.md
7. Update `addons/gazpar2haws/README.md` migration guide section
8. Update `addons/gazpar2haws/DOCS.md` with migration section
9. Add deprecation warnings if possible
10. Update CHANGELOG.md with breaking change notice
11. Add FAQ entry about migration

**Scenario 3: Changing published entities**
1. Update `gazpar.py` - Sensor name definitions and publishing logic
2. Update entity lists in:
   - `README.md` (Configuration section, "What's New" section)
   - `CLAUDE.md` (Architecture section)
   - `addons/gazpar2haws/DOCS.md` (entity descriptions)
3. Update "What's New" section in both:
   - `README.md`
   - `addons/gazpar2haws/DOCS.md`
4. Update CHANGELOG.md with entity changes
5. Consider impact on existing Home Assistant installations
6. If entity names changed: Add migration note to MIGRATIONS.md and `addons/gazpar2haws/DOCS.md`

### File Location Quick Reference

```
Configuration Files:
├── config/configuration.yaml              # Main example config
├── config/configuration.template.yaml     # Docker template
├── config/secrets.template.yaml           # Secrets template
├── addons/gazpar2haws/config.yaml        # Add-on config + schema
└── tests/config/example_*.yaml           # Test configurations

Documentation Files:
├── README.md                              # Main user docs (overview, features, quick links)
├── MIGRATIONS.md                          # Version upgrade guides (breaking changes, step-by-step)
├── FAQ.md                                 # User questions (links to MIGRATIONS.md for upgrades)
├── CHANGELOG.md                           # Version history (links to MIGRATIONS.md for breaking changes)
├── CLAUDE.md                              # Developer guide
├── TODO.md                                # Planned improvements
└── addons/gazpar2haws/DOCS.md            # Add-on user guide (links to MIGRATIONS.md)

Test Data:
└── tests/XLPricer.xlsx                   # Expected pricing calculations
```
