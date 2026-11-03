# Gazpar2HAWS Developer Guide

This guide provides comprehensive information for developers working on the Gazpar2HAWS project.

---

## Table of Contents

- [Standards & Specifications](#standards--specifications)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)
- [Build & Release](#build--release)
- [Troubleshooting](#troubleshooting)

---

## Standards & Specifications

This project follows industry-standard specifications and best practices. All contributors should be familiar with these standards.

### Version Control & Commits

#### 📋 [Conventional Commits](https://www.conventionalcommits.org/) v1.0.0
Specification for structured commit messages that enable automatic changelog generation and semantic versioning.

**Format**: `<type>[optional scope]: <description>`

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

**Why**: Enables automatic changelog generation, semantic versioning, and clear project history.

#### 🏷️ [Semantic Versioning](https://semver.org/) (SemVer) v2.0.0
Versioning scheme using `MAJOR.MINOR.PATCH` format.

- **MAJOR**: Incompatible API changes (breaking changes)
- **MINOR**: Backward-compatible new features
- **PATCH**: Backward-compatible bug fixes

**Why**: Provides predictable version numbers that communicate the nature of changes.

#### 📝 [Keep a Changelog](https://keepachangelog.com/) v1.1.0
Standard format for maintaining CHANGELOG.md files.

**Sections**: Added, Changed, Deprecated, Removed, Fixed, Security

**Why**: Human-readable changelog that clearly communicates changes to users.

### Python Standards

#### 🐍 [PEP 8](https://peps.python.org/pep-0008/) – Style Guide for Python Code
Official Python style guide covering naming conventions, code layout, and best practices.

**Key Points**:
- 4 spaces for indentation (not tabs)
- Max line length: 120 characters (configured in `pyproject.toml`)
- Snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants

**Why**: Consistent, readable Python code across the project.

#### 📖 [PEP 257](https://peps.python.org/pep-0257/) – Docstring Conventions
Standard for writing Python docstrings.

**Format**:
```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description on one line.

    More detailed description if needed. Explain parameters,
    return values, and any exceptions raised.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is invalid
    """
```

**Why**: Self-documenting code and automatic documentation generation.

#### 🔤 [PEP 484](https://peps.python.org/pep-0484/) – Type Hints
Standard for type annotations in Python.

**Example**:
```python
from typing import Optional, List, Dict

def process_data(items: List[str], config: Optional[Dict[str, Any]] = None) -> int:
    """Process items and return count."""
    return len(items)
```

**Why**: Better IDE support, early error detection with mypy, and self-documenting code.

### Testing Standards

#### ✅ [pytest](https://docs.pytest.org/) – Testing Framework
Modern Python testing framework with rich plugin ecosystem.

**Conventions**:
- Test files: `test_*.py` or `*_test.py`
- Test functions: `def test_*():`
- Test classes: `class Test*:`
- Use fixtures for setup/teardown
- Use `pytest.mark.asyncio` for async tests

**Why**: Simple, powerful testing with excellent fixture support.

### Documentation Standards

#### 📄 [CommonMark](https://commonmark.org/) – Markdown Specification
Standard Markdown syntax for all documentation files.

**Files**: `README.md`, `CHANGELOG.md`, `FAQ.md`, `docs/*.md`

**Why**: Consistent, portable documentation that renders correctly everywhere.

### Code Quality Standards

#### ⚡ [Ruff](https://docs.astral.sh/ruff/) – Linter and Code Formatter
A fast Python linter and code formatter. `ruff format` formats the code, and `ruff check` lints it.

**Configuration**: `pyproject.toml` → `[tool.ruff]` and `[tool.ruff.lint]`

**Why**: One fast tool for formatting and linting, with zero-debate formatting.

#### 🔍 [mypy](https://mypy.readthedocs.io/) – Static Type Checker
Static type checker for Python using PEP 484 type hints.

**Configuration**: `pyproject.toml` → `[tool.mypy]`

**Why**: Catch type errors before runtime, better IDE support.

### Project-Specific Standards

#### 🏠 [Home Assistant Developer Docs](https://developers.home-assistant.io/)
Guidelines for integrating with Home Assistant.

**Key Topics**:
- [WebSocket API](https://developers.home-assistant.io/docs/api/websocket/)
- [Statistics](https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics)
- [Add-on Development](https://developers.home-assistant.io/docs/add-ons/)
- [Add-on Testing](https://developers.home-assistant.io/docs/apps/testing/)
- [Add-on Security](https://developers.home-assistant.io/docs/add-ons/security/)
- [Add-on Configuration](https://developers.home-assistant.io/docs/apps/configuration)
- [Internationalization](https://developers.home-assistant.io/docs/api/supervisor/endpoints/#addonsaddon-translations)
- [Supervisor API](https://developers.home-assistant.io/docs/api/supervisor/)
- [Entity Naming](https://developers.home-assistant.io/docs/core/entity/#entity-naming)

**Example Repositories**:
- [Official Example Add-on](https://github.com/home-assistant/addons-example) - Blueprint for add-on development
  - [Example Dockerfile](https://github.com/home-assistant/addons-example/blob/main/example/Dockerfile)
  - [Example build.yaml](https://github.com/home-assistant/addons-example/blob/main/example/build.yaml)
  - [Example config.yaml](https://github.com/home-assistant/addons-example/blob/main/example/config.yaml)
  - [Example AppArmor profile](https://github.com/home-assistant/addons-example/blob/main/example/apparmor.txt)
  - [Example translations](https://github.com/home-assistant/addons-example/tree/main/example/translations)

**Docker Base Images**:
- [HA Docker Base Repository](https://github.com/home-assistant/docker-base) - Official base images
  - Current project uses: `ghcr.io/home-assistant/{arch}-base:3.23` (Alpine 3.23)
  - Includes s6-overlay, Bashio, and TempIO
- [hassio-addons Debian Base](https://github.com/hassio-addons/debian-base) - Community Debian images
  - Alternative for glibc compatibility: `ghcr.io/hassio-addons/debian-base/{arch}:stable`

**Community Resources**:
- [DevContainer Documentation](https://code.visualstudio.com/docs/devcontainers/containers) - VS Code DevContainer setup
- [s6-overlay](https://github.com/just-containers/s6-overlay) - Process supervisor used in HA add-ons
- [Bashio](https://github.com/hassio-addons/bashio) - Bash function library for HA add-ons

**Related Project Issues**:
- [Issue #105](https://github.com/ssenart/gazpar2haws/issues/105) - Segmentation fault resolved by Alpine 3.23 upgrade

**Why**: Ensures proper integration with Home Assistant ecosystem and provides reference for add-on development.

### Security Standards

#### 🔒 Security Best Practices
- Never commit secrets (passwords, tokens, API keys) to repository
- Use environment variables or `secrets.yaml` for sensitive data
- Follow [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- Report security vulnerabilities privately via GitHub Security Advisories

### License

#### 📜 Project License
This project uses the license specified in the [LICENSE](../LICENSE) file. All contributions must comply with this license.

---

## Project Overview

### What is Gazpar2HAWS?

Gazpar2HAWS is a gateway application that:
- Fetches gas consumption data from GrDF (French gas provider) via PyGazpar
- Publishes historical statistics to Home Assistant via WebSocket API
- Calculates detailed energy costs with flexible pricing components
- Supports Home Assistant Energy Dashboard integration

### Key Features

- **Historical data import**: Retrieve up to 3 years of gas consumption history
- **Exact timestamping**: Data is timestamped to actual meter reading dates, not retrieval dates
- **Cost calculation**: Flexible pricing with unlimited custom components (consumption, subscription, transport, taxes, etc.)
- **WebSocket integration**: Direct integration with Home Assistant Recorder via WebSocket
- **Multiple deployment options**: Standalone Python, Docker, or Home Assistant add-on

### Technology Stack

- **Language**: Python 3.10+
- **Key Dependencies**:
  - `pygazpar`: GrDF API client
  - `websockets`: Home Assistant WebSocket communication
  - `pydantic`: Configuration validation and data models
  - `pyyaml`: Configuration file parsing
- **Development Tools**:
  - `pytest`: Testing framework
  - `ruff`: Code formatting and linting
  - `mypy`: Type checking
  - `uv`: Dependency management, virtual environment and build

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gazpar2HAWS                            │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐   │
│  │  Bridge  │───▶│  Gazpar  │───▶│ HomeAssistantWS    │───┼──▶ Home Assistant
│  └──────────┘    └──────────┘    └────────────────────┘   │    (WebSocket)
│       │               │                                     │
│       │               ▼                                     │
│       │          ┌─────────┐                               │
│       │          │ Pricer  │                               │
│       │          └─────────┘                               │
│       │               │                                     │
│       ▼               ▼                                     │
│  ┌──────────────────────────┐                              │
│  │   Configuration Model    │                              │
│  └──────────────────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
        ▲
        │
   ┌────┴────┐
   │ PyGazpar │ ──▶ GrDF API
   └─────────┘
```

### Component Overview

#### 1. **Entry Point** (`__main__.py`)
- Parses command-line arguments
- Loads configuration files (`configuration.yaml`, `secrets.yaml`)
- Sets up logging
- Initializes and runs the Bridge

#### 2. **Bridge** (`bridge.py`)
- **Orchestrator** for the entire application
- Manages the scan interval loop
- Coordinates between Gazpar instances and Home Assistant
- Handles graceful shutdown (SIGINT, SIGTERM)
- Responsibilities:
  - Connect to Home Assistant WebSocket
  - Iterate through configured devices
  - Call `gazpar.publish()` for each device
  - Disconnect and wait for next scan interval

#### 3. **Gazpar** (`gazpar.py`)
- **Core business logic** for data retrieval and publishing
- One instance per configured device (PCE identifier)
- Responsibilities:
  - Fetch gas consumption data from GrDF via PyGazpar
  - Extract volume and energy data from GrDF response
  - Calculate costs using Pricer
  - Publish statistics to Home Assistant (volume, energy, costs)
  - Handle sensor migration (v0.3.x → v0.4.0+)
  - Manage `reset` flag for clearing historical data

#### 4. **Pricer** (`pricer.py`)
- **Cost calculation engine**
- Supports flexible pricing components with dual pricing models:
  - **Quantity-based** pricing: `quantity_value` (e.g., €/kWh)
  - **Time-based** pricing: `time_value` (e.g., €/month, €/year)
- Handles VAT rates and time-varying prices
- Returns `CostBreakdown` with separate cost components
- Key methods:
  - `get_composite_price_array()`: Build composite price arrays with quantity and time components
  - `compute()`: Calculate costs from quantities and prices

#### 5. **HomeAssistantWS** (`haws.py`)
- **Home Assistant WebSocket client**
- Manages WebSocket connection lifecycle
- Sends statistics to Home Assistant Recorder
- Key methods:
  - `connect()`: Establish WebSocket connection and authenticate
  - `import_statistics()`: Send statistics to Recorder
  - `get_last_statistic()`: Query last recorded statistic
  - `clear_statistics()`: Clear statistics for sensor (used with `reset: true`)
  - `disconnect()`: Close WebSocket connection

#### 6. **Configuration** (`configuration.py`, `config_utils.py`, `model.py`)
- **Configuration management** and validation
- `Configuration`: Main configuration class (Pydantic model)
- `config_utils`: YAML loading, secrets resolution, environment variable substitution
- `model.py`: Pydantic models for all configuration structures
  - `Device`: GrDF device configuration
  - `Pricing`: Flexible pricing components (VAT, custom components)
  - `CompositePriceValue`: Dual-component pricing (quantity + time)
  - `CostBreakdown`: Cost calculation result

#### 7. **Utilities**
- `date_array.py`: Date-indexed array operations (slicing, cumsum, interpolation)
- `datetime_utils.py`: Timezone and date handling utilities
- `version.py`: Version information

### Data Flow

1. **Configuration Loading**:
   ```
   configuration.yaml + secrets.yaml
         ↓
   config_utils.load_config() + resolve_secrets()
         ↓
   Configuration (Pydantic validation)
   ```

2. **Data Retrieval**:
   ```
   PyGazpar.login() → PyGazpar.get_data()
         ↓
   GrDF JSON response
         ↓
   Gazpar.extract_property_from_daily_gazpar_history()
         ↓
   Volume & Energy DateArrays
   ```

3. **Cost Calculation**:
   ```
   Pricing configuration
         ↓
   Pricer.get_composite_price_array()
         ↓
   CompositePriceArray (quantity + time components)
         ↓
   Pricer.compute()
         ↓
   CostBreakdown (component1_cost, component2_cost, ..., total_cost)
   ```

4. **Publishing to Home Assistant**:
   ```
   Volume, Energy, Costs (DateArrays)
         ↓
   Gazpar.publish_date_array()
         ↓
   HomeAssistantWS.import_statistics()
         ↓
   Home Assistant Recorder
   ```

### Design Patterns

#### 1. **Pydantic Models**
All configuration and data structures use Pydantic for:
- Automatic validation
- Type safety
- Field defaults and constraints
- Secret handling (e.g., `SecretStr` for passwords)

#### 2. **DateArray Abstraction**
`DateArray` class provides:
- Date-indexed data storage
- Slicing by date ranges
- Cumulative sum operations
- Interpolation for missing dates
- Used for volume, energy, and cost time series

#### 3. **Async/Await**
WebSocket communication and I/O operations use async patterns:
- `asyncio` for event loop
- `async def` for coroutines
- `await` for I/O operations

#### 4. **Factory Pattern**
Configuration loading uses factories:
- `Configuration.load()` creates validated configuration from YAML files
- Handles secrets resolution and environment variable substitution

---

## Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **uv**: 0.13 or higher
- **Git**: For version control
- **Home Assistant**: Running instance for integration testing (optional)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ssenart/gazpar2haws.git
   cd gazpar2haws
   ```

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Activate virtual environment** (or prefix the commands with `uv run`):
   ```bash
   source .venv/bin/activate
   ```

### Configuration for Development

1. **Create configuration files**:
   ```bash
   mkdir -p config
   cp tests/config/example_1.yaml config/configuration.yaml
   cp tests/config/secrets_example.yaml config/secrets.yaml
   ```

2. **Edit secrets** with your credentials:
   ```yaml
   # config/secrets.yaml
   grdf.username: "your-email@example.com"
   grdf.password: "your-password"
   homeassistant.host: "localhost"
   homeassistant.port: "8123"
   homeassistant.token: "your-long-lived-access-token"
   ```

3. **Update PCE identifier** in `config/configuration.yaml`:
   ```yaml
   grdf:
     devices:
       - pce_identifier: "your-pce-number"
   ```

### Running the Application

```bash
# Run with default config paths
uv run python -m gazpar2haws

# Run with custom config paths
uv run python -m gazpar2haws --config /path/to/config.yaml --secrets /path/to/secrets.yaml

# Run with debug logging
# (Edit config/configuration.yaml: logging.level: debug)
uv run python -m gazpar2haws
```

---

## Code Structure

### Directory Layout

```
gazpar2haws/
├── gazpar2haws/           # Source code
│   ├── __init__.py
│   ├── __main__.py        # Entry point
│   ├── bridge.py          # Orchestrator
│   ├── gazpar.py          # Business logic
│   ├── haws.py            # Home Assistant WebSocket client
│   ├── pricer.py          # Cost calculation
│   ├── configuration.py   # Configuration model
│   ├── config_utils.py    # Config loading utilities
│   ├── model.py           # Pydantic models
│   ├── date_array.py      # Date-indexed array
│   ├── datetime_utils.py  # Date/time utilities
│   └── version.py         # Version info
├── tests/                 # Test suite
│   ├── config/            # Test configurations
│   ├── test_*.py          # Test modules
│   └── conftest.py        # Pytest fixtures
├── docker/                # Docker configuration
├── addons/                # Home Assistant add-on
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
├── README.md              # User documentation
├── FAQ.md                 # Frequently asked questions
├── CHANGELOG.md           # Version history
├── MIGRATIONS.md          # Migration guides
└── TODO.md                # Test coverage TODO
```

### Module Descriptions

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `__main__.py` | Application entry point | `main()` |
| `bridge.py` | Application orchestrator | `Bridge` |
| `gazpar.py` | GrDF data retrieval & publishing | `Gazpar` |
| `haws.py` | Home Assistant WebSocket client | `HomeAssistantWS` |
| `pricer.py` | Cost calculation engine | `Pricer` |
| `configuration.py` | Configuration model | `Configuration` |
| `config_utils.py` | Config loading utilities | `load_config()`, `resolve_secrets()` |
| `model.py` | Data models | `Device`, `Pricing`, `CompositePriceValue`, `CostBreakdown` |
| `date_array.py` | Date-indexed arrays | `DateArray` |
| `datetime_utils.py` | Date/time utilities | Various date functions |

### Key Files

- **`pyproject.toml`**: Project metadata, dependencies, tool configurations
- **`uv.lock`**: Locked dependency versions
- **`.github/workflows/`**: CI/CD workflows (build, test, publish)
- **`Dockerfile`**: Docker image build configuration
- **`tests/config/example_*.yaml`**: Example configurations for testing

---

## Development Workflow

### Git Conventions

This project follows **[Conventional Commits](https://www.conventionalcommits.org/)** and **[Semantic Versioning](https://semver.org/)** specifications.

#### Git Branching Strategy (Gitflow)

This project uses the **[Gitflow](https://nvie.com/posts/a-successful-git-branching-model/)** branching model for managing releases and development.

**Main Branches** (permanent):
- `main` – Production-ready code. Every commit represents a released version.
- `develop` – Integration branch for features. Contains the latest development changes for the next release.

**Supporting Branches** (temporary):
- `feature/*` – New features (branch from `develop`, merge back to `develop`)
- `release/*` – Release preparation (branch from `develop`, merge to `main` and `develop`)
- `hotfix/*` – Urgent production fixes (branch from `main`, merge to `main` and `develop`)
- `bugfix/*` – Bug fixes (branch from `develop`, merge back to `develop`)

**Workflow Diagram**:

```
main        ──●────────────●────────●────────▶
              │  hotfix/   │        │ release
              │            │        │
develop  ─────●────●───●───●────●───●────────▶
                   │   │        │
feature/          ●───●        ●────●
                 feature/    feature/
```

**Detailed Workflow**:

1. **Feature Development**:
   ```bash
   # Create feature branch from develop
   git checkout develop
   git pull origin develop
   git checkout -b feature/123-my_new_feature

   # Work on feature...
   git add .
   git commit -m "feat: add new feature (#123)"

   # Merge back to develop when complete
   git checkout develop
   git merge --no-ff feature/123-my_new_feature
   git push origin develop
   git branch -d feature/123-my_new_feature
   ```

2. **Release Preparation**:
   ```bash
   # Create release branch from develop
   git checkout develop
   git checkout -b release/0.6.0

   # Bump version in pyproject.toml
   # Update CHANGELOG.md
   # Perform final testing and bug fixes
   git commit -m "chore: prepare release 0.6.0"

   # Merge to main
   git checkout main
   git merge --no-ff release/0.6.0
   git tag -a v0.6.0 -m "Release version 0.6.0"
   git push origin main --tags

   # Merge back to develop
   git checkout develop
   git merge --no-ff release/0.6.0
   git push origin develop

   # Delete release branch
   git branch -d release/0.6.0
   ```

3. **Hotfix for Production**:
   ```bash
   # Create hotfix branch from main
   git checkout main
   git checkout -b hotfix/0.6.1-critical_fix

   # Fix the issue
   git add .
   git commit -m "fix: resolve critical security issue (#456)"

   # Bump version to 0.6.1
   # Update CHANGELOG.md
   git commit -m "chore: bump version to 0.6.1"

   # Merge to main
   git checkout main
   git merge --no-ff hotfix/0.6.1-critical_fix
   git tag -a v0.6.1 -m "Hotfix version 0.6.1"
   git push origin main --tags

   # Merge back to develop
   git checkout develop
   git merge --no-ff hotfix/0.6.1-critical_fix
   git push origin develop

   # Delete hotfix branch
   git branch -d hotfix/0.6.1-critical_fix
   ```

4. **Bug Fixes** (non-urgent):
   ```bash
   # Create bugfix branch from develop
   git checkout develop
   git checkout -b bugfix/789-fix_validation_error

   # Fix the bug
   git commit -m "fix: correct validation logic (#789)"

   # Merge back to develop
   git checkout develop
   git merge --no-ff bugfix/789-fix_validation_error
   git push origin develop
   git branch -d bugfix/789-fix_validation_error
   ```

**Branch Lifetime**:
- `main` and `develop` – Permanent (never deleted)
- `feature/*`, `bugfix/*` – Exist until merged to `develop`, then deleted
- `release/*` – Exist until merged to `main` and `develop`, then deleted
- `hotfix/*` – Exist until merged to `main` and `develop`, then deleted

**Key Principles**:
- Never commit directly to `main` or `develop` (except emergency hotfixes)
- Use `--no-ff` (no fast-forward) for merges to preserve branch history
- Always tag releases on `main` with version number
- Keep `develop` up-to-date with `main` after releases/hotfixes

**Why Gitflow?**
✅ Clear separation between production and development code
✅ Structured release process
✅ Parallel development of features
✅ Support for emergency hotfixes
✅ Clean and traceable history

**Reference**: [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/) by Vincent Driessen

#### Branch Naming

**Format**: `<type>/<issue-id>-<brief_description>`

Use underscores (`_`) to separate words in the description (consistent with Python snake_case convention).

**Branch Types**:
- `feature/` – New features
- `fix/` or `bugfix/` – Bug fixes
- `docs/` – Documentation only changes
- `refactor/` – Code refactoring (no functional changes)
- `test/` – Adding or updating tests
- `chore/` – Maintenance tasks (dependencies, tooling)
- `hotfix/` – Urgent production fixes
- `release/` – Release preparation

**Examples**:
```bash
feature/108-flexible_pricing_components
fix/109-invalid_statistic_id_error
docs/110-update_developer_guide
refactor/111-simplify_pricer_logic
test/112-add_config_utils_tests
chore/113-update_dependencies
hotfix/114-critical_security_patch
release/0.5.0
```

#### Commit Messages

**Format**:
```
<type>[optional scope]: <description> (#<issue-id>)

[optional body]

[optional footer(s)]
```

**Commit Types**:
- `feat` – New feature
- `fix` – Bug fix
- `docs` – Documentation changes
- `style` – Code style (formatting, no logic change)
- `refactor` – Code refactoring
- `perf` – Performance improvements
- `test` – Adding or updating tests
- `build` – Build system changes
- `ci` – CI/CD changes
- `chore` – Maintenance tasks
- `revert` – Revert previous commit

**Scope** (optional): Component being changed
```bash
feat(pricer): add composite price support
fix(haws): resolve WebSocket connection timeout
docs(readme): update installation instructions
```

**Description Rules**:
- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Keep under 72 characters
- Include `(#123)` for issue reference

**Body** (optional):
- Explain what and why, not how
- Wrap at 72 characters per line
- Separated from description by blank line

**Footer** (optional):
- `Closes #123` – Auto-closes issue on merge
- `Fixes #123` – Auto-closes bug issue on merge
- `Resolves #123` – Auto-closes issue on merge
- `Refs #123` – References issue without closing
- `BREAKING CHANGE:` – Describes breaking changes

**Examples**:

```bash
# Simple commit
feat: add flexible pricing components (#108)

# With scope
feat(pricer): add flexible pricing components (#108)

# With body
feat: add flexible pricing components (#108)

Implements unlimited custom pricing component names instead of being
limited to 4 hardcoded names. Users can now define components like
carbon_tax, distribution_cost, peak_rate, etc.

# With footer (auto-closes issue on merge)
feat: add flexible pricing components (#108)

Implements unlimited custom pricing component names instead of being
limited to 4 hardcoded names.

Closes #108

# Breaking change
feat!: change pricing configuration format (#83)

BREAKING CHANGE: Pricing configuration format has changed.
- Renamed `value` to `quantity_value`/`time_value`
- Renamed `value_unit` to `price_unit`
- Renamed `base_unit` to `quantity_unit`/`time_unit`

See MIGRATIONS.md for upgrade instructions.

Closes #83

# Multiple issues
fix: resolve entity naming and validation issues (#109, #92)

- Ensure entity names follow HA conventions
- Add validation for uppercase/special characters
- Update documentation with naming rules

Fixes #109, #92
```

**GitHub Auto-linking & Auto-closing**:
- Any `#123` in commit message creates clickable link to issue
- Keywords `Closes`, `Fixes`, `Resolves` in body/footer auto-close issues on merge to main
- Use `(#123)` in description for visibility in `git log --oneline`
- Use `Closes #123` in footer to auto-close issue

#### Quick Reference

```bash
# Create branch
git checkout -b feature/123-brief_description

# Commit during development
git commit -m "feat: add validation logic (#123)"
git commit -m "feat: add unit tests (#123)"
git commit -m "feat: update documentation (#123)"

# Final commit when merging (squash commits if needed)
git commit -m "feat: add flexible pricing components (#123)

Detailed explanation of the feature.

Closes #123"
```

### Making Changes

Follow this workflow for feature development (using Gitflow):

1. **Ensure you have the latest develop branch**:
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Create a feature branch from develop**:
   ```bash
   git checkout -b feature/123-my_feature
   ```

3. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation

4. **Run code quality checks**:
   ```bash
   # Format and lint code
   uv run ruff format gazpar2haws
   uv run ruff check gazpar2haws

   # Type check
   uv run mypy gazpar2haws
   ```

5. **Run tests**:
   ```bash
   uv run pytest
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature (#123)"
   ```

7. **Push your feature branch**:
   ```bash
   git push origin feature/123-my_feature
   ```

8. **Create a pull request**:
   - Target: `develop` branch (not `main`)
   - Title: Use conventional commit format
   - Description: Reference the issue, describe changes, testing done
   - Request review from maintainers

9. **After PR approval and merge**:
   ```bash
   # Update your local develop branch
   git checkout develop
   git pull origin develop

   # Delete the feature branch
   git branch -d feature/123-my_feature
   ```

**Note**: For urgent production **hotfixes**, branch from `main` instead of `develop` and merge to both `main` and `develop`.

---

## Testing

### Testing Strategy Overview

This project uses multiple testing approaches for comprehensive coverage:

| Testing Type | Tool/Method | Location | Use Case |
|--------------|-------------|----------|----------|
| **Unit Tests** | pytest | `tests/test_*.py` | Fast feedback for core logic |
| **Integration Tests** | pytest + HA container | `tests/test_haws.py` | WebSocket API validation |
| **Add-on E2E Testing** | DevContainer + HA | [.devcontainer/README.md](../.devcontainer/README.md) | Full add-on deployment testing |
| **Multi-arch Builds** | Docker buildx | CI/CD pipeline | Architecture compatibility |

**For complete add-on testing guide with step-by-step instructions, see [.devcontainer/README.md](../.devcontainer/README.md)**

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── conftest.py              # Pytest fixtures
├── test_bridge.py           # Bridge tests
├── test_gazpar.py           # Gazpar tests
├── test_haws.py             # Home Assistant WS tests
├── test_pricer.py           # Pricer tests
├── test_date_array.py       # DateArray tests
├── test_configuration.py    # Configuration tests
└── config/                  # Test configuration files
    ├── example_1.yaml       # Basic configuration
    ├── example_2.yaml       # With pricing
    └── secrets_example.yaml # Secrets template
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gazpar2haws --cov-report=html

# Run specific test file
uv run pytest tests/test_pricer.py

# Run specific test
uv run pytest tests/test_pricer.py::test_compute_cost

# Run with verbose output
uv run pytest -v

# Run with debug output
uv run pytest -s
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from gazpar2haws.pricer import Pricer
from gazpar2haws.model import Pricing

def test_compute_cost_basic():
    """Test basic cost computation with quantity-based pricing"""
    # Arrange
    pricing = Pricing(
        vat=[{"id": "normal", "start_date": "2023-01-01", "value": 0.20}],
        consumption_prices=[
            {
                "start_date": "2023-01-01",
                "quantity_value": 0.10,
                "quantity_unit": "kWh",
                "price_unit": "€",
                "vat_id": "normal"
            }
        ]
    )
    pricer = Pricer(pricing)

    # Act
    result = pricer.compute(quantities=[100], start_date="2023-01-01")

    # Assert
    assert result.consumption_cost == pytest.approx(12.0)  # 100 * 0.10 * 1.20
```

#### Async Test Example

```python
import pytest
from gazpar2haws.haws import HomeAssistantWS

@pytest.mark.asyncio
async def test_connect_success(mock_websocket):
    """Test successful WebSocket connection"""
    # Arrange
    haws = HomeAssistantWS("localhost", 8123, "/api/websocket", "token")

    # Act
    await haws.connect()

    # Assert
    assert haws.is_connected()
```

### Test Coverage

Current test coverage goals (see [TODO.md](TODO.md) for details):

| Module | Current | Target |
|--------|---------|--------|
| config_utils.py | 0% | 90%+ |
| model.py | 10% | 80%+ |
| bridge.py | 20% | 80%+ |
| gazpar.py | 60% | 85%+ |
| pricer.py | 75% | 90%+ |
| haws.py | 85% | 90%+ |
| date_array.py | 80% | 90%+ |

**View coverage report**:
```bash
uv run pytest --cov=gazpar2haws --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Mocking

Tests use `unittest.mock` or `pytest-mock` for mocking external dependencies:

```python
from unittest.mock import Mock, patch

@patch('gazpar2haws.gazpar.Client')
def test_gazpar_fetch_data(mock_client):
    """Test GrDF data fetching"""
    # Arrange
    mock_client.return_value.get_data.return_value = {"data": [...]}

    # Act & Assert
    # ... test code
```

---

## Code Quality

### Code Formatting and Linting

**Ruff** is used for code formatting and linting:
```bash
# Format all code
uv run ruff format gazpar2haws tests

# Check formatting without changes
uv run ruff format --check gazpar2haws tests

# Lint code
uv run ruff check gazpar2haws tests
```

### Type Checking

**mypy** is used for static type checking:
```bash
uv run mypy gazpar2haws
```

### Configuration

Tool configurations are in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
# E501 is ignored: ruff format owns the line length, and long strings are left as they are.
select = ["E", "F", "W", "I", "B", "UP", "ARG", "RET", "BLE"]
ignore = ["E501"]
```

### Pre-commit Checks

Before committing, run:
```bash
# Format and lint
uv run ruff format gazpar2haws tests
uv run ruff check gazpar2haws tests

# Type check
uv run mypy gazpar2haws tests

# Test
uv run pytest
```

---

## Contributing

### Guidelines

1. **Read existing documentation**: FAQ, README, CHANGELOG
2. **Check open issues**: Avoid duplicate work
3. **Create an issue first**: For significant changes, discuss in an issue
4. **Write tests**: All new features must have tests
5. **Update documentation**: Update relevant docs (README, FAQ, etc.)
6. **Follow code style**: Run `ruff format` and pass `ruff check` and mypy
7. **Write clear commit messages**: Follow conventional commits

### Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** with tests and documentation
3. **Run all quality checks** (formatting, linting, tests)
4. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable
5. **Address review feedback** promptly
6. **Squash commits** if requested

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are added and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages are clear
- [ ] No sensitive data in commits

---

## Build & Release

### CI/CD Pipeline

This project uses **GitHub Actions** for automated Continuous Integration and Continuous Deployment.

#### 🔄 CI Workflow (Automated)

**File**: `.github/workflows/ci.yaml`

**Triggered on**:
- Push to `main`, `develop`, `release/*`, `feature/*` branches
- All pull requests
- Manual trigger via GitHub UI (with options to skip lint/tests)

**Jobs**:
1. **Prepare** – Read the target Python versions
2. **Lint** – Run code quality checks:
   - `ruff format --check` (formatting)
   - `ruff check` (linting: pyflakes, pycodestyle, import order, bugbear and more)
   - `mypy` (type checking)
3. **Test** – Run test suite on multiple Python versions:
   - Python 3.10, 3.11, 3.12, 3.13
   - Full pytest suite with coverage

**How to view CI results**:
- Go to the GitHub repository → "Actions" tab
- View logs and results for each workflow run
- Failed checks block PR merges

**Manual trigger**:
```bash
# Via GitHub UI:
# 1. Go to Actions → CI
# 2. Click "Run workflow"
# 3. Select branch
# 4. Optionally skip lint/tests for quick runs
```

#### 🚀 Create Release Workflow (Manual)

**File**: `.github/workflows/create-release.yaml`

**Purpose**: Release a version: validate, bump, finalize the changelog, publish, tag and create the GitHub release.

**Triggered**: Manually only, from the GitHub Actions UI or with `gh workflow run create-release.yaml --ref <branch> -f version=<version>`.

**Pipeline**:
1. **Preflight** – Validates before anything is changed:
   - The version is PEP 440 and in canonical form (`0.6.0a1`, not `0.6.0a01`).
   - The version kind matches the branch: `develop` → `aN`, `release/X.Y.Z` → `bN` or `rcN` with base `X.Y.Z`, `main` → final, `feature/*` → TestPyPI only.
   - The version is new and greater than the highest existing tag.
   - The `[Unreleased]` section of `CHANGELOG.md` is not empty.
   - The `ci.yaml` run for this exact commit succeeded.
2. **Release** (one job, in this order):
   - Bump `pyproject.toml`, `addons/gazpar2haws/config.yaml` and `addons/gazpar2haws/build.yaml`.
   - Finalize `CHANGELOG.md`: `[Unreleased]` becomes `[<version>] - <date>`, a new empty `[Unreleased]` is added above it, and the compare links are updated.
   - Build the Python package.
   - Publish to PyPI (`main`, `develop`, `release/*`) or TestPyPI (`feature/*`).
   - Build and push the Docker image. The `latest` tag is set only for final versions published from `main`.
   - Commit the bump, create the tag and push both atomically.
   - Create the GitHub release, with the changelog section as its notes.

**How to trigger**:
1. Go to GitHub repository → "Actions" tab → "Create Release" → "Run workflow".
2. Select the branch to release from. The branch decides which version kinds are allowed.
3. Fill in the parameters:
   - **Version** (required), e.g. `0.6.0a1`.
   - **Draft** (default: checked): create the GitHub release as a draft, to review it before publishing it.
   - **Dry run** (default: unchecked): validate, bump and build without pushing, publishing or releasing.
4. Click "Run workflow".

**Parameters**:
- `version` (required): the version to release, in PEP 440 form.
- `draft` (boolean, default `true`): create the GitHub release as a draft.
- `dry_run` (boolean, default `false`): run everything except push, publish and release.

**Run summary**: the job summary shows the last tag, the version channel, the publish target, the commit and the files changed.

**Failure recovery**:
- A failed preflight changes nothing.
- A failure before publishing leaves no tag: fix the cause and rerun with the same version.
- PyPI never accepts the same version twice. If PyPI already accepted the version and a later step failed, release a new version instead.
- If the final push fails after publishing (for example, because the branch moved), push the bump commit and the tag manually, then create the GitHub release by hand.

#### 🐳 Publish to DockerHub Workflow (Manual)

**File**: `.github/workflows/publish-to-dockerhub.yaml`

**Purpose**: Republish Docker image (without creating release)

**Triggered**: Manually via GitHub Actions UI only

**Use cases**:
- Rebuild Docker image for existing version
- Update `latest` tag without new release
- Test Docker build process

**How to trigger**:
1. Go to GitHub repository → "Actions" tab
2. Select "Publish to DockerHub" workflow
3. Click "Run workflow"
4. Fill in parameters:
   - **Version** (required): an existing tag, e.g. `0.6.0`
   - **Update 'latest' tag** (boolean, default unchecked): only for final versions
5. Click "Run workflow"

---

### Version Management

#### Semantic Versioning

This project follows **[Semantic Versioning](https://semver.org/)** (SemVer):

**Format**: `MAJOR.MINOR.PATCH[-prerelease][+build]`

**Version increments**:
- **MAJOR** (1.0.0 → 2.0.0) – Breaking changes, incompatible API changes
- **MINOR** (0.5.0 → 0.6.0) – New features, backward-compatible
- **PATCH** (0.5.0 → 0.5.1) – Bug fixes, backward-compatible

**Pre-release versions**:
- **Alpha** (`0.6.0a1`, `0.6.0a2`) – Early development, unstable
- **Beta** (`0.6.0b1`, `0.6.0b2`) – Feature complete, testing
- **Release Candidate** (`0.6.0rc1`) – Final testing before release

**Examples**:
```
0.5.0       → Stable release
0.6.0a1     → Alpha (early development)
0.6.0a2     → Alpha 2 (fixes/updates)
0.6.0b1     → Beta (feature-complete)
0.6.0rc1    → Release candidate
0.6.0       → Final release
0.6.1       → Patch/bugfix
```

#### Version Storage

Version is stored in multiple files:

**`pyproject.toml`** (source of truth):
```toml
[project]
version = "0.5.0"
```

**`addons/gazpar2haws/config.yaml`** (Home Assistant add-on):
```yaml
version: "0.5.0"
```

**`addons/gazpar2haws/build.yaml`** (Docker build):
```yaml
args:
  GAZPAR2HAWS_VERSION: "0.5.0"
```

**Note**: The CI/CD pipeline automatically updates all three files when creating a release.

---

### Release Process (Gitflow)

#### 1. Development Phase

**Work on features in `develop` branch**:
```bash
git checkout develop
git checkout -b feature/123-new_feature
# ... develop feature ...
git checkout develop
git merge --no-ff feature/123-new_feature
git push origin develop
```

#### 2. Release Preparation

**Create release branch from `develop`**:
```bash
git checkout develop
git checkout -b release/0.6.0
```

**Update CHANGELOG.md**: add the entries under `[Unreleased]`. The release workflow dates and versions that section:
```markdown
## [Unreleased]

### Added
- New feature X (#123)
- New feature Y (#456)

### Fixed
- Bug fix Z (#789)

### Changed
- Updated dependency A to v2.0
```

**Commit and push**:
```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v0.6.0"
git push origin release/0.6.0
```

**Test the release branch** – Run final integration tests, QA

#### 3. Merge Release to Main

**Merge the release into `main` and `develop`, before the final release**:
```bash
# Merge release to main
git checkout main
git merge --no-ff release/0.6.0
git push origin main

# Merge release back to develop
git checkout develop
git merge --no-ff release/0.6.0
git push origin develop

# Delete release branch
git branch -d release/0.6.0
git push origin --delete release/0.6.0
```

#### 4. Trigger the Release on `main`

The final version is released from `main`, after the merge in step 3.

**Go to GitHub Actions** → "Create Release" workflow (on branch `main`):
- **Version**: `0.6.0`
- **Draft**: ✅ (checked, publish the GitHub release after review)

**What happens automatically** (see [Create Release Workflow](#-create-release-workflow-manual) above):
1. Validates the version, the branch and the CI status
2. Bumps the version files and finalizes `CHANGELOG.md`
3. Publishes to PyPI and builds the Docker image
4. Commits the bump, tags `0.6.0` and pushes both
5. Creates the GitHub release (draft)

#### 5. Publish the GitHub Release

The workflow creates the GitHub release as a draft, with the changelog section as its notes. Go to GitHub → Releases, check the notes and publish the release.

---

### Hotfix Process

For urgent production fixes:

#### 1. Create Hotfix Branch from Main

```bash
git checkout main
git checkout -b hotfix/0.5.1-critical_security_fix
```

#### 2. Make the Fix

```bash
# Fix the issue
git add .
git commit -m "fix: resolve critical security vulnerability (#999)"
```

#### 3. Update CHANGELOG

```markdown
## [0.5.1] - 2026-02-01

### Fixed
- Critical security vulnerability in authentication (#999)
```

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v0.5.1"
git push origin hotfix/0.5.1-critical_security_fix
```

#### 4. Merge Hotfix

```bash
# Merge to main
git checkout main
git merge --no-ff hotfix/0.5.1-critical_security_fix
git push origin main

# Merge to develop
git checkout develop
git merge --no-ff hotfix/0.5.1-critical_security_fix
git push origin develop

# Delete hotfix branch
git branch -d hotfix/0.5.1-critical_security_fix
```


#### 5. Trigger the Release on `main`

After the merge in step 4.

**GitHub Actions** → "Create Release":
- **Version**: `0.5.1` (on `main`)
- **Draft**: ❌ (unchecked, publish right away)

---

### Pre-release Process (Alpha/Beta)

For testing releases before final:

#### Alpha Release (Early Development)

```bash
# In develop branch
git checkout develop

# GitHub Actions → "Create Release"
# Version: 0.6.0a1
```

**Published to**:
- PyPI as `0.6.0a1`
- DockerHub as `0.6.0a1` (NOT `latest`)
- TestPyPI (if not from main/develop)

#### Beta Release (Feature Complete)

```bash
# In release branch
git checkout release/0.6.0

# GitHub Actions → "Create Release"
# Version: 0.6.0b1
```

#### Release Candidate

```bash
# In release branch
git checkout release/0.6.0

# GitHub Actions → "Create Release"
# Version: 0.6.0rc1
```

---

### Local Build & Testing

#### Build Python Package Locally

```bash
# Install build dependencies
uv sync

# Build wheel and source distribution
uv build

# Output in dist/
ls dist/
# gazpar2haws-0.5.0-py3-none-any.whl
# gazpar2haws-0.5.0.tar.gz
```

#### Build Docker Image Locally

```bash
# Build image
cd docker
docker build -t gazpar2haws:dev .

# Test image
docker run --rm gazpar2haws:dev --version
```

#### Test PyPI Package Locally

```bash
# Install from local build
pip install dist/gazpar2haws-0.5.0-py3-none-any.whl

# Or install in editable mode for development
uv sync
```

---

### CI/CD Secrets Configuration

Required GitHub Secrets (configured in repository settings):

**Docker**:
- `DOCKERHUB_USERNAME` – DockerHub username
- `DOCKERHUB_PASSWORD` – DockerHub access token

**PyPI** (uses Trusted Publishing, no tokens needed):
- Configured in PyPI project settings
- GitHub Actions OIDC authentication

**How to configure secrets**:
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add repository secrets
3. Never commit secrets to code!

---

### Monitoring CI/CD

#### View Workflow Runs

**GitHub UI**:
- Repository → Actions tab
- Filter by workflow name
- View logs, artifacts, and status

#### Check Build Status

**Badges** (add to README.md):
```markdown
![CI](https://github.com/ssenart/gazpar2haws/workflows/CI/badge.svg)
```

#### Download Artifacts

**After workflow completion**:
1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download built packages

---

### Troubleshooting CI/CD

#### CI Fails on Lint

**Problem**: Code doesn't pass linting checks

**Solution**:
```bash
# Run locally before pushing
uv run ruff format gazpar2haws tests
uv run ruff check gazpar2haws tests
uv run mypy gazpar2haws tests
```

#### CI Fails on Tests

**Problem**: Tests fail in CI but pass locally

**Solution**:
- Check Python version compatibility (CI tests 3.10-3.13)
- Check for environment-specific dependencies
- Review CI logs for specific failure

#### Release Workflow Fails

**Common issues**:
- Invalid version format (must follow SemVer)
- Git tag already exists
- PyPI version already published
- Missing DockerHub credentials

**Solution**: Check workflow logs for specific error message

---

### Summary: Release Checklist

**For Standard Release**:
- [ ] Create `release/X.Y.Z` branch from `develop`
- [ ] Update CHANGELOG.md
- [ ] Test the release branch
- [ ] Trigger "Create Release" workflow (version `X.Y.Z`, final=true)
- [ ] Verify PyPI publication: https://pypi.org/project/gazpar2haws/
- [ ] Verify DockerHub: https://hub.docker.com/r/ssenart/gazpar2haws
- [ ] Merge release to `main`
- [ ] Merge release back to `develop`
- [ ] Delete release branch
- [ ] Create GitHub Release (optional)

**For Hotfix**:
- [ ] Create `hotfix/X.Y.Z-description` from `main`
- [ ] Fix the issue and update CHANGELOG
- [ ] Trigger "Create Release" workflow (version `X.Y.Z`, final=true)
- [ ] Merge hotfix to `main`
- [ ] Merge hotfix to `develop`
- [ ] Delete hotfix branch

**For Pre-release** (Alpha/Beta):
- [ ] Trigger "Create Release" workflow (version `X.Y.Za1/b1`, final=false)
- [ ] Test the pre-release
- [ ] Gather feedback
- [ ] Iterate or proceed to final release

---

## Troubleshooting

### Common Development Issues

#### Issue: Lock file conflicts

**Solution**:
```bash
uv lock
git add uv.lock
```

#### Issue: Tests fail with "Connection refused"

**Solution**: Ensure you're not trying to connect to a real Home Assistant instance in unit tests. Use mocks:
```python
@patch('gazpar2haws.haws.websockets.connect')
def test_my_function(mock_connect):
    # ... test code
```

#### Issue: Import errors in tests

**Solution**: Install the package in development mode:
```bash
uv sync
```

#### Issue: Coverage report not generated

**Solution**: Install coverage plugin:
```bash
uv add --group dev pytest-cov
```

### Debugging

#### Enable debug logging

In your test configuration:
```yaml
logging:
  level: debug
  console: true
```

#### Debug with pytest

```bash
# Run with verbose output
uv run pytest -v -s

# Debug specific test
uv run pytest tests/test_file.py::test_name -v -s

# Drop into debugger on failure
uv run pytest --pdb
```

#### Debug in IDE

Most IDEs (PyCharm, VSCode) support debugging pytest tests directly. Set breakpoints and run tests in debug mode.

### Getting Help

- **GitHub Issues**: https://github.com/ssenart/gazpar2haws/issues
- **GitHub Discussions**: https://github.com/ssenart/gazpar2haws/discussions
- **FAQ**: [FAQ.md](FAQ.md)

---

## Additional Resources

- **User Documentation**: [README.md](../README.md)
- **Migration Guides**: [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)
- **Frequently Asked Questions**: [FAQ.md](FAQ.md)
- **Version History**: [CHANGELOG.md](../CHANGELOG.md)
- **Test Coverage TODO**: [TODO.md](TODO.md)
- **Flexible Pricing Guide**: [FLEXIBLE_PRICING_GUIDE.md](FLEXIBLE_PRICING_GUIDE.md)

---

**Last Updated**: 2026-01-31
**Version**: 0.5.0
**Maintainer**: Stéphane Senart