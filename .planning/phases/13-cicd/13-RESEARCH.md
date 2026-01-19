# Phase 13: CI/CD - Research

**Researched:** 2026-01-19
**Domain:** GitHub Actions, PyPI Trusted Publishing, Cross-Platform CI
**Confidence:** HIGH

## Summary

This phase implements automated testing and release automation using GitHub Actions. The project requires two separate workflows: a test workflow that runs on push/PR across MacOS, Linux, and Windows, and a release workflow that publishes to PyPI on version tags using trusted publishing (OIDC, no API tokens).

The primary challenge is installing Sapling on each CI platform since Sapling is required for tests but has different installation methods per OS. GitHub Actions provides a mature matrix strategy for cross-platform testing, and PyPA's official `pypi-publish` action handles trusted publishing seamlessly.

**Primary recommendation:** Create two workflow files - `ci.yml` for testing (triggered on push/PR) and `release.yml` for PyPI publishing (triggered on version tags). Use platform-specific installation steps for Sapling.

## Standard Stack

The established tools for Python CI/CD on GitHub Actions:

### Core Actions
| Action | Version | Purpose | Why Standard |
|--------|---------|---------|--------------|
| `actions/checkout` | v4 | Clone repository | Official GitHub action |
| `actions/setup-python` | v5 | Configure Python version | Official, supports matrix |
| `pypa/gh-action-pypi-publish` | release/v1 | Publish to PyPI | Official PyPA action, trusted publishing support |

### Build Tools
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `build` (pypa) | Latest | Build sdist and wheel | For creating distribution packages |
| `pytest` | Installed by ./test | Run tests | Already configured in project |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pypa/gh-action-pypi-publish | twine + OIDC manual | More complexity, same result |
| Platform-specific Sapling install | Docker with Sapling | Slower, more complex, but more reproducible |

**Note:** The project already has a `./test` script that handles venv creation and pytest installation, so CI can use this directly.

## Architecture Patterns

### Recommended Workflow Structure
```
.github/
  workflows/
    ci.yml            # Test workflow (push, PR)
    release.yml       # Release workflow (tags)
```

### Pattern 1: Matrix Strategy for Cross-Platform Testing
**What:** Run tests across multiple OS and Python versions in parallel
**When to use:** Always for cross-platform Python projects
**Example:**
```yaml
# Source: GitHub Docs - Building and testing Python
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
  fail-fast: false  # Continue other jobs if one fails

runs-on: ${{ matrix.os }}

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

### Pattern 2: Platform-Specific Steps with Conditionals
**What:** Use `if` conditionals to run different commands per OS
**When to use:** When installation steps differ by platform (like Sapling)
**Example:**
```yaml
# Source: GitHub Actions documentation
- name: Install Sapling (Ubuntu)
  if: runner.os == 'Linux'
  run: |
    curl -LO https://github.com/facebook/sapling/releases/download/...
    sudo dpkg -i sapling_*.deb

- name: Install Sapling (macOS)
  if: runner.os == 'macOS'
  run: brew install sapling

- name: Install Sapling (Windows)
  if: runner.os == 'Windows'
  shell: pwsh
  run: |
    # Download and extract Sapling
    # Remove PowerShell sl alias
    Remove-Alias -Name sl -Force -Scope Global -ErrorAction SilentlyContinue
```

### Pattern 3: Trusted Publishing Workflow
**What:** Use OIDC tokens for PyPI publishing without API keys
**When to use:** For all PyPI publishing to avoid storing secrets
**Example:**
```yaml
# Source: PyPI Docs - Trusted Publishers
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi  # Must match PyPI configuration
    permissions:
      id-token: write  # MANDATORY for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### Pattern 4: Tag-Triggered Release
**What:** Only publish to PyPI when version tags are pushed
**When to use:** For production releases
**Example:**
```yaml
# Source: GitHub Docs - Triggering workflows
on:
  push:
    tags:
      - 'v*'  # Matches v1.0.0, v2.0.0-beta, etc.
```

