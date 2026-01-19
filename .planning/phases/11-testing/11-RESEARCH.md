# Phase 11: Testing - Research

**Researched:** 2026-01-19
**Domain:** Test infrastructure, cross-platform test runners, pytest patterns
**Confidence:** HIGH

## Summary

This research investigates how to create a comprehensive test infrastructure for gitsl, including a cross-platform test runner script, command-based test filtering, and expanded test coverage for edge cases and error conditions.

The existing test infrastructure uses pytest with well-designed fixtures and helpers. Tests are organized by command in `tests/test_cmd_*.py` files. The framework includes sophisticated comparison utilities (exact vs semantic) and skip markers for when Sapling (`sl`) is not available.

**Primary recommendation:** Build a Python-based `./test` runner script with Windows `test.cmd` wrapper that self-bootstraps a venv, installs pytest, runs tests with marker-based filtering, and supports JUnit XML output for CI integration.

## Existing Test Infrastructure

### Current State (HIGH confidence)

| Component | Location | Purpose |
|-----------|----------|---------|
| pytest.ini | `/pytest.ini` | Sets pythonpath and testpaths to `tests/` |
| conftest.py | `/tests/conftest.py` | Fixtures: `git_repo`, `git_repo_with_commit`, `git_repo_with_changes`, `sl_repo`, `sl_repo_with_commit`, `sl_repo_with_commits` |
| helpers/commands.py | `/tests/helpers/` | `CommandResult` dataclass, `run_command()` function |
| helpers/comparison.py | `/tests/helpers/` | `compare_exact()`, `compare_semantic()`, `assert_commands_equal()` |

### Existing Test Files

| File | Tests Command | Tests Count |
|------|---------------|-------------|
| test_harness.py | (self-validation) | 27 tests |
| test_execution.py | execution pipeline | 5 tests |
| test_cmd_add.py | add | 10 tests |
| test_cmd_commit.py | commit | 4 tests |
| test_cmd_diff.py | diff | 3 tests |
| test_cmd_init.py | init | 2 tests |
| test_cmd_log.py | log | 10 tests |
| test_cmd_rev_parse.py | rev-parse | 5 tests |
| test_status_porcelain.py | status | 13 tests |
| test_unsupported.py | unsupported | 8 tests |

### Current Skip Pattern

All test files that require `sl` use this pattern:
```python
import shutil
sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")
```

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | latest | Test runner and framework | De facto standard for Python testing |
| venv | stdlib | Virtual environment | Built into Python, no external deps |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-xdist | optional | Parallel test execution | Large test suites (not needed for gitsl) |

### No Additional Dependencies

The test infrastructure should only require `pytest` as an external dependency. All other tooling uses Python stdlib:
- `venv` for virtual environment creation
- `shutil.which()` for binary detection
- `subprocess` for running commands
- `pathlib` for cross-platform paths

**Installation (in venv):**
```bash
pip install pytest
```

## Architecture Patterns

### Recommended Test Runner Structure

```
gitsl/
├── test              # Python script with shebang (chmod +x)
├── test.cmd          # Windows batch wrapper
├── pytest.ini        # pytest configuration (exists)
└── tests/
    ├── conftest.py   # Fixtures and marker registration
    ├── test_add.py   # Renamed from test_cmd_add.py
    ├── test_commit.py
    ├── test_diff.py
    ├── test_init.py
    ├── test_log.py
    ├── test_rev_parse.py
    ├── test_status.py    # Renamed from test_status_porcelain.py
    ├── test_unsupported.py
    ├── test_harness.py
    ├── test_execution.py
    ├── test_edge_cases.py    # NEW: special characters, empty repos
    ├── test_error_conditions.py  # NEW: missing sl, invalid args
    ├── mocks/
    │   └── sl           # Mock sl script for error testing
    └── helpers/
        ├── __init__.py
        ├── commands.py
        └── comparison.py
```

### Pattern 1: Self-Bootstrapping Test Runner

**What:** Python script that creates venv, installs deps, and runs pytest
**When to use:** All test invocations

