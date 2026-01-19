# Phase 12: Packaging - Research

**Researched:** 2026-01-19
**Domain:** Python packaging with setuptools, pyproject.toml, PyPI publishing
**Confidence:** HIGH

## Summary

This phase packages gitsl as an installable Python CLI tool using modern pyproject.toml-based configuration with setuptools. The project has a flat layout with multiple Python modules in the root directory (gitsl.py, common.py, cmd_*.py) which requires explicit py-modules configuration rather than package auto-discovery.

The standard approach is:
1. Use pyproject.toml with setuptools as build backend
2. Configure explicit py-modules list for flat layout
3. Use setuptools-scm for automatic version from git tags
4. Use console_scripts entry point for the `gitsl` command
5. Use GitHub Actions with trusted publishing for PyPI releases

**Primary recommendation:** Configure pyproject.toml with explicit py-modules list, setuptools-scm for git tag versioning, and a console_scripts entry point pointing to `gitsl:main`.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| setuptools | >=80 | Build backend | Official PyPA tool, best pyproject.toml support |
| setuptools-scm | >=8 | Version from git tags | Official PyPA tool for SCM-based versioning |
| build | latest | Build wheel/sdist | Official PyPA build frontend |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| twine | latest | Upload to PyPI | Manual uploads (not needed with trusted publishing) |
| pypa/gh-action-pypi-publish | v1 | GitHub Actions publish | Automated PyPI releases |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| setuptools | hatchling | Hatchling simpler but setuptools more established |
| setuptools | flit | Flit simpler for pure Python but less flexible |
| setuptools-scm | manual version | Manual requires syncing version in multiple places |

**Installation:**
```bash
# Build dependencies (in pyproject.toml, not installed manually)
# setuptools>=80
# setuptools-scm>=8

# For local testing
pip install build
python -m build
```

## Architecture Patterns

### Recommended Project Structure
```
gitsl/
├── gitsl.py           # Main entry point with main() function
├── common.py          # Shared utilities, VERSION constant
├── cmd_*.py           # Command handlers
├── pyproject.toml     # Package configuration
├── LICENSE            # License file
├── README.md          # Package description
└── tests/             # Test suite (excluded from package)
```

### Pattern 1: Flat Layout with Explicit py-modules
**What:** List each Python module explicitly in pyproject.toml instead of relying on package auto-discovery
**When to use:** When modules are in project root, not in a package directory
**Example:**
```toml
# Source: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
[tool.setuptools]
py-modules = ["gitsl", "common", "cmd_status", "cmd_log", "cmd_diff", "cmd_init", "cmd_rev_parse", "cmd_add", "cmd_commit"]
```

### Pattern 2: Console Scripts Entry Point
**What:** Define CLI command that invokes a Python function
**When to use:** Creating command-line tools
**Example:**
```toml
# Source: https://setuptools.pypa.io/en/latest/userguide/quickstart.html
[project.scripts]
gitsl = "gitsl:main"
```

### Pattern 3: Dynamic Version from Git Tags
**What:** Version automatically derived from git tags like v0.1.0
**When to use:** When releases are tagged in git
**Example:**
```toml
# Source: https://setuptools-scm.readthedocs.io/en/latest/usage/
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
# Empty section is sufficient for basic usage
```

### Pattern 4: Runtime Version Access
**What:** Access installed package version at runtime
**When to use:** For --version flag
**Example:**
```python
# Source: https://docs.python.org/3/library/importlib.metadata.html
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("gitsl")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development
```

### Anti-Patterns to Avoid
- **Hardcoded version in multiple places:** Use setuptools-scm single source of truth
- **Using setup.py for configuration:** Use pyproject.toml exclusively
- **Relying on auto-discovery for flat layout:** Explicitly list py-modules
- **Importing package at build time:** Use attr: or setuptools-scm, not import

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version from git tags | Shell scripts parsing git describe | setuptools-scm | Handles edge cases, dev versions, dirty state |
| CLI entry point | Wrapper shell script | console_scripts | Cross-platform, proper PATH integration |
| PyPI upload | Manual curl/requests | gh-action-pypi-publish | Trusted publishing, no token management |
| Build artifacts | Manual zip/tar | python -m build | Proper wheel/sdist format, metadata |

**Key insight:** Python packaging has many edge cases (Windows paths, editable installs, namespace packages). Use established tools.

## Common Pitfalls

### Pitfall 1: Package Auto-Discovery Fails for Flat Layout
**What goes wrong:** Setuptools doesn't find modules when they're not in a package directory
**Why it happens:** Auto-discovery expects packages (directories with __init__.py), not standalone modules
**How to avoid:** Explicitly configure py-modules in [tool.setuptools]
**Warning signs:** `pip install -e .` succeeds but `import gitsl` fails

### Pitfall 2: Version Not Found at Runtime
**What goes wrong:** `importlib.metadata.version("gitsl")` raises PackageNotFoundError
**Why it happens:** Running uninstalled code (python gitsl.py) vs installed package
**How to avoid:** Always test with `pip install -e .` not direct Python execution
**Warning signs:** Works locally, fails in tests

