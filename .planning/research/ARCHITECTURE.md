# Architecture Research: v1.1 Polish

**Domain:** Python CLI Packaging for PyPI
**Researched:** 2026-01-18
**Confidence:** HIGH (well-established Python packaging patterns)

## Executive Summary

For v1.1, gitsl needs to transition from a flat collection of Python files to a proper installable package. The recommended approach uses **src layout** with **setuptools** as the build backend. This structure enables `pip install gitsl` to create the `gitsl` command via console script entry points, while maintaining backward compatibility with the existing module organization.

---

## Package Layout

### Recommended Directory Structure

Transform the current flat layout into a src layout package:

```
gitsl/
├── pyproject.toml          # Package metadata and build config
├── README.md               # Package description for PyPI
├── LICENSE                 # License file
├── pytest.ini              # Test configuration (unchanged)
├── src/
│   └── gitsl/              # Main package
│       ├── __init__.py     # Package initialization, exports VERSION
│       ├── __main__.py     # Enable `python -m gitsl`
│       ├── cli.py          # Main entry point (from gitsl.py)
│       ├── common.py       # Shared utilities
│       ├── cmd_status.py   # Command handlers
│       ├── cmd_log.py
│       ├── cmd_diff.py
│       ├── cmd_init.py
│       ├── cmd_rev_parse.py
│       ├── cmd_add.py
│       └── cmd_commit.py
└── tests/
    ├── __init__.py
    ├── conftest.py         # Fixtures
    ├── helpers/
    │   ├── __init__.py
    │   ├── commands.py
    │   └── comparison.py
    ├── test_cmd_status.py  # Renamed from test_status_porcelain.py
    ├── test_cmd_log.py
    ├── test_cmd_diff.py
    ├── test_cmd_init.py
    ├── test_cmd_rev_parse.py
    ├── test_cmd_add.py
    ├── test_cmd_commit.py
    └── test_unsupported.py
```

### Why src Layout

**Benefits over flat layout:**

1. **Prevents accidental imports** - Cannot accidentally import uninstalled code
2. **Enforces proper installation** - Tests run against installed package, catching packaging errors
3. **Clear separation** - Source code isolated from project metadata

**Source:** [Python Packaging User Guide - src layout vs flat layout](https://daobook.github.io/packaging.python.org/discussions/src-layout-vs-flat-layout.html)

### Migration from Current Structure

| Current Location | New Location |
|-----------------|--------------|
| `gitsl.py` | `src/gitsl/cli.py` |
| `common.py` | `src/gitsl/common.py` |
| `cmd_*.py` | `src/gitsl/cmd_*.py` |
| `tests/` | `tests/` (unchanged) |

---

## Entry Points

### Console Script Configuration

The `gitsl` command is installed via entry points in `pyproject.toml`:

```toml
[project.scripts]
gitsl = "gitsl.cli:main"
```

When users run `pip install gitsl`, this creates a `gitsl` executable that calls the `main()` function from `gitsl.cli` module.

### Supporting `python -m gitsl`

Create `src/gitsl/__main__.py`:

```python
"""Enable running gitsl as a module: python -m gitsl"""
from gitsl.cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
```

### Package Initialization

Create `src/gitsl/__init__.py`:

```python
"""gitsl - Git to Sapling CLI shim."""
from gitsl.common import VERSION

__version__ = VERSION
__all__ = ["VERSION", "__version__"]
```

---

## pyproject.toml Configuration

### Complete Configuration

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "gitsl"
version = "1.1.0"
description = "Git to Sapling CLI translation shim"
readme = "README.md"
license = "MIT"
requires-python = ">=3.9"
authors = [
    {name = "Your Name", email = "your@email.com"}
]
keywords = ["git", "sapling", "vcs", "cli", "shim"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Version Control",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]

[project.scripts]
gitsl = "gitsl.cli:main"

[project.urls]
Homepage = "https://github.com/youruser/gitsl"
Repository = "https://github.com/youruser/gitsl"
Issues = "https://github.com/youruser/gitsl/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Key Configuration Points

| Section | Purpose |
|---------|---------|
| `[build-system]` | Declares setuptools as build backend |
| `[project]` | Standard metadata (name, version, description) |
| `[project.scripts]` | Creates `gitsl` CLI command |
| `[tool.setuptools.packages.find]` | Tells setuptools to find packages in `src/` |
| `[tool.pytest.ini_options]` | Configures pytest to find src and tests |

**Source:** [Python Packaging User Guide - Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

---

## Test Organization

### Command-Specific Test Pattern

Tests are already organized by command. Maintain this pattern:

```
tests/
├── test_cmd_status.py      # All status command tests
├── test_cmd_log.py         # All log command tests
├── test_cmd_diff.py        # All diff command tests
└── ...
```

### Running Tests for Specific Commands

With pytest, filter by command using `-k`:

```bash
# Run all status tests
pytest -k status

# Run all log tests
pytest -k log

# Run specific test class
pytest -k "TestLogOneline"

# Run tests matching pattern
pytest -k "test_cmd_log and oneline"
```

### Wrapper Script for `./test <command>`

Create a test runner script for the `./test <command>` pattern:

```bash
#!/bin/bash
# test - Run tests for a specific command or all tests

if [ -z "$1" ]; then
    # No argument - run all tests
    pytest tests/ -v
else
    # Filter by command name
    pytest tests/ -k "$1" -v
fi
```

Usage:
```bash
./test              # All tests
./test status       # Status command tests
./test log          # Log command tests
./test "log and oneline"  # More specific filter
```

### Test Discovery After Restructure

Update `pytest.ini` or use `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Important:** With src layout, you must either:
1. Install the package in editable mode: `pip install -e .`
2. OR configure `pythonpath` in pytest config

**Source:** [Pytest with Eric - Organizing Tests](https://pytest-with-eric.com/pytest-best-practices/pytest-organize-tests/)

---

## CI Workflow Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Sapling
        run: |
          # Install Sapling for E2E tests
          # Note: Sapling may need specific installation steps
          # This is a placeholder - verify actual installation method
          echo "Sapling installation step"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest -v --tb=short

      - name: Run linter
        run: ruff check src/ tests/
```

### Key CI Considerations

1. **Sapling Dependency** - E2E tests require Sapling (`sl`). CI needs to install it.
2. **Editable Install** - Use `pip install -e .` so tests run against the actual package.
3. **Matrix Testing** - Test across Python 3.9-3.12 for compatibility.
4. **Linting** - Add ruff for code quality checks.

**Source:** [Pytest with Eric - GitHub Actions Integration](https://pytest-with-eric.com/integrations/pytest-github-actions/)

---

## Build Order

### Phase 1: Package Restructure

**Goal:** Reorganize files into src layout.

**Steps:**
1. Create `src/gitsl/` directory structure
2. Move source files with updated imports
3. Create `__init__.py` and `__main__.py`
4. Update all internal imports (e.g., `from common import` -> `from gitsl.common import`)

**Dependencies:** None

### Phase 2: pyproject.toml

**Goal:** Create package configuration.

**Steps:**
1. Create `pyproject.toml` with metadata
2. Configure entry points for `gitsl` command
3. Configure setuptools package discovery
4. Merge pytest.ini into pyproject.toml (optional)

**Dependencies:** Phase 1 complete

### Phase 3: Test Updates

**Goal:** Tests work with new structure.

**Steps:**
1. Update conftest.py to use installed package
2. Update imports in test files
3. Verify `pytest -k <command>` filtering works
4. Create `./test` convenience script

**Dependencies:** Phase 2 complete (need editable install)

### Phase 4: CI Integration

**Goal:** Automated testing on push.

**Steps:**
1. Create `.github/workflows/test.yml`
2. Configure Sapling installation in CI
3. Add linting step
4. Test matrix across Python versions

**Dependencies:** Phase 3 complete (tests must pass)

### Phase 5: PyPI Publishing (Optional)

**Goal:** Package available via `pip install gitsl`.

**Steps:**
1. Create PyPI account and API token
2. Add publish workflow to GitHub Actions
3. Configure trusted publisher (recommended)
4. Create first release

**Dependencies:** Phase 4 complete

### Dependency Graph

```
Phase 1: Package Restructure
    │
    v
Phase 2: pyproject.toml
    │
    v
Phase 3: Test Updates
    │
    v
Phase 4: CI Integration
    │
    v
Phase 5: PyPI Publishing (optional)
```

---

## Import Updates Required

### Before (Flat Layout)

```python
# In gitsl.py
from common import parse_argv, is_debug_mode, print_debug_info, VERSION
import cmd_status
import cmd_log
...

# In cmd_status.py
from common import ParsedCommand, run_sl
```

### After (src Layout)

```python
# In src/gitsl/cli.py
from gitsl.common import parse_argv, is_debug_mode, print_debug_info, VERSION
from gitsl import cmd_status
from gitsl import cmd_log
...

# In src/gitsl/cmd_status.py
from gitsl.common import ParsedCommand, run_sl
```

### Automated Migration

Consider using `rope` or manual find-replace:

```bash
# Find all imports to update
grep -r "from common import" --include="*.py"
grep -r "import cmd_" --include="*.py"
```

---

## Pitfalls to Avoid

### 1. Forgetting Editable Install

**Problem:** Tests fail with `ModuleNotFoundError: No module named 'gitsl'`

**Solution:** Always run `pip install -e .` after restructure before testing.

### 2. Circular Import with __init__.py

**Problem:** Importing VERSION in `__init__.py` from common.py may cause issues if common.py imports from other modules.

**Solution:** Keep `__init__.py` minimal. Only import what is truly needed for public API.

### 3. Test Import Path Confusion

**Problem:** Tests import wrong version (local vs installed).

**Solution:** src layout prevents this by design - you MUST install to import.

### 4. Missing __init__.py Files

**Problem:** Package not discoverable.

**Solution:** Ensure `__init__.py` exists in:
- `src/gitsl/__init__.py`
- `tests/__init__.py`
- `tests/helpers/__init__.py`

---

## Sources

### Primary (HIGH Confidence)
- [Python Packaging User Guide - Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python Packaging User Guide - src layout vs flat layout](https://daobook.github.io/packaging.python.org/discussions/src-layout-vs-flat-layout.html)
- [Xebia - Updated Guide to Setuptools and Pyproject.toml](https://xebia.com/blog/an-updated-guide-to-setuptools-and-pyproject-toml/)

### Secondary (MEDIUM Confidence)
- [Pytest with Eric - GitHub Actions Integration](https://pytest-with-eric.com/integrations/pytest-github-actions/)
- [Pytest with Eric - Organizing Tests](https://pytest-with-eric.com/pytest-best-practices/pytest-organize-tests/)
- [pyOpenSci - pyproject.toml Tutorial](https://www.pyopensci.org/python-package-guide/tutorials/pyproject-toml.html)
- [Real Python - Managing Python Projects with pyproject.toml](https://realpython.com/python-pyproject-toml/)