```python
#!/usr/bin/env python3
"""
Cross-platform test runner for gitsl.
Usage: ./test [command] [--report FILE]
"""

import os
import subprocess
import sys
import shutil
import venv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
VENV_DIR = SCRIPT_DIR / ".venv"
REQUIREMENTS = ["pytest"]


def get_venv_python() -> Path:
    """Get path to Python in venv (cross-platform)."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def get_venv_pytest() -> Path:
    """Get path to pytest in venv (cross-platform)."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "pytest.exe"
    return VENV_DIR / "bin" / "pytest"


def ensure_venv():
    """Create venv and install dependencies if needed."""
    venv_python = get_venv_python()

    if not venv_python.exists():
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)

    # Check if pytest is installed
    pytest_path = get_venv_pytest()
    if not pytest_path.exists():
        print("Installing pytest...")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-q"] + REQUIREMENTS,
            check=True
        )


def check_sl_binary():
    """Check if sl binary is available."""
    if shutil.which("sl") is None:
        print("Warning: Sapling (sl) not found. Tests requiring sl will be skipped.")


def main():
    # Check for sl upfront
    check_sl_binary()

    # Bootstrap venv
    ensure_venv()

    # Parse arguments
    args = sys.argv[1:]
    pytest_args = []
    command_filter = None
    report_file = None

    i = 0
    while i < len(args):
        if args[i] == "--report" and i + 1 < len(args):
            report_file = args[i + 1]
            i += 2
        elif not args[i].startswith("-"):
            command_filter = args[i]
            i += 1
        else:
            pytest_args.append(args[i])
            i += 1

    # Build pytest command
    cmd = [str(get_venv_pytest())]

    if command_filter:
        # Filter by marker: -m "command or always"
        cmd.extend(["-m", f"{command_filter} or always"])

    if report_file:
        cmd.extend(["--junitxml", report_file])

    cmd.extend(pytest_args)

    # Run pytest
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
```

### Pattern 2: Marker-Based Test Filtering

**What:** Use pytest markers to tag tests by command
**When to use:** All command tests

```python
# In conftest.py - register markers
def pytest_configure(config):
    config.addinivalue_line("markers", "add: tests for git add command")
    config.addinivalue_line("markers", "commit: tests for git commit command")
    config.addinivalue_line("markers", "diff: tests for git diff command")
    config.addinivalue_line("markers", "init: tests for git init command")
    config.addinivalue_line("markers", "log: tests for git log command")
    config.addinivalue_line("markers", "rev_parse: tests for git rev-parse command")
    config.addinivalue_line("markers", "status: tests for git status command")
    config.addinivalue_line("markers", "unsupported: tests for unsupported commands")
    config.addinivalue_line("markers", "always: tests that run regardless of filter")

# In test files - apply markers
import pytest

pytestmark = pytest.mark.add  # Marks all tests in file

@pytest.mark.add
class TestAddBasic:
    ...
```

### Pattern 3: Mock sl Binary via PATH

**What:** Create a mock sl script and inject via PATH
**When to use:** Testing error conditions, sl unavailable scenarios

```python
# tests/mocks/sl (make executable)
#!/usr/bin/env python3
"""Mock sl binary for testing error conditions."""
import os
import sys

exit_code = int(os.environ.get("MOCK_SL_EXIT", "0"))
stdout = os.environ.get("MOCK_SL_STDOUT", "")
stderr = os.environ.get("MOCK_SL_STDERR", "")

if stdout:
    print(stdout)
if stderr:
    print(stderr, file=sys.stderr)
sys.exit(exit_code)
```

```python
# In test - use PATH injection
@pytest.fixture
def mock_sl_path(tmp_path):
    """Create mock sl in temp dir and return modified PATH."""
    mock_dir = tmp_path / "mock_bin"
    mock_dir.mkdir()

    mock_sl = mock_dir / "sl"
    mock_sl.write_text('#!/usr/bin/env python3\nimport sys; sys.exit(1)')
    mock_sl.chmod(0o755)

    # Prepend mock dir to PATH
    new_path = str(mock_dir) + os.pathsep + os.environ.get("PATH", "")
    return {"PATH": new_path}

def test_sl_failure(git_repo, mock_sl_path):
    result = run_gitsl(["status"], cwd=git_repo, env=mock_sl_path)
    assert result.exit_code != 0
```

### Anti-Patterns to Avoid