### Anti-Patterns to Avoid
- **Storing PyPI API tokens in secrets:** Use trusted publishing instead
- **Running release on every push:** Use tag filtering
- **Installing dependencies globally:** Use virtual environments
- **Ignoring matrix failures:** Use `fail-fast: false` to see all failures

## Don't Hand-Roll

Problems that have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Python version management | Shell scripts to install Python | `actions/setup-python` | Handles caching, multiple versions |
| PyPI authentication | Manual OIDC token exchange | `pypa/gh-action-pypi-publish` | Abstracts OIDC complexity |
| Package building | Custom build scripts | `python -m build` | Standard, handles isolation |
| Repository checkout | Git commands | `actions/checkout` | Handles tokens, submodules |

**Key insight:** GitHub Actions has mature, official actions for Python CI/CD. The only custom work needed is Sapling installation since it's not a standard package.

## Common Pitfalls

### Pitfall 1: Windows PowerShell `sl` Alias Conflict
**What goes wrong:** `sl` is a PowerShell alias for `Set-Location`, masking the Sapling command
**Why it happens:** PowerShell has built-in aliases that shadow external commands
**How to avoid:** Remove the alias before running tests
```powershell
Remove-Alias -Name sl -Force -Scope Global -ErrorAction SilentlyContinue
```
**Warning signs:** Tests work locally but fail on Windows CI with "Set-Location" errors

### Pitfall 2: Sapling Version Pinning
**What goes wrong:** Tests break when Sapling releases new version with different behavior
**Why it happens:** Using `latest` release or unpinned versions
**How to avoid:** Pin to a specific Sapling release version in CI
**Warning signs:** Intermittent CI failures after no code changes

### Pitfall 3: Missing id-token Permission
**What goes wrong:** PyPI publish fails with authentication error
**Why it happens:** Trusted publishing requires explicit `id-token: write` permission
**How to avoid:** Always specify the permission in the job
```yaml
permissions:
  id-token: write
```
**Warning signs:** Error message about OIDC token or authentication failure

### Pitfall 4: PyPI Environment Not Configured
**What goes wrong:** Trusted publishing fails with "trusted publisher not found"
**Why it happens:** PyPI project hasn't been configured to trust the GitHub workflow
**How to avoid:** Configure trusted publisher on PyPI before first release
**Warning signs:** Error about no matching trusted publisher

### Pitfall 5: Tag Pattern Too Broad
**What goes wrong:** Accidental releases from test tags or non-version tags
**Why it happens:** Using `tags: '*'` instead of `tags: 'v*'`
**How to avoid:** Use specific tag patterns like `'v*'` or `'v[0-9]*'`
**Warning signs:** Unexpected PyPI publishes

## Code Examples

Verified patterns from official sources:

### CI Workflow Structure
```yaml
# Source: GitHub Docs - Building and testing Python
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      # Platform-specific Sapling installation here

      - name: Run tests
        run: python test  # Use the project's test script
```

### Release Workflow Structure
```yaml
# Source: PyPI Docs - Using a Publisher
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build package
        run: |
          pip install build
          python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### Sapling Installation (Ubuntu)
```yaml
# Source: Sapling Installation Docs + GitHub API
- name: Install Sapling (Ubuntu)
  if: runner.os == 'Linux'
  run: |
    SAPLING_VERSION="0.2.20250521-115337+25ed6ac4"
    curl -LO "https://github.com/facebook/sapling/releases/download/${SAPLING_VERSION}/sapling_${SAPLING_VERSION}_amd64.Ubuntu22.04.deb"
    sudo dpkg -i sapling_*.deb
    sl --version
```

### Sapling Installation (macOS)
```yaml
# Source: Sapling Installation Docs
- name: Install Sapling (macOS)
  if: runner.os == 'macOS'
  run: |
    brew install sapling
    sl --version