### Pitfall 3: setuptools-scm Requires Git History
**What goes wrong:** Build fails with "LookupError: setuptools-scm was unable to detect version"
**Why it happens:** Building from tarball without .git directory
**How to avoid:** Configure fallback_version or build from git checkout
**Warning signs:** Works in dev, fails in CI with shallow clone

### Pitfall 4: Missing Modules in Wheel
**What goes wrong:** Some cmd_*.py files not included in installed package
**Why it happens:** Forgot to add new modules to py-modules list
**How to avoid:** Add each new module to py-modules array
**Warning signs:** ImportError for specific commands after install

### Pitfall 5: Entry Point Function Signature
**What goes wrong:** CLI command exits with wrong code or crashes
**Why it happens:** Entry point function must return int (exit code) or raise SystemExit
**How to avoid:** Ensure main() returns int, handle all exceptions
**Warning signs:** Command works but exit code is always 0

## Code Examples

Verified patterns from official sources:

### Complete pyproject.toml for gitsl
```toml
# Source: Composite from official setuptools documentation
[build-system]
requires = ["setuptools>=80", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "gitsl"
description = "Git to Sapling CLI shim"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Author Name", email = "author@example.com"}
]
requires-python = ">=3.8"
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
    "Topic :: Software Development :: Version Control",
]
dynamic = ["version"]

[project.scripts]
gitsl = "gitsl:main"

[project.urls]
Homepage = "https://github.com/owner/gitsl"
Repository = "https://github.com/owner/gitsl"
Issues = "https://github.com/owner/gitsl/issues"

[tool.setuptools]
py-modules = [
    "gitsl",
    "common",
    "cmd_add",
    "cmd_commit",
    "cmd_diff",
    "cmd_init",
    "cmd_log",
    "cmd_rev_parse",
    "cmd_status",
]

[tool.setuptools_scm]
fallback_version = "0.0.0"
```

### Runtime Version Access (modify common.py)
```python
# Source: https://docs.python.org/3/library/importlib.metadata.html
from importlib.metadata import version, PackageNotFoundError

try:
    VERSION = version("gitsl")
except PackageNotFoundError:
    VERSION = "0.0.0"  # Fallback for uninstalled development
```

### Build and Install Verification
```bash
# Source: https://packaging.python.org/en/latest/guides/

# Install in editable mode for development
pip install -e .

# Verify command is available
which gitsl
gitsl --version

# Build distribution
pip install build
python -m build

# Check wheel contents
unzip -l dist/gitsl-*.whl

# Install from wheel
pip install dist/gitsl-*.whl
```

### GitHub Actions Publish Workflow
```yaml
# Source: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for setuptools-scm
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/gitsl
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| setup.py | pyproject.toml | PEP 517/518 (2017) | Declarative, no code execution |
| setup.cfg | pyproject.toml [project] | PEP 621 (2020) | Single config file |
| pkg_resources | importlib.metadata | Python 3.8+ | Standard library, faster |
| API tokens | Trusted publishing | PyPI 2023 | No secret management |
| Manual version | setuptools-scm | 2015+ | Single source of truth |

**Deprecated/outdated:**
- setup.py for configuration: Use pyproject.toml exclusively
- pkg_resources: Use importlib.metadata (Python 3.8+)
- PyPI API tokens in secrets: Use trusted publishing (OIDC)
- write_to in setuptools-scm: Use version_file instead

## Open Questions

Things that couldn't be fully resolved:

1. **Test file exclusion verification**
   - What we know: tests/ directory should not be included in wheel
   - What's unclear: Whether py-modules automatically excludes tests or needs explicit exclusion
   - Recommendation: Verify wheel contents after build, add exclusion if needed

2. **Exact py-modules syntax validation**
   - What we know: Array of module names without .py extension
   - What's unclear: Whether underscore vs hyphen matters for module names
   - Recommendation: Test with pip install -e . and verify imports work

## Sources

### Primary (HIGH confidence)
- [setuptools pyproject_config.html](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html) - py-modules, packages, entry points
- [setuptools quickstart.html](https://setuptools.pypa.io/en/latest/userguide/quickstart.html) - Build system, entry points
- [setuptools package_discovery.html](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html) - py-modules vs packages
- [setuptools-scm usage](https://setuptools-scm.readthedocs.io/en/latest/usage/) - Version file, configuration
- [setuptools-scm config](https://setuptools-scm.readthedocs.io/en/latest/config/) - All configuration options
- [Python importlib.metadata docs](https://docs.python.org/3/library/importlib.metadata.html) - Runtime version access
- [PyPA publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - GitHub Actions trusted publishing

### Secondary (MEDIUM confidence)
- [Xebia setuptools guide](https://xebia.com/blog/a-practical-guide-to-setuptools-and-pyproject-toml/) - Complete examples
- [Better Stack pyproject guide](https://betterstack.com/community/guides/scaling-python/pyproject-explained/) - Version strategies
- [GitHub setuptools-scm](https://github.com/pypa/setuptools-scm) - README and examples

### Tertiary (LOW confidence)
- None required for this research

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official PyPA tools with current documentation
- Architecture: HIGH - Official setuptools documentation covers all patterns
- Pitfalls: HIGH - Well-documented common issues in official guides

**Research date:** 2026-01-19
**Valid until:** 2026-02-19 (30 days - stable domain)
