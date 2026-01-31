# Src Layout Migration Plan

This document provides a comprehensive plan for migrating Gazpar2HAWS from a flat layout to a src layout structure.

---

## Table of Contents

- [Overview](#overview)
- [Rationale](#rationale)
- [Impact Analysis](#impact-analysis)
- [Migration Steps](#migration-steps)
- [File Changes Checklist](#file-changes-checklist)
- [Testing Plan](#testing-plan)
- [Rollback Plan](#rollback-plan)
- [Timeline](#timeline)
- [Post-Migration](#post-migration)

---

## Overview

### Current Structure (Flat Layout)

```
gazpar2haws/
├── gazpar2haws/                 # Source code at root level
│   ├── __init__.py
│   ├── __main__.py
│   ├── bridge.py
│   ├── configuration.py
│   ├── config_utils.py
│   ├── date_array.py
│   ├── datetime_utils.py
│   ├── gazpar.py
│   ├── haws.py
│   ├── model.py
│   ├── pricer.py
│   └── version.py
├── tests/
├── docs/
├── docker/
├── addons/
├── pyproject.toml
├── poetry.lock
└── README.md
```

### Target Structure (Src Layout)

```
gazpar2haws/
├── src/
│   └── gazpar2haws/             # Source code under src/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bridge.py
│       ├── configuration.py
│       ├── config_utils.py
│       ├── date_array.py
│       ├── datetime_utils.py
│       ├── gazpar.py
│       ├── haws.py
│       ├── model.py
│       ├── pricer.py
│       └── version.py
├── tests/                       # Tests remain at root
├── docs/
├── docker/
├── addons/
├── pyproject.toml
├── poetry.lock
└── README.md
```

---

## Rationale

### Why Migrate?

#### ✅ Benefits

1. **Better Isolation**
   - Source code is isolated from project metadata
   - Prevents accidental imports from local directory
   - Forces proper package installation

2. **Industry Best Practice**
   - Recommended by [Python Packaging Authority](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
   - Used by modern Python projects
   - Aligns with PEP 517/518 standards

3. **Improved Testing**
   - Tests run against installed package, not source directory
   - Catches packaging issues early
   - Ensures tests reflect real-world usage

4. **Cleaner Project Structure**
   - Clear separation between source and project files
   - Easier navigation for contributors
   - Professional project organization

5. **Build System Compatibility**
   - Works better with Poetry and modern build tools
   - Prevents common packaging mistakes
   - Better editable install support

#### ⚠️ Costs

1. **Migration Effort**
   - ~2-3 hours work
   - Updates to ~15+ files
   - Thorough testing required

2. **Breaking Change**
   - Development workflows need adjustment
   - CI/CD pipelines need updates
   - Documentation updates required

3. **One Extra Directory Level**
   - Slightly longer paths
   - More nesting in file browser

### Decision

**Proceed with migration** for the following reasons:
- ✅ Project is pre-1.0 (v0.5.0) – good time for structural changes
- ✅ Active development – establishing best practices early
- ✅ Professional project – benefit from industry standards
- ✅ Using Poetry – handles src layout well
- ✅ Strong CI/CD – will catch migration issues

---

## Impact Analysis

### Affected Components

| Component | Impact Level | Changes Required |
|-----------|-------------|------------------|
| **Source code** | 🔴 High | Move to src/ directory |
| **pyproject.toml** | 🔴 High | Update package path, tool configs |
| **GitHub Actions** | 🟡 Medium | Update paths in workflows |
| **Docker** | 🟡 Medium | Update COPY paths |
| **Add-on** | 🟡 Medium | Update run.sh paths (if any) |
| **Tests** | 🟢 Low | No changes (imports still work) |
| **Documentation** | 🟡 Medium | Update structure diagrams |
| **Developer workflows** | 🟡 Medium | Re-run poetry install |

### Breaking Changes

**For Contributors:**
- Must run `poetry install` after pulling changes
- IDE configurations might need updates
- Local scripts using direct imports will break

**For End Users:**
- ✅ **No impact** – Published packages work the same
- ✅ **No API changes** – All imports remain `from gazpar2haws import ...`

**For CI/CD:**
- Workflow paths need updates
- Docker builds need path adjustments
- Tool configurations need updates

---

## Migration Steps

### Prerequisites

- [ ] All current PRs merged or rebased
- [ ] Working directory is clean (`git status` shows no changes)
- [ ] All tests passing
- [ ] On `develop` branch

### Step 1: Preparation (10 minutes)

#### 1.1 Create Migration Branch

```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create migration branch
git checkout -b refactor/migrate-to-src-layout
```

#### 1.2 Backup Current State

```bash
# Tag current state for easy rollback
git tag -a pre-src-layout -m "Backup before src layout migration"
```

#### 1.3 Document Current State

```bash
# Save current test results
poetry run pytest --verbose > migration-backup/test-results-before.txt

# Save current structure
tree -L 3 > migration-backup/structure-before.txt
```

### Step 2: Move Source Code (5 minutes)

#### 2.1 Create src Directory

```bash
mkdir src
```

#### 2.2 Move gazpar2haws Package

```bash
git mv gazpar2haws src/
```

#### 2.3 Verify Move

```bash
# Check new structure
ls -la src/gazpar2haws/

# Should show all Python files:
# __init__.py, __main__.py, bridge.py, configuration.py, etc.
```

### Step 3: Update pyproject.toml (15 minutes)

#### 3.1 Update Package Configuration

Edit `pyproject.toml`:

```toml
[tool.poetry]
name = "gazpar2haws"
version = "0.5.0"
description = "Gazpar2HAWS is a gateway that reads data history from the GrDF (French gas provider) meter and send it to Home Assistant using WebSocket interface"
license = { file = "LICENSE" }
readme = "README.md"
requires-python = ">=3.10"
authors = [
    { name = "Stéphane Senart" }
]

# ADD THIS LINE - tells Poetry where to find the package
packages = [{include = "gazpar2haws", from = "src"}]

# ... rest of configuration ...
```

#### 3.2 Update Tool Configurations

```toml
[tool.pytest.ini_options]
# ADD these lines for pytest
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mypy]
exclude = [ ".venv" ]
# ADD this line for mypy
mypy_path = "src"

[[tool.mypy.overrides]]
module = "tests.*"
check_untyped_defs = false

[tool.coverage.run]
# ADD this line for coverage
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[tool.isort]
profile = "black"
skip = ".venv"
# UPDATE this line for isort
src_paths = ["src", "tests"]
```

#### 3.3 Complete pyproject.toml Example

Full updated section:

```toml
[project]
name = "gazpar2haws"
version = "0.5.0"
description = "Gazpar2HAWS is a gateway that reads data history from the GrDF (French gas provider) meter and send it to Home Assistant using WebSocket interface"
license = { file = "LICENSE" }
readme = "README.md"
requires-python = ">=3.10"
authors = [{ name = "Stéphane Senart" }]
classifiers = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "pygazpar>=1.3.1",
    "websockets>=14.1",
    "pyyaml>=6.0.2",
    "pydantic[email] (>=2.10.6,<3.0.0)",
    "pydantic-extra-types (>=2.10.2,<3.0.0)",
]

[tool.poetry]
requires-poetry = ">=2.0"
include = ["CHANGELOG.md"]
packages = [{include = "gazpar2haws", from = "src"}]

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.4"
pytest-asyncio = "^0.25.0"
flake8-pyproject = "^1.2.3"
pylint = "^3.3.4"
black = "^25.1.0"
flake8 = "^7.1.1"
isort = "^6.0.0"
mypy = "^1.14.1"
ruff = "^0.9.4"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

[tool.pylint.'MESSAGES CONTROL']
ignore = ".venv"
max-line-length = 120
disable = "C,W1203,R0902,R0913,R0914,R0917,R0801"

[tool.black]
exclude = ".venv"
line-length = 120

[tool.flake8]
max-line-length = 120
extend-ignore = [ "E203", "W503", "E704", "E501" ]
exclude = [".venv"]

[tool.isort]
profile = "black"
skip = ".venv"
src_paths = ["src", "tests"]

[tool.mypy]
exclude = [ ".venv" ]
mypy_path = "src"

[[tool.mypy.overrides]]
module = "tests.*"
check_untyped_defs = false

[tool.ruff]
exclude = [ ".venv" ]
line-length = 120

[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Step 4: Update Docker Files (10 minutes)

#### 4.1 Update docker/Dockerfile

```dockerfile
# Before
FROM python:3.12-slim

WORKDIR /app

# Copy source code
COPY gazpar2haws /app/gazpar2haws
COPY pyproject.toml poetry.lock /app/

# After
FROM python:3.12-slim

WORKDIR /app

# Copy source code
COPY src /app/src
COPY pyproject.toml poetry.lock /app/

# Rest remains the same
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "-m", "gazpar2haws"]
```

#### 4.2 Update Dockerfile (if different from docker/Dockerfile)

Apply same changes to root `Dockerfile` if it exists.

#### 4.3 Update .dockerignore (if needed)

```
# Add src-specific ignores if needed
src/**/__pycache__
src/**/*.pyc
```

### Step 5: Update GitHub Actions (15 minutes)

#### 5.1 Update .github/workflows/ci.yaml

```yaml
# Find and update paths from:
poetry run black gazpar2haws
poetry run isort gazpar2haws
poetry run pylint gazpar2haws
poetry run flake8 gazpar2haws
poetry run ruff check gazpar2haws
poetry run mypy gazpar2haws

# To:
poetry run black src/gazpar2haws tests
poetry run isort src/gazpar2haws tests
poetry run pylint src/gazpar2haws
poetry run flake8 src/gazpar2haws
poetry run ruff check src/gazpar2haws
poetry run mypy src/gazpar2haws tests
```

Full example section:

```yaml
- name: Lint
  uses: ./.github/workflows/python-lint
  with:
    python-version: ${{ env.DEFAULT_PYTHON_VERSION }}
```

#### 5.2 Update .github/workflows/python-lint/action.yaml

```yaml
# Before
- name: Lint with black
  run: poetry run black --check gazpar2haws

- name: Lint with isort
  run: poetry run isort --check gazpar2haws

- name: Lint with pylint
  run: poetry run pylint gazpar2haws

- name: Lint with flake8
  run: poetry run flake8 gazpar2haws

- name: Lint with ruff
  run: poetry run ruff check gazpar2haws

- name: Type check with mypy
  run: poetry run mypy gazpar2haws

# After
- name: Lint with black
  run: poetry run black --check src/gazpar2haws tests

- name: Lint with isort
  run: poetry run isort --check src/gazpar2haws tests

- name: Lint with pylint
  run: poetry run pylint src/gazpar2haws

- name: Lint with flake8
  run: poetry run flake8 src/gazpar2haws

- name: Lint with ruff
  run: poetry run ruff check src/gazpar2haws

- name: Type check with mypy
  run: poetry run mypy src/gazpar2haws tests
```

#### 5.3 Update Other Workflows

Check and update paths in:
- `.github/workflows/create-release.yaml`
- `.github/workflows/publish-to-dockerhub.yaml`
- Any other custom workflows

### Step 6: Update Add-on Files (10 minutes)

#### 6.1 Update addons/gazpar2haws/run.sh

Check if run.sh has any hardcoded paths to `gazpar2haws/`:

```bash
# Before
python3 -m gazpar2haws --config config/configuration.yaml

# After (likely no change needed, but verify)
python3 -m gazpar2haws --config config/configuration.yaml
```

The module import should still work because the package is installed via pip/poetry.

#### 6.2 Verify Add-on Build Configuration

Check `addons/gazpar2haws/build.yaml` and `addons/gazpar2haws/Dockerfile`:

```dockerfile
# Should use the main Dockerfile which we already updated
# No changes needed if it references the root Dockerfile
```

### Step 7: Update Documentation (20 minutes)

#### 7.1 Update docs/DEVELOPER_GUIDE.md

Find and update directory structure sections:

```markdown
### Directory Layout

\`\`\`
gazpar2haws/
├── src/                   # Source code (NEW)
│   └── gazpar2haws/       # Package code
│       ├── __init__.py
│       ├── __main__.py        # Entry point
│       ├── bridge.py          # Orchestrator
│       ├── gazpar.py          # Business logic
│       ├── haws.py            # Home Assistant WebSocket client
│       ├── pricer.py          # Cost calculation
│       ├── configuration.py   # Configuration model
│       ├── config_utils.py    # Config loading utilities
│       ├── model.py           # Pydantic models
│       ├── date_array.py      # Date-indexed array
│       ├── datetime_utils.py  # Date/time utilities
│       └── version.py         # Version info
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
\`\`\`
```

Update "Making Changes" workflow:

```markdown
### Making Changes

Follow this workflow for feature development (using Gitflow):

1. **Ensure you have the latest develop branch**:
   \`\`\`bash
   git checkout develop
   git pull origin develop
   \`\`\`

2. **Create a feature branch from develop**:
   \`\`\`bash
   git checkout -b feature/123-my_feature
   \`\`\`

3. **Make your changes**:
   - Write code in `src/gazpar2haws/`
   - Add tests in `tests/`
   - Update documentation

4. **Run code quality checks**:
   \`\`\`bash
   # Format code
   poetry run black src/gazpar2haws tests
   poetry run isort src/gazpar2haws tests

   # Lint code
   poetry run pylint src/gazpar2haws
   poetry run flake8 src/gazpar2haws
   poetry run ruff check src/gazpar2haws

   # Type check
   poetry run mypy src/gazpar2haws tests
   \`\`\`
```

#### 7.2 Update README.md

Find and update any references to directory structure:

```markdown
### Project Structure

- `src/gazpar2haws/` - Source code
- `tests/` - Test suite
- `docs/` - Documentation
- `docker/` - Docker configuration
- `addons/` - Home Assistant add-on
```

#### 7.3 Add Migration Notice to CHANGELOG.md

```markdown
## [Unreleased]

### Changed
- **BREAKING (for contributors)**: Migrated to src layout structure
  - Source code moved from `gazpar2haws/` to `src/gazpar2haws/`
  - Contributors must run `poetry install` after pulling this change
  - No impact on end users or package imports
  - See docs/SRC_LAYOUT_MIGRATION.md for details
```

### Step 8: Re-install Package (5 minutes)

#### 8.1 Clean Previous Installation

```bash
# Remove old virtual environment
poetry env remove python

# Or manually delete
rm -rf .venv
```

#### 8.2 Re-install with New Structure

```bash
# Install package with new src layout
poetry install

# Verify installation
poetry run python -c "import gazpar2haws; print(gazpar2haws.__file__)"
# Should show: .../site-packages/gazpar2haws/__init__.py
```

#### 8.3 Verify Package Can Be Imported

```bash
poetry run python -c "
from gazpar2haws import __version__
from gazpar2haws.bridge import Bridge
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS
from gazpar2haws.pricer import Pricer
print('All imports successful!')
print(f'Version: {__version__}')
"
```

---

## File Changes Checklist

### Source Code
- [x] `mkdir src`
- [x] `git mv gazpar2haws src/`

### Configuration Files
- [x] `pyproject.toml` - Add packages path, update tool configs
- [x] `poetry.lock` - Will update automatically with `poetry install`

### Docker Files
- [x] `docker/Dockerfile` - Update COPY paths
- [x] `Dockerfile` (root, if exists) - Update COPY paths
- [x] `.dockerignore` - Update if needed

### GitHub Actions
- [x] `.github/workflows/ci.yaml` - Update lint/test paths
- [x] `.github/workflows/python-lint/action.yaml` - Update all tool paths
- [x] `.github/workflows/python-test/action.yaml` - Verify paths (likely no change)
- [x] `.github/workflows/create-release.yaml` - Verify build paths
- [x] `.github/workflows/publish-to-dockerhub.yaml` - Verify Docker build

### Add-on Files
- [x] `addons/gazpar2haws/run.sh` - Verify paths (likely no change)
- [x] `addons/gazpar2haws/Dockerfile` - Verify paths
- [x] `addons/gazpar2haws/build.yaml` - Verify paths

### Documentation
- [x] `docs/DEVELOPER_GUIDE.md` - Update directory structure, commands
- [x] `README.md` - Update structure references
- [x] `CHANGELOG.md` - Add migration notice
- [x] `docs/SRC_LAYOUT_MIGRATION.md` - This document

### IDE Configuration (if exists)
- [ ] `.vscode/settings.json` - Update paths if needed
- [ ] `.idea/` - Update PyCharm configs if needed

### Environment
- [x] `.venv/` - Delete and recreate with `poetry install`

---

## Testing Plan

### Phase 1: Local Testing (30 minutes)

#### 1.1 Installation Test

```bash
# Clean install
poetry env remove python
poetry install

# Verify installation
poetry run python -c "import gazpar2haws; print('OK')"
```

**Expected**: No errors, prints "OK"

#### 1.2 Unit Tests

```bash
# Run full test suite
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=gazpar2haws --cov-report=html
```

**Expected**: All tests pass, coverage report generates

#### 1.3 Linting Tests

```bash
# Black
poetry run black --check src/gazpar2haws tests
# Expected: All would be reformatted (or already formatted)

# isort
poetry run isort --check src/gazpar2haws tests
# Expected: No changes needed

# Pylint
poetry run pylint src/gazpar2haws
# Expected: No errors (warnings OK)

# Flake8
poetry run flake8 src/gazpar2haws
# Expected: No errors

# Ruff
poetry run ruff check src/gazpar2haws
# Expected: No errors

# Mypy
poetry run mypy src/gazpar2haws tests
# Expected: Success: no issues found
```

#### 1.4 Package Build Test

```bash
# Build wheel and source distribution
poetry build

# Check dist/ directory
ls -lh dist/
```

**Expected**:
- `gazpar2haws-0.5.0-py3-none-any.whl`
- `gazpar2haws-0.5.0.tar.gz`

#### 1.5 Package Installation Test

```bash
# Create clean venv
python -m venv test-venv
source test-venv/bin/activate  # On Windows: test-venv\Scripts\activate

# Install from wheel
pip install dist/gazpar2haws-0.5.0-py3-none-any.whl

# Test import
python -c "from gazpar2haws import __version__; print(__version__)"

# Cleanup
deactivate
rm -rf test-venv
```

**Expected**: Version prints correctly (0.5.0)

#### 1.6 Docker Build Test

```bash
# Build Docker image
cd docker
docker build -t gazpar2haws:test .

# Test image
docker run --rm gazpar2haws:test python -m gazpar2haws --help

# Cleanup
docker rmi gazpar2haws:test
cd ..
```

**Expected**: Help message displays correctly

#### 1.7 Application Run Test

```bash
# Run application with test config
poetry run python -m gazpar2haws --help
```

**Expected**: Help message displays

### Phase 2: CI/CD Testing (automated)

#### 2.1 Push to Feature Branch

```bash
git add .
git commit -m "refactor: migrate to src layout for better packaging"
git push origin refactor/migrate-to-src-layout
```

#### 2.2 Monitor GitHub Actions

1. Go to GitHub repository → Actions tab
2. Wait for CI workflow to complete
3. Verify all jobs pass:
   - ✅ Prepare
   - ✅ Lint
   - ✅ Test (Python 3.10, 3.11, 3.12, 3.13)

**Expected**: All CI checks pass

#### 2.3 Create Pull Request

```bash
# Via GitHub CLI
gh pr create --base develop \
  --title "refactor: migrate to src layout" \
  --body "Migrates project to src layout structure for better packaging.

## Changes
- Move source code to src/gazpar2haws/
- Update all configurations and workflows
- Update documentation

## Testing
- ✅ All unit tests pass
- ✅ All linters pass
- ✅ Docker builds successfully
- ✅ Package builds correctly
- ✅ CI/CD pipeline passes

See docs/SRC_LAYOUT_MIGRATION.md for details."
```

**Expected**: PR created, CI runs and passes

### Phase 3: Integration Testing (optional, 30 minutes)

#### 3.1 Test Add-on Build

```bash
# If you have HA test environment
# Test add-on installation
```

#### 3.2 Test End-to-End Workflow

```bash
# Test with real configuration
# (requires actual GrDF and HA credentials)
poetry run python -m gazpar2haws \
  --config tests/config/example_1.yaml \
  --secrets tests/config/secrets_test.yaml
```

**Expected**: Application runs without import errors

---

## Rollback Plan

If migration fails or causes issues:

### Option 1: Revert Git Changes

```bash
# Discard all changes
git reset --hard origin/develop

# Or revert to backup tag
git reset --hard pre-src-layout

# Force push if needed (only on feature branch!)
git push origin refactor/migrate-to-src-layout --force
```

### Option 2: Manual Rollback

```bash
# Move src/gazpar2haws back to root
git mv src/gazpar2haws .
rmdir src

# Revert pyproject.toml changes
git checkout HEAD -- pyproject.toml

# Re-install
poetry install

# Discard other changes
git checkout -- .github/ docker/ docs/
```

### Option 3: Create Rollback PR

If already merged to develop:

```bash
git checkout develop
git revert <migration-commit-sha>
git push origin develop
```

### Rollback Checklist

- [ ] Move source code back to root
- [ ] Revert pyproject.toml
- [ ] Revert all workflow files
- [ ] Revert Docker files
- [ ] Re-install package: `poetry install`
- [ ] Run tests: `poetry run pytest`
- [ ] Commit rollback changes

---

## Timeline

### Estimated Time: 2-3 hours

| Phase | Duration | Description |
|-------|----------|-------------|
| **Preparation** | 10 min | Create branch, backup state |
| **Move Source** | 5 min | Create src/, move gazpar2haws/ |
| **Update pyproject.toml** | 15 min | Update package path and tool configs |
| **Update Docker** | 10 min | Update Dockerfile paths |
| **Update GitHub Actions** | 15 min | Update workflow paths |
| **Update Add-on** | 10 min | Verify add-on configuration |
| **Update Documentation** | 20 min | Update guides and references |
| **Re-install** | 5 min | `poetry install` and verify |
| **Local Testing** | 30 min | Run all tests and linters |
| **CI/CD Testing** | 15 min | Push and monitor GitHub Actions |
| **PR Review** | 30 min | Create PR, request reviews |
| **Buffer** | 30 min | Handle unexpected issues |

**Total**: ~2.5 hours

### Recommended Schedule

**Day 1 (60 minutes)**:
1. Preparation and code move
2. Update pyproject.toml
3. Local testing

**Day 2 (90 minutes)**:
1. Update Docker and workflows
2. Update documentation
3. CI/CD testing
4. Create PR

---

## Post-Migration

### Communication

#### 1. Update Contributors

**Announcement in PR**:
```markdown
## ⚠️ Important for Contributors

This PR migrates the project to a src layout structure.

**Action Required**:
After pulling this change, run:
\`\`\`bash
poetry install
\`\`\`

**What Changed**:
- Source code moved from `gazpar2haws/` to `src/gazpar2haws/`
- All imports remain the same: `from gazpar2haws import ...`
- IDE might need to re-index
```

#### 2. Update Issues/Discussions

Post in GitHub Discussions:
```markdown
# 📢 Project Structure Update

We've migrated to a src layout structure for better packaging.

## For Contributors
- Source code is now in `src/gazpar2haws/`
- Run `poetry install` after pulling changes
- Update IDE project settings if needed

## For Users
- No changes to package usage
- Imports remain the same
- No action required

See docs/SRC_LAYOUT_MIGRATION.md for details.
```

### Documentation Updates

#### 1. Update Contributor Guide

Add to docs/DEVELOPER_GUIDE.md:

```markdown
### Project Structure Notes

This project uses the **src layout** structure:
- Source code: `src/gazpar2haws/`
- Tests: `tests/`
- Documentation: `docs/`

**Benefits**:
- Better isolation of source code
- Forces proper package installation
- Industry best practice
- Prevents accidental imports

**For New Contributors**:
After cloning, always run:
\`\`\`bash
poetry install
\`\`\`

This installs the package in editable mode.
```

#### 2. Add to README

```markdown
## Development Setup

\`\`\`bash
# Clone repository
git clone https://github.com/ssenart/gazpar2haws.git
cd gazpar2haws

# Install dependencies (installs from src/)
poetry install

# Verify installation
poetry run python -c "import gazpar2haws; print(gazpar2haws.__version__)"
\`\`\`
```

### Monitoring

#### 1. Watch for Issues

Monitor for 1-2 weeks after merge:
- GitHub Issues for migration-related problems
- CI/CD failures
- Contributor questions

#### 2. Be Ready to Rollback

Keep rollback instructions handy for first week.

#### 3. Track Metrics

- CI/CD success rate
- Test coverage (should remain same)
- Build times (should be similar)
- Package size (should be same)

### Cleanup

#### 1. Delete Backup Tag

After 2 weeks of stable operation:

```bash
git tag -d pre-src-layout
git push origin :refs/tags/pre-src-layout
```

#### 2. Archive Migration Document

After successful migration and cleanup:

```bash
# Move to archive
mkdir docs/archive
git mv docs/SRC_LAYOUT_MIGRATION.md docs/archive/

# Or add note at top
echo "✅ This migration was completed on YYYY-MM-DD" | cat - docs/SRC_LAYOUT_MIGRATION.md > temp && mv temp docs/SRC_LAYOUT_MIGRATION.md
```

---

## Troubleshooting

### Common Issues

#### Issue: ModuleNotFoundError after migration

**Symptom**:
```
ModuleNotFoundError: No module named 'gazpar2haws'
```

**Solution**:
```bash
poetry install
```

#### Issue: Tests can't find package

**Symptom**:
```
ImportError: cannot import name 'Bridge' from 'gazpar2haws'
```

**Solution**:
Check `pyproject.toml` has correct configuration:
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]

[tool.poetry]
packages = [{include = "gazpar2haws", from = "src"}]
```

#### Issue: Docker build fails

**Symptom**:
```
COPY failed: file not found in build context
```

**Solution**:
Update Dockerfile COPY paths:
```dockerfile
COPY src /app/src
```

#### Issue: GitHub Actions lint fails

**Symptom**:
```
Error: No such file or directory: gazpar2haws
```

**Solution**:
Update workflow paths:
```yaml
run: poetry run pylint src/gazpar2haws
```

#### Issue: IDE can't find imports

**Symptom**:
Red squiggly lines under imports in IDE

**Solution**:
1. Reload IDE window
2. Mark `src` as sources root
3. Re-run `poetry install`

#### Issue: Coverage report empty

**Symptom**:
Coverage report shows 0%

**Solution**:
Update `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["src"]
```

---

## References

- [Python Packaging: src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Hynek Schlawack: Testing & Packaging](https://hynek.me/articles/testing-packaging/)
- [Poetry: Project Setup](https://python-poetry.org/docs/basic-usage/#project-setup)
- [Ionel Cristian Mărieș: Packaging a Python library](https://blog.ionelmc.ro/2014/05/25/python-packaging/)

---

## Success Criteria

Migration is considered successful when:

- [x] All source code in `src/gazpar2haws/`
- [x] `poetry install` works without errors
- [x] All tests pass (`poetry run pytest`)
- [x] All linters pass (black, isort, pylint, flake8, ruff, mypy)
- [x] Package builds (`poetry build`)
- [x] Docker image builds successfully
- [x] CI/CD pipeline passes on GitHub Actions
- [x] Documentation updated
- [x] Add-on still works
- [x] No import errors in application
- [x] Coverage report generates correctly

---

**Migration Lead**: Development Team
**Document Version**: 1.0
**Last Updated**: 2026-01-31
**Status**: Ready for Execution
