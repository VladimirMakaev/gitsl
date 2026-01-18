# Stack Research: v1.1 Polish

**Project:** gitsl - Git to Sapling CLI shim
**Researched:** 2025-01-18
**Scope:** PyPI publishing, cross-platform CI, test runner patterns
**Confidence:** HIGH (verified with official documentation)

---

## PyPI Publishing

### Recommendation: pyproject.toml with setuptools

**Use pyproject.toml** - This is the modern standard. The Python Packaging Authority explicitly recommends migrating from setup.py to pyproject.toml.

**Build backend:** setuptools (standard, no extra dependencies)

### pyproject.toml Configuration

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "gitsl"
dynamic = ["version"]
description = "Git to Sapling CLI shim - translates git commands to sl equivalents"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["git", "sapling", "scm", "cli", "shim"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Version Control",
    "Topic :: Software Development :: Version Control :: Git",
]

[project.scripts]
gitsl = "gitsl:main"

[project.urls]
Homepage = "https://github.com/yourusername/gitsl"
Repository = "https://github.com/yourusername/gitsl"
Issues = "https://github.com/yourusername/gitsl/issues"

[tool.setuptools]
py-modules = ["gitsl", "common", "cmd_status", "cmd_log", "cmd_diff", "cmd_init", "cmd_rev_parse", "cmd_add", "cmd_commit"]

[tool.setuptools.dynamic]
version = {attr = "common.VERSION"}
```

### Entry Point Configuration

The `[project.scripts]` section defines CLI entry points:

```toml
[project.scripts]
gitsl = "gitsl:main"
```

This creates an executable `gitsl` command that calls `main()` from `gitsl.py`.

**Key insight:** Because gitsl uses a flat module layout (not a package directory), you must explicitly list modules in `[tool.setuptools].py-modules`. Setuptools auto-discovery works best with package directories.

### Version Management Strategy

**Recommended:** Keep version in `common.py` (single source of truth) and use dynamic version reading.

```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "common.VERSION"}
```

This reads the version from `common.VERSION` at build time, ensuring the installed package and runtime code report the same version.

The current project already has `VERSION = "0.1.0"` in `common.py`, so this pattern works without changes.

### Build and Upload Commands

```bash
# Build distribution
python -m pip install build
python -m build

# Upload to TestPyPI (for testing)
python -m pip install twine
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

---

## GitHub Actions CI

### Workflow Structure

Create two workflows:
- `.github/workflows/ci.yml` - Testing on push/PR
- `.github/workflows/publish.yml` - PyPI publishing on release

### CI Workflow: Test Matrix

```yaml
name: CI

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }} on ${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
        exclude:
          # Reduce matrix size - Windows builds are slow
          - os: windows-latest
            python-version: "3.8"
          - os: windows-latest
            python-version: "3.9"

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Sapling (Ubuntu)
        if: runner.os == 'Linux'
        run: |
          curl -LO https://github.com/facebook/sapling/releases/latest/download/sapling_0.2.20240718-145624+f4e9df48_amd64.Ubuntu22.04.deb
          sudo dpkg -i *.deb || sudo apt-get install -f -y

      - name: Install Sapling (macOS)
        if: runner.os == 'macOS'
        run: brew install sapling

      - name: Install Sapling (Windows)
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          $release = Invoke-RestMethod -Uri "https://api.github.com/repos/facebook/sapling/releases/latest"
          $asset = $release.assets | Where-Object { $_.name -like "*windows*.zip" }
          Invoke-WebRequest -Uri $asset.browser_download_url -OutFile sapling.zip
          Expand-Archive -Path sapling.zip -DestinationPath $env:USERPROFILE\sapling
          echo "$env:USERPROFILE\sapling" | Out-File -FilePath $env:GITHUB_PATH -Append

      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install pytest

      - name: Run tests
        run: pytest tests/ -v

      - name: Verify CLI entry point
        run: python gitsl.py --version
```

### Sapling Installation Notes

| Platform | Method | Notes |
|----------|--------|-------|
| macOS | `brew install sapling` | Straightforward, ~30 seconds |
| Linux (Ubuntu) | Download .deb from releases | ~15 seconds, needs version pinning |
| Windows | Download ZIP from releases | Requires PATH manipulation |

**Alternative for Linux using Homebrew:**
```yaml
- name: Install Sapling (Ubuntu via Homebrew)
  if: runner.os == 'Linux'
  run: |
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install sapling
    echo "/home/linuxbrew/.linuxbrew/bin" >> $GITHUB_PATH
```

This adds ~2-3 minutes but keeps installation consistent across platforms.

### Publish Workflow: Trusted Publishing

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Install build tools
        run: python -m pip install build

      - name: Build package
        run: python -m build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-pypi:
    name: Publish to PyPI
    needs: [build]
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/gitsl
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

**Trusted Publishing:** Configure at PyPI.org under project settings. This eliminates API tokens - GitHub Actions authenticates via OIDC.

**Setup steps for Trusted Publishing:**
1. Create account on pypi.org
2. Create project or reserve name
3. Go to project settings > Publishing
4. Add GitHub Actions as trusted publisher (owner, repo, workflow filename)

---

## Test Runner

### Current Pattern

The project already uses pytest with a good structure:
- `pytest.ini` configures test paths
- `tests/conftest.py` provides fixtures for git/sl repos
- `tests/helpers/` contains shared test utilities

### Wrapper Script Pattern

Create `./test` script for convenience:

```bash
#!/bin/bash
# ./test - Run gitsl tests
#
# Usage:
#   ./test              Run all tests
#   ./test status       Run tests for cmd_status
#   ./test log diff     Run tests for cmd_log and cmd_diff
#   ./test -v           Pass flags to pytest

set -e

# Change to script directory
cd "$(dirname "$0")"

if [ $# -eq 0 ]; then
    # No arguments - run all tests
    python -m pytest tests/ -v
elif [[ "$1" == -* ]]; then
    # Flags passed directly to pytest
    python -m pytest tests/ "$@"
else
    # Command names - map to test files
    TEST_FILES=()
    for cmd in "$@"; do
        if [[ "$cmd" == -* ]]; then
            # It's a flag, pass through
            TEST_FILES+=("$cmd")
        elif [ -f "tests/test_cmd_$cmd.py" ]; then
            TEST_FILES+=("tests/test_cmd_$cmd.py")
        elif [ -f "tests/test_$cmd.py" ]; then
            TEST_FILES+=("tests/test_$cmd.py")
        else
            echo "Warning: No test file found for '$cmd'"
        fi
    done

    if [ ${#TEST_FILES[@]} -gt 0 ]; then
        python -m pytest "${TEST_FILES[@]}" -v
    else
        echo "No matching test files found"
        exit 1
    fi
fi
```

**Usage:**
- `./test` - Run all tests
- `./test status` - Run `tests/test_cmd_status.py`
- `./test log diff` - Run tests for both commands
- `./test -k "porcelain"` - Pass pytest filters

### pytest Configuration Update

Consider updating `pytest.ini` for better defaults:

```ini
[pytest]
pythonpath = .
testpaths = tests
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

Current `pytest.ini` is minimal but functional:
```ini
[pytest]
pythonpath = tests
testpaths = tests
```

---

## Recommendations Summary

### PyPI Publishing

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Config format | pyproject.toml | Modern standard, setup.py deprecated |
| Build backend | setuptools | No extra deps, stdlib-only project |
| Entry point | `[project.scripts]` | Creates `gitsl` command |
| Module listing | Explicit `py-modules` | Flat layout requires explicit list |
| Version source | `common.VERSION` via dynamic | Single source of truth, already exists |

### GitHub Actions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python versions | 3.8-3.13 | Match `requires-python = ">=3.8"` |
| OS matrix | ubuntu, macos, windows | Full cross-platform coverage |
| Sapling install (mac) | Homebrew | Official, fast |
| Sapling install (linux) | .deb package | Faster than Homebrew on Linux |
| Sapling install (windows) | ZIP from releases | Official distribution |
| Publishing trigger | GitHub Release | Clean separation of CI and release |
| Auth method | Trusted Publishing (OIDC) | No secrets to manage |

### Test Runner

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | pytest (existing) | Already in use, good fixture pattern |
| Wrapper script | `./test` shell script | Convenient command-specific testing |
| CI integration | `pytest tests/ -v` | Simple, reliable |

---

## Required Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `pyproject.toml` | Package configuration | Required for PyPI |
| `.github/workflows/ci.yml` | Test matrix on push/PR | Required for CI |
| `.github/workflows/publish.yml` | PyPI publishing on release | Required for PyPI |
| `./test` (executable) | Test runner wrapper | Nice to have |
| `README.md` | Required by pyproject.toml | Required for PyPI |
| `LICENSE` | Required for PyPI | Required for PyPI |

---

## Roadmap Implications

Based on this research, v1.1 phases should include:

1. **Packaging Phase** - Create pyproject.toml, verify `pip install -e .` works, test entry point
2. **CI Phase** - Create GitHub Actions workflows, verify Sapling installation works on all platforms
3. **Documentation Phase** - Create README.md with installation and usage instructions
4. **Release Phase** - Configure PyPI trusted publishing, create first release

**Key dependency:** README.md must exist before pyproject.toml can use `readme = "README.md"`.

---

## Sources

- [Python Packaging User Guide - Modernize setup.py](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/)
- [Setuptools pyproject.toml Configuration](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
- [GitHub Docs - Building and Testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
- [PyPI Publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Sapling Installation Guide](https://sapling-scm.com/docs/introduction/installation)
- [GitHub Actions Matrix Strategy](https://codefresh.io/learn/github-actions/github-actions-matrix/)
- [Xebia - Setuptools and pyproject.toml Guide](https://xebia.com/blog/an-updated-guide-to-setuptools-and-pyproject-toml/)
