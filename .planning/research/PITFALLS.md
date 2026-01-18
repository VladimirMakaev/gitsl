# Pitfalls Research: v1.1 Polish (Packaging & CI/CD)

**Domain:** Python CLI package publishing and cross-platform CI
**Researched:** 2026-01-18
**Confidence:** HIGH (verified against PyPI docs, GitHub Actions docs, and Python Packaging Guide)

---

## PyPI Publishing Pitfalls

### Pitfall 1: Version Already Exists (Immutable Releases)

**What goes wrong:** Attempting to upload a version that already exists on PyPI fails with "File already exists" error.

**Why it happens:** PyPI does not allow overwriting releases. Once version 1.0.0 is uploaded, it cannot be replaced or deleted (even if yanked, the version number remains reserved).

**Consequences:**
- Failed CI releases require version bump to fix
- Accidental premature release blocks that version number forever
- Testing on TestPyPI then real PyPI can cause version conflicts

**Prevention:**
```yaml
# Test on TestPyPI first with .dev versions
# pyproject.toml
version = "1.0.0.dev1"  # For testing

# Only tag and release final versions after TestPyPI validation
# Use semantic versioning: 1.0.0, 1.0.1, 1.1.0
```

**Warning signs:** CI publishing step fails with 400 error mentioning "file already exists"

**Which phase should address:** Phase 1 (Release Workflow Setup). Establish versioning discipline before first release.