- **Shell scripts for cross-platform:** Don't use bash scripts that won't work on Windows
- **Hardcoded paths:** Always use `pathlib.Path` for cross-platform compatibility
- **Requiring global pytest:** Don't assume pytest is globally installed
- **Skipping venv check:** Always verify venv exists before running pytest

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test filtering | Custom test discovery | pytest `-m` markers | Pytest handles all edge cases |
| JUnit XML output | Custom XML generation | pytest `--junitxml` | Standard format, tested |
| TTY detection | Custom isatty checks | pytest auto-detection | Handles all edge cases |
| venv creation | subprocess venv calls | `venv.create()` | Python stdlib, handles cross-platform |
| Binary detection | shell `which` | `shutil.which()` | Works on Windows too |

**Key insight:** pytest has mature solutions for test filtering, reporting, and output formatting. Use built-in features rather than custom implementations.

## Common Pitfalls

### Pitfall 1: Windows PATH and Binary Detection
**What goes wrong:** Tests fail to find `sl` or mock binaries on Windows
**Why it happens:** Windows uses different path separators and `.exe` extensions
**How to avoid:** Always use `shutil.which()` and `pathlib.Path`. For mock binaries, create both `sl` and `sl.cmd` on Windows.
**Warning signs:** Tests pass on Linux/Mac but fail on Windows

### Pitfall 2: Venv Activation vs Direct Execution
**What goes wrong:** Trying to "activate" venv in subprocess calls
**Why it happens:** Activation is shell-specific and not needed
**How to avoid:** Call venv executables directly: `.venv/bin/python` or `.venv/Scripts/python.exe`
**Warning signs:** Reliance on `source activate` or batch `activate.bat`

### Pitfall 3: Marker Registration
**What goes wrong:** pytest warns about unknown markers
**Why it happens:** Markers not registered in conftest.py or pytest.ini
**How to avoid:** Register all markers in `pytest_configure` hook or `pytest.ini`
**Warning signs:** "PytestUnknownMarkWarning" in output

### Pitfall 4: Test File Discovery with Renames
**What goes wrong:** Renamed test files not discovered
**Why it happens:** pytest uses `test_*.py` pattern
**How to avoid:** Ensure renamed files still match `test_*.py` pattern
**Warning signs:** Test count drops after renaming

### Pitfall 5: Empty Repo Edge Cases
**What goes wrong:** Tests assume at least one commit exists
**Why it happens:** Many sl commands behave differently in empty repos
**How to avoid:** Use `sl_repo` fixture (empty) vs `sl_repo_with_commit` fixture explicitly
**Warning signs:** Tests pass locally but fail in CI on fresh checkout

## Code Examples

### Windows Wrapper (test.cmd)

```batch
@echo off
REM Windows wrapper for test runner
python "%~dp0test" %*
```

### Marker Registration in pytest.ini

```ini
[pytest]
pythonpath = tests
testpaths = tests
markers =
    add: tests for git add command
    commit: tests for git commit command
    diff: tests for git diff command
    init: tests for git init command
    log: tests for git log command
    rev_parse: tests for git rev-parse command
    status: tests for git status command
    unsupported: tests for unsupported commands
    always: tests that run regardless of filter
```

### Edge Case Test Examples

```python
# test_edge_cases.py
import pytest
from conftest import run_gitsl

pytestmark = pytest.mark.always  # Run with any filter


class TestSpecialCharacters:
    """Test handling of special characters in filenames."""

    def test_filename_with_spaces(self, sl_repo):
        """File with spaces in name."""
        file = sl_repo / "file with spaces.txt"
        file.write_text("content\n")

        result = run_gitsl(["add", "file with spaces.txt"], cwd=sl_repo)
        assert result.exit_code == 0

    def test_filename_with_unicode(self, sl_repo):
        """File with unicode characters."""
        file = sl_repo / "file_\u00e9\u00e8.txt"  # accented chars
        file.write_text("content\n")

        result = run_gitsl(["add", "file_\u00e9\u00e8.txt"], cwd=sl_repo)
        assert result.exit_code == 0


class TestEmptyRepo:
    """Test behavior in empty repository."""

    def test_status_empty_repo(self, sl_repo):
        """Status in repo with no files."""
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert result.exit_code == 0
        assert result.stdout == ""

    def test_log_empty_repo(self, sl_repo):
        """Log in repo with no commits."""
        result = run_gitsl(["log"], cwd=sl_repo)
        # sl log on empty repo should handle gracefully
        # (may succeed with empty output or fail - test actual behavior)
```

### Error Condition Test Examples

```python
# test_error_conditions.py
import os
import pytest
from pathlib import Path
from conftest import run_gitsl
from helpers.commands import run_command

pytestmark = pytest.mark.always


class TestMissingSl:
    """Test behavior when sl binary is not available."""

    @pytest.fixture
    def empty_path_env(self, tmp_path):
        """Environment with empty PATH (no sl)."""
        # Create a minimal PATH with just Python
        # This ensures sl cannot be found
        return {"PATH": ""}

    def test_gitsl_without_sl(self, tmp_path, empty_path_env):
        """gitsl should fail gracefully when sl is not found."""
        result = run_gitsl(["status"], cwd=tmp_path, env=empty_path_env)
        assert result.exit_code != 0
        # Should have helpful error message


class TestInvalidArgs:
    """Test handling of invalid arguments."""

    def test_unknown_command(self, sl_repo):
        """Unknown command handled gracefully."""
        result = run_gitsl(["unknowncommand"], cwd=sl_repo)
        assert result.exit_code == 0  # UNSUP-02: unsupported exits 0
        assert "unsupported" in result.stderr.lower()
```

## Coverage Gaps Identified

### Commands Not Fully Tested

| Command | Gap | Needed Tests |
|---------|-----|--------------|
| status | No empty repo test | `status --porcelain` on repo with 0 commits |
| log | No empty repo test | `log` behavior with no commits |
| diff | Limited | diff with staged changes, specific files |
| init | Limited | init in existing repo, init with path |
| add | No special chars | Files with spaces, unicode |
| commit | Limited | commit with -a flag, amend |

### Edge Cases Needed

1. **Special characters in filenames:**
   - Spaces: `"file name.txt"`
   - Unicode: `"file_\u00e9.txt"`
   - Special chars: `"file[1].txt"`, `"file@2.txt"`

2. **Empty/fresh repositories:**
   - status on empty repo
   - log on repo with no commits
   - diff on repo with no commits

3. **Large file scenarios:**
   - Many files (100+)
   - Large file content

4. **Path edge cases:**
   - Subdirectories
   - Relative vs absolute paths
   - Paths with `.` and `..`

### Error Conditions Needed

1. **Missing sl binary** - gitsl behavior when `sl` not in PATH
2. **Invalid arguments** - malformed flags, missing required args
3. **sl command failures** - sl returns non-zero, handle stderr
4. **Permission errors** - read-only directories, no write access

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| unittest | pytest | ~2015 | Better fixtures, cleaner assertions |
| setup.py test | pytest direct | ~2020 | No need for setup.py entry point |
| bash test scripts | Python runners | Current best practice | Cross-platform support |
| manual marker tracking | pytest.ini registration | pytest 5.0+ | Warnings on unknown markers |

**Deprecated/outdated:**
- `nose` test framework: Unmaintained, use pytest
- `unittest.TestCase` base class: Not needed with pytest (though compatible)

## Open Questions

Things that couldn't be fully resolved:

1. **Mock sl on Windows**
   - What we know: Need `.cmd` wrapper or Python script
   - What's unclear: Exact Windows PATH behavior with mock
   - Recommendation: Test on Windows early, may need `.cmd` wrapper

2. **CI caching of venv**
   - What we know: Self-bootstrapping works
   - What's unclear: Whether to cache `.venv` in CI
   - Recommendation: Let CI recreate venv each run for simplicity

## Sources

### Primary (HIGH confidence)
- pytest official documentation - Marker registration, skip patterns, JUnit output
- Python venv documentation - Programmatic venv creation
- gitsl codebase analysis - Existing test structure and patterns

### Secondary (MEDIUM confidence)
- [pytest-with-eric.com](https://pytest-with-eric.com/introduction/pytest-k-options/) - -k option filtering
- [LambdaTest pytest tutorial](https://www.lambdatest.com/blog/xml-reports-in-pytest/) - JUnit XML reports

### Tertiary (LOW confidence)
- General web search on cross-platform patterns

## Metadata

**Confidence breakdown:**
- Existing infrastructure: HIGH - Direct code analysis
- pytest patterns: HIGH - Official documentation
- Cross-platform runner: MEDIUM - Tested patterns, Windows needs validation
- Edge case coverage: HIGH - Requirements clearly specified

**Research date:** 2026-01-19
**Valid until:** 60 days (stable tooling, no rapid changes expected)