```

### Sapling Installation (Windows)
```yaml
# Source: Sapling Installation Docs + PowerShell Remove-Alias docs
- name: Install Sapling (Windows)
  if: runner.os == 'Windows'
  shell: pwsh
  run: |
    $SAPLING_VERSION = "0.2.20250521-115337+25ed6ac4"
    $url = "https://github.com/facebook/sapling/releases/download/$SAPLING_VERSION/sapling_windows_${SAPLING_VERSION}_amd64.zip"
    Invoke-WebRequest -Uri $url -OutFile sapling.zip
    Expand-Archive sapling.zip -DestinationPath "$env:LOCALAPPDATA\Sapling"
    $env:PATH = "$env:LOCALAPPDATA\Sapling\sapling_windows_${SAPLING_VERSION}_amd64;$env:PATH"
    [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")

    # Remove PowerShell sl alias that conflicts with Sapling
    Remove-Alias -Name sl -Force -Scope Global -ErrorAction SilentlyContinue

    sl.exe --version
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| PyPI API tokens in secrets | Trusted Publishing (OIDC) | 2023 | No secrets to manage, more secure |
| `setup-python@v3` | `setup-python@v5` | 2024 | Better caching, arm64 support |
| `upload-artifact@v3` | `upload-artifact@v4` | 2024 | Improved performance |
| Manual twine upload | `pypa/gh-action-pypi-publish` | 2023 | Handles OIDC transparently |

**Deprecated/outdated:**
- API token authentication: Still works but trusted publishing is preferred
- `setup-python@v3`: Still works but v5 has better features
- TestPyPI for testing: Still useful for validation before production

## Open Questions

Things that couldn't be fully resolved:

1. **Sapling ARM64 for macOS Runners**
   - What we know: macOS runners may be ARM64 (M1/M2)
   - What's unclear: Homebrew should handle this, but worth validating
   - Recommendation: Test on `macos-latest` and verify Sapling installs correctly

2. **Windows Sapling PATH Persistence**
   - What we know: PATH changes in one step may not persist to next
   - What's unclear: Whether `GITHUB_PATH` is needed instead of setx
   - Recommendation: Use `echo "path" >> $env:GITHUB_PATH` for reliability

3. **Python Version Matrix Scope**
   - What we know: Project supports Python 3.8+
   - What's unclear: How many versions to test (3.8-3.13 = 6 versions)
   - Recommendation: Test 3.9, 3.11, 3.13 (oldest active, middle, latest)

## Sources

### Primary (HIGH confidence)
- [GitHub Docs - Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) - Matrix strategy, pytest examples
- [PyPI Docs - Using a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/) - OIDC configuration, workflow requirements
- [PyPA Packaging Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - Complete workflow examples
- [actions/setup-python](https://github.com/actions/setup-python) - Python version configuration, caching
- [Sapling Installation Docs](https://sapling-scm.com/docs/introduction/installation/) - Platform-specific installation
- [GitHub API - Sapling Releases](https://api.github.com/repos/facebook/sapling/releases/latest) - Asset URLs, version info

### Secondary (MEDIUM confidence)
- [GitHub Docs - Triggering Workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) - Tag triggers
- [Microsoft Learn - Remove-Alias](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/remove-alias) - PowerShell alias removal
- [pypa/build](https://github.com/pypa/build) - Package building

### Tertiary (LOW confidence)
- Medium articles on GitHub Actions patterns - General patterns, verified against official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official GitHub and PyPA actions with extensive documentation
- Architecture: HIGH - Well-established patterns from official guides
- Sapling installation: MEDIUM - Platform-specific, tested against docs but not CI-verified
- Pitfalls: HIGH - Documented issues with known solutions

**Research date:** 2026-01-19
**Valid until:** 30 days (stable domain, GitHub Actions evolves slowly)