**Source:** [PyPI Docs](https://docs.pypi.org/) - HIGH confidence

---

### Pitfall 2: Missing Trusted Publisher Configuration

**What goes wrong:** GitHub Actions workflow fails with 403 Forbidden when attempting to publish to PyPI.

**Why it happens:** Trusted Publishing requires explicit configuration on PyPI before the first publish. The workflow, repository, and environment must all match exactly.

**Consequences:**
- First release attempt fails
- Must manually configure PyPI project settings
- Environment name mismatch silently fails

**Prevention:**
```yaml
# 1. Configure on PyPI BEFORE first release:
#    pypi.org/manage/account/publishing/
#    - Repository: owner/repo
#    - Workflow: release.yml (exact filename)
#    - Environment: pypi (if using environments)

# 2. Workflow must have id-token permission:
jobs:
  publish:
    permissions:
      id-token: write  # MANDATORY for trusted publishing

    # 3. Environment must match PyPI configuration
    environment:
      name: pypi
      url: https://pypi.org/p/gitsl
```

**Warning signs:** 403 errors mentioning "token" or "authentication" despite using trusted publishing

**Which phase should address:** Phase 1 (Release Workflow Setup). Configure before first release attempt.

**Source:** [PyPI Trusted Publishers Docs](https://docs.pypi.org/trusted-publishers/) - HIGH confidence

---

### Pitfall 3: TestPyPI vs PyPI Account Confusion

**What goes wrong:** Credentials work on TestPyPI but not PyPI, or vice versa.

**Why it happens:** TestPyPI and PyPI are completely separate systems with independent:
- User accounts
- API tokens
- Trusted publisher configurations
- Package namespaces

**Consequences:**
- Package name available on TestPyPI but taken on real PyPI
- Trusted publisher must be configured on BOTH separately
- Different tokens/credentials needed for each

**Prevention:**
```yaml
# Configure trusted publishing on BOTH:
# 1. test.pypi.org/manage/account/publishing/
# 2. pypi.org/manage/account/publishing/

# Use separate workflow jobs or conditions:
jobs:
  publish-testpypi:
    if: github.event_name == 'push'  # Every push
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      repository-url: https://test.pypi.org/legacy/

  publish-pypi:
    if: startsWith(github.ref, 'refs/tags/')  # Only tags
    uses: pypa/gh-action-pypi-publish@release/v1
```

**Warning signs:** Works on test, fails on production (or reverse)

**Which phase should address:** Phase 1 (Release Workflow). Check package name availability on real PyPI first.

**Source:** [Using TestPyPI - Python Packaging Guide](https://packaging.python.org/en/latest/guides/using-testpypi/) - HIGH confidence

---

### Pitfall 4: pypa/gh-action-pypi-publish is Linux-Only

**What goes wrong:** Publish job fails when using Windows or macOS runner.

**Why it happens:** The official PyPI publish action is Docker-based and only runs on Linux runners.

**Consequences:**
- Build on Windows/macOS, but MUST publish from Linux job
- Requires separate build and publish jobs with artifact transfer

**Prevention:**
```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.os }}
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest  # MUST be Linux
    steps:
      - uses: actions/download-artifact@v4
      - uses: pypa/gh-action-pypi-publish@release/v1
```

**Warning signs:** "Cannot run Docker-based action on this runner"

**Which phase should address:** Phase 2 (CI Pipeline). Design job structure with Linux publish job.

**Source:** [gh-action-pypi-publish README](https://github.com/pypa/gh-action-pypi-publish) - HIGH confidence

---

### Pitfall 5: Build Artifacts Not in dist/ Directory

**What goes wrong:** Publish action finds no files to upload.

**Why it happens:**
- Build output in wrong location
- Artifact download doesn't preserve directory structure
- `python -m build` outputs to `dist/` but action looks elsewhere

**Consequences:**
- Empty release
- "No files to upload" error

**Prevention:**
```yaml
# Ensure build creates dist/
- run: python -m build
  # Creates: dist/package-1.0.0.tar.gz and dist/package-1.0.0-py3-none-any.whl

# When downloading artifacts, merge into single dist/
- uses: actions/download-artifact@v4
  with:
    path: dist/
    merge-multiple: true  # Combine all artifacts
    pattern: dist-*

# Verify before publish
- run: ls -la dist/
```

**Warning signs:** Publish step completes instantly with no files uploaded

**Which phase should address:** Phase 2 (CI Pipeline). Test artifact flow locally first.

**Source:** [Python Packaging Guide - Publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - HIGH confidence

---

## Cross-Platform CI Pitfalls

### Pitfall 6: Windows PowerShell `sl` Alias Conflict

**What goes wrong:** `sl` command in Windows CI runs PowerShell's `Set-Location` instead of Sapling.

**Why it happens:** PowerShell has a built-in alias `sl` for `Set-Location` (equivalent to `cd`). This alias takes precedence over the Sapling binary.

**Consequences:**
- Tests using `sl` commands fail mysteriously on Windows
- Error messages about invalid paths instead of Sapling errors
- Works locally if user removed alias, fails in CI

**Prevention:**
```powershell
# Option 1: Remove the alias in workflow
Remove-Alias -Name sl -Force -ErrorAction SilentlyContinue

# Option 2: Use full path
C:\Program Files\Sapling\sl.exe status

# Option 3: In Python tests, always use full path on Windows
import shutil
sl_path = shutil.which('sl') or r'C:\Program Files\Sapling\sl.exe'
```

**Warning signs:** Windows tests fail with path-related errors, Linux/macOS pass

**Which phase should address:** Phase 2 (CI Pipeline). Add alias removal to Windows setup.

**Source:** [Sapling Installation Docs](https://sapling-scm.com/docs/introduction/getting-started/) - HIGH confidence

---

### Pitfall 7: Path Separator Differences

**What goes wrong:** File paths in tests or output use wrong separator for platform.

**Why it happens:**
- Windows uses `\`, Unix uses `/`
- Hardcoded paths break cross-platform
- Git/Sapling output may normalize to `/` even on Windows

**Consequences:**
- Path comparisons fail
- File operations fail
- Tests pass on one OS, fail on others

**Prevention:**
```python
# WRONG - hardcoded separator
expected = "src/gitsl/main.py"

# CORRECT - use pathlib or os.path
from pathlib import Path
expected = Path("src/gitsl/main.py")  # Handles separators

# For comparing git output (which uses /), normalize:
output_path = output.replace('\\', '/')
```

**Warning signs:** String comparison failures in tests involving paths

**Which phase should address:** Phase 2 (CI Pipeline). Review all path handling in tests.

**Source:** [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence

---

### Pitfall 8: Line Ending Differences (CRLF vs LF)

**What goes wrong:** Tests comparing file contents or command output fail due to line endings.

**Why it happens:**
- Windows defaults to CRLF (`\r\n`)
- Unix uses LF (`\n`)
- Git can auto-convert line endings
- Text mode file reads may not preserve original endings

**Consequences:**
- String comparisons fail
- Hash/checksum differences
- Diff output shows entire file changed

**Prevention:**
```python
# Normalize line endings in comparisons
def normalize_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')

# Configure git to handle line endings
# .gitattributes
* text=auto eol=lf

# In subprocess, use text=True for automatic handling
result = subprocess.run(cmd, capture_output=True, text=True)
```

**Warning signs:** Tests fail only on Windows with output comparison errors

**Which phase should address:** Phase 2 (CI Pipeline). Add .gitattributes and normalize in tests.

**Source:** General cross-platform patterns - HIGH confidence

---

### Pitfall 9: GitHub Actions Cache Key Mismatch Across OS

**What goes wrong:** Cache restored from wrong OS, causing failures or wasted time.

**Why it happens:** Same cache key used across different operating systems. A cache saved on Linux cannot be used on Windows due to:
- Different paths
- Different compression
- Binary incompatibility

**Consequences:**
- Cache restores but contents unusable
- Subtle failures from wrong binaries
- No cache benefit if key doesn't include OS

**Prevention:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    # MUST include runner.os in key
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**Warning signs:** Cache hit but installation still runs, or strange import errors

**Which phase should address:** Phase 2 (CI Pipeline). Always include OS in cache keys.

**Source:** [GitHub Actions Cache Documentation](https://github.com/actions/cache) - HIGH confidence

---

### Pitfall 10: Matrix Strategy fail-fast Behavior

**What goes wrong:** One failing OS/Python combination cancels all other matrix jobs.

**Why it happens:** `fail-fast: true` is the default. When one job fails, GitHub cancels pending and running jobs in the same matrix.

**Consequences:**
- Cannot see which platforms actually work
- Intermittent failures cancel valid tests
- Hard to debug platform-specific issues

**Prevention:**
```yaml
strategy:
  fail-fast: false  # Let all jobs complete
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

**Warning signs:** Jobs showing as "cancelled" rather than failed/passed

**Which phase should address:** Phase 2 (CI Pipeline). Set fail-fast: false for test matrices.

**Source:** [GitHub Actions Matrix Documentation](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs) - HIGH confidence

---

## Sapling Installation in CI

### Pitfall 11: No Official Sapling GitHub Action

**What goes wrong:** Searching for `sapling-scm/setup-sapling` action finds nothing.

**Why it happens:** Unlike many tools, Sapling doesn't provide an official GitHub Action for installation. Manual installation required.

**Consequences:**
- Must write custom installation steps
- Different installation for each OS
- Version pinning is manual

**Prevention:**
```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}

    steps:
      - name: Install Sapling (Ubuntu)
        if: runner.os == 'Linux'
        run: |
          RELEASE="0.2.20250521-115337+25ed6ac4"
          curl -L -o sapling.deb \
            "https://github.com/facebook/sapling/releases/download/${RELEASE}/sapling_${RELEASE}_amd64.Ubuntu22.04.deb"
          sudo dpkg -i sapling.deb

      - name: Install Sapling (macOS)
        if: runner.os == 'macOS'
        run: brew install sapling

      - name: Install Sapling (Windows)
        if: runner.os == 'Windows'
        run: |
          # Download and extract Windows build
          # Add to PATH
```

**Warning signs:** "sl: command not found" in CI

**Which phase should address:** Phase 2 (CI Pipeline). Create reusable installation steps.

**Source:** [Sapling Releases](https://github.com/facebook/sapling/releases) - HIGH confidence

---

### Pitfall 12: Sapling Version Not Pinned

**What goes wrong:** CI suddenly breaks when Sapling releases new version with breaking changes.

**Why it happens:**
- `brew install sapling` gets latest version
- Releases may change command behavior
- No version constraint in workflow

**Consequences:**
- Flaky CI (works sometimes, fails others)
- Hard to reproduce failures locally
- Unexpected behavior changes

**Prevention:**
```yaml
# Pin to specific release version
- name: Install Sapling (Ubuntu)
  run: |
    VERSION="0.2.20250521-115337+25ed6ac4"
    curl -L -o sapling.deb \
      "https://github.com/facebook/sapling/releases/download/${VERSION}/..."
    sudo dpkg -i sapling.deb

# For Homebrew, pin if possible
- name: Install Sapling (macOS)
  run: |
    brew tap facebook/fb
    brew install facebook/fb/sapling@0.2  # If available
```

**Warning signs:** CI fails on date X but passed before, no code changes

**Which phase should address:** Phase 2 (CI Pipeline). Pin versions from the start.

**Source:** [Sapling Releases](https://github.com/facebook/sapling/releases) - MEDIUM confidence

---

### Pitfall 13: Missing Git Dependency for Sapling

**What goes wrong:** Sapling commands fail in CI even though sl is installed.

**Why it happens:** When using Sapling in git-compatible mode (working with .git repos), it requires git to be installed for certain operations.

**Consequences:**
- Tests fail with cryptic errors
- Works locally where git is always present
- Partial test failures

**Prevention:**
```yaml
# Ensure git is installed (usually is by default, but verify)
- name: Setup dependencies
  run: |
    git --version
    sl --version
```

**Warning signs:** Some Sapling operations fail with "git not found" in logs

**Which phase should address:** Phase 2 (CI Pipeline). Verify git presence in setup.

**Source:** [Sapling Getting Started](https://sapling-scm.com/docs/introduction/getting-started/) - MEDIUM confidence

---

### Pitfall 14: Windows Sapling PATH Not Set

**What goes wrong:** Sapling installed on Windows but `sl` not found.

**Why it happens:** Windows Sapling installer adds to PATH but:
- GitHub Actions may not pick up PATH changes mid-job
- Installer may require shell restart
- PATH modification may not persist between steps

**Consequences:**
- Install succeeds, tests fail
- Manual PATH addition required

**Prevention:**
```yaml
- name: Install Sapling (Windows)
  run: |
    # Download and install
    Invoke-WebRequest -Uri $URL -OutFile sapling.zip
    Expand-Archive sapling.zip -DestinationPath C:\sapling

    # Explicitly add to PATH for subsequent steps
    echo "C:\sapling" >> $env:GITHUB_PATH
```

**Warning signs:** Windows install step passes, next step fails with "sl not found"

**Which phase should address:** Phase 2 (CI Pipeline). Explicitly add to GITHUB_PATH.

**Source:** [Sapling Installation Docs](https://sapling-scm.com/docs/introduction/getting-started/) - HIGH confidence

---

## Package Structure Pitfalls

### Pitfall 15: Missing [build-system] Table

**What goes wrong:** `pip install .` fails or uses legacy behavior with deprecation warnings.

**Why it happens:** pyproject.toml without `[build-system]` table is treated as legacy. Modern pip requires explicit build system declaration.

**Consequences:**
- "No build backend configured" errors
- Falls back to deprecated setup.py behavior
- Installation may silently work differently than expected

**Prevention:**
```toml
# pyproject.toml - ALWAYS include this
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "gitsl"
version = "1.0.0"
# ...
```

**Warning signs:** DeprecationWarning about build backend during install

**Which phase should address:** Phase 1 (Package Structure). Add from the start.

**Source:** [Python Packaging Guide - Modernizing setup.py](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/) - HIGH confidence

---

### Pitfall 16: Console Scripts Not Working After Install

**What goes wrong:** `pip install .` succeeds but `gitsl` command not found.

**Why it happens:**
- `[project.scripts]` entry point syntax wrong
- Module path doesn't match actual package structure
- Function doesn't exist or has wrong signature

**Consequences:**
- Package installs but command unavailable
- Command exists but fails immediately on import

**Prevention:**
```toml
# pyproject.toml
[project.scripts]
gitsl = "gitsl:main"  # module:function

# Verify:
# 1. gitsl.py exists in package root OR gitsl/__init__.py
# 2. main() function exists and is importable
# 3. main() accepts no required arguments

# Test locally:
pip install -e .
which gitsl  # Should show path
gitsl --version  # Should work
```

**Warning signs:** "command not found" after successful install

**Which phase should address:** Phase 1 (Package Structure). Test entry points before release.

**Source:** [Setuptools Entry Points Documentation](https://setuptools.pypa.io/en/latest/userguide/entry_point.html) - HIGH confidence

---

### Pitfall 17: Version String Duplication

**What goes wrong:** Version in pyproject.toml doesn't match version in code, causing confusion.

**Why it happens:**
- Version hardcoded in multiple places
- Forgot to update one when bumping version
- `--version` flag shows different version than pip

**Consequences:**
- User confusion about actual version
- Bug reports reference wrong version
- Debugging nightmare

**Prevention:**
```toml
# Option 1: Single source in pyproject.toml (simplest for small packages)
[project]
version = "1.0.0"

# Access at runtime:
from importlib.metadata import version
VERSION = version("gitsl")
```

```python
# common.py - get version from package metadata
try:
    from importlib.metadata import version
    VERSION = version("gitsl")
except Exception:
    VERSION = "0.0.0-dev"  # Fallback for development
```

**Warning signs:** `--version` shows different version than `pip show`

**Which phase should address:** Phase 1 (Package Structure). Establish single source of truth.

**Source:** [Python Packaging Guide - Version Management](https://betterstack.com/community/guides/scaling-python/pyproject-explained/) - HIGH confidence

---

### Pitfall 18: Package Not Including All Necessary Files

**What goes wrong:** Installed package missing files that exist in source tree.

**Why it happens:**
- Setuptools auto-discovery misses files
- Non-.py files (configs, data) not included
- Files outside package directory excluded

**Consequences:**
- ImportError for missing modules
- FileNotFoundError for data files
- Works in dev, fails when installed

**Prevention:**
```toml
# pyproject.toml - be explicit about package structure
[tool.setuptools]
packages = ["gitsl"]  # Or use find:

# For flat layout (files in root):
[tool.setuptools]
py-modules = ["gitsl", "common", "cmd_status", "cmd_log", "cmd_diff",
              "cmd_init", "cmd_rev_parse", "cmd_add", "cmd_commit"]

# Include non-Python files:
[tool.setuptools.package-data]
gitsl = ["*.json", "*.txt"]
```

**Warning signs:** "ModuleNotFoundError" after pip install

**Which phase should address:** Phase 1 (Package Structure). List modules explicitly.

**Source:** [Python Packaging Guide](https://www.pyopensci.org/python-package-guide/package-structure-code/pyproject-toml-python-package-metadata.html) - HIGH confidence

---

### Pitfall 19: requires-python Not Set

**What goes wrong:** Package installed on unsupported Python version, then crashes with syntax errors.

**Why it happens:** Without `requires-python`, pip allows installation on any Python version. Modern syntax (f-strings, walrus operator, etc.) then fails on older Python.

**Consequences:**
- SyntaxError on older Python
- Confusing error messages
- Users blame package, not their Python version

**Prevention:**
```toml
[project]
name = "gitsl"
requires-python = ">=3.9"

# Also add classifiers for clarity (informational only)
classifiers = [
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

**Warning signs:** Issues from users on old Python with syntax errors

**Which phase should address:** Phase 1 (Package Structure). Set minimum version explicitly.

**Source:** [Writing pyproject.toml - Python Packaging Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - HIGH confidence

---

### Pitfall 20: Flat Layout Without Explicit Module List

**What goes wrong:** gitsl uses flat layout (modules in repo root), but setuptools doesn't find all modules.

**Why it happens:**
- Setuptools' auto-discovery is designed for src/ layout or package directories
- Flat layout with multiple .py files in root needs explicit configuration
- `find:` doesn't work well for flat layouts

**Consequences:**
- Only some modules included in wheel
- ImportError for "helper" modules
- Works locally (all files present), fails after install

**Prevention:**
```toml
# For gitsl's flat layout, be EXPLICIT:
[tool.setuptools]
py-modules = [
    "gitsl",
    "common",
    "cmd_status",
    "cmd_log",
    "cmd_diff",
    "cmd_init",
    "cmd_rev_parse",
    "cmd_add",
    "cmd_commit"
]

# Test with:
pip install . && python -c "import common; print('OK')"
```

**Warning signs:** `pip show -f gitsl` shows fewer files than expected

**Which phase should address:** Phase 1 (Package Structure). Critical for gitsl's layout.

**Source:** [Setuptools Package Discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html) - HIGH confidence

---

## Phase-Specific Warning Summary

| Phase | Topic | Critical Pitfalls | Prevention |
|-------|-------|-------------------|------------|
| Phase 1 | Package Structure | #15 (build-system), #16 (entry points), #18 (module list), #20 (flat layout) | Explicit pyproject.toml, test install early |
| Phase 1 | Versioning | #1 (immutable), #17 (duplication) | Single source of truth, test on TestPyPI |
| Phase 1 | PyPI Setup | #2 (trusted publisher), #3 (TestPyPI separation) | Configure both registries before first release |
| Phase 2 | CI Matrix | #6 (sl alias), #7 (paths), #8 (line endings), #10 (fail-fast) | OS-specific handling, normalization |
| Phase 2 | Sapling Install | #11 (no action), #12 (version pin), #14 (Windows PATH) | Custom install steps, pin versions |
| Phase 2 | Publishing | #4 (Linux only), #5 (artifacts) | Separate build/publish jobs, artifact transfer |

---

## Recommended Workflow Structure

Based on pitfalls research, the CI/CD workflow should follow this structure:

```
1. Test Job (matrix: OS x Python)
   - Install Sapling (OS-specific)
   - Install package in editable mode
   - Run tests
   - fail-fast: false

2. Build Job (single Linux runner)
   - Build sdist and wheel
   - Upload as artifact
   - Runs after test job passes

3. Publish-TestPyPI Job (optional, Linux only)
   - Download artifact
   - Publish to test.pypi.org
   - Runs on push to main

4. Publish-PyPI Job (Linux only)
   - Download artifact
   - Publish to pypi.org
   - Runs only on version tags
   - Requires environment approval
```

---

## Sources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/) - HIGH confidence
- [Python Packaging Guide - Publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - HIGH confidence
- [Using TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/) - HIGH confidence
- [gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) - HIGH confidence
- [GitHub Actions Cache](https://github.com/actions/cache) - HIGH confidence
- [GitHub Actions Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs) - HIGH confidence
- [Sapling Installation](https://sapling-scm.com/docs/introduction/getting-started/) - HIGH confidence
- [Sapling Releases](https://github.com/facebook/sapling/releases) - HIGH confidence
- [Python Packaging Guide - Modernizing setup.py](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/) - HIGH confidence
- [Setuptools Entry Points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html) - HIGH confidence
- [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - HIGH confidence
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence
