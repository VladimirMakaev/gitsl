# Phase 2: E2E Test Infrastructure - Research

**Researched:** 2026-01-18
**Domain:** Python E2E testing with pytest, subprocess capture, output comparison
**Confidence:** HIGH

## Summary

Phase 2 establishes the test infrastructure for comparing git and gitsl behavior on temporary repositories. The golden-master approach requires: (1) creating temp git repos with known states, (2) running commands via subprocess and capturing output, (3) comparing results with both exact and semantic matching.

The standard approach is:
1. Use pytest's `tmp_path` fixture for temporary directories
2. Create git repos by running `git init` and setup commands
3. Capture subprocess output with `subprocess.run(capture_output=True, text=True)`
4. Use a helper function that returns a dataclass with stdout, stderr, exit_code
5. Implement two comparison modes: exact match and semantic match (normalized whitespace)

**Primary recommendation:** Use pytest with custom fixtures in `conftest.py`. Create a `run_command()` helper that wraps `subprocess.run()` and returns a `CommandResult` dataclass. Use exact matching for porcelain formats, semantic matching (whitespace normalization) for human-readable output.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pytest` | 8.x | Test framework | Industry standard for Python testing |
| `subprocess` | stdlib | Command execution | Official Python subprocess API |
| `tempfile` | stdlib | Temp directory creation | Secure temp handling, matches requirement |
| `dataclasses` | stdlib | Result objects | Clean structured data |
| `difflib` | stdlib | Output comparison | Semantic diff capabilities |
| `pathlib` | stdlib | Path manipulation | Modern path handling |

### Not Needed

| Library | Why Avoid |
|---------|-----------|
| `pytest-git` | External dependency; simple `git init` via subprocess is sufficient |
| `GitPython` | External dependency; only need CLI testing, not API |
| `pytest-goldie` | Overkill for our comparison needs; custom comparison is simpler |

**Installation:**
```bash
pip install pytest
```

Note: All other dependencies are stdlib - no additional packages required.

## Architecture Patterns

### Recommended Test Structure

```
tests/
    conftest.py         # Shared fixtures: git_repo, run_git, run_gitsl
    test_harness.py     # Test that harness itself works correctly
    test_status.py      # E2E tests for status command (future phases)
    test_commit.py      # E2E tests for commit command (future phases)
    helpers/
        __init__.py
        comparison.py   # Comparison utilities (exact, semantic)
        commands.py     # CommandResult, run_command helper
```

### Pattern 1: CommandResult Dataclass

**What:** Structured container for command execution results.

**When to use:** Every time you run a subprocess command in tests.

**Example:**
```python
# Source: Python dataclasses documentation + subprocess.CompletedProcess pattern
from dataclasses import dataclass

@dataclass
class CommandResult:
    """Result of running a command via subprocess."""
    stdout: str
    stderr: str
    exit_code: int

    @property
    def success(self) -> bool:
        """Return True if command exited with code 0."""
        return self.exit_code == 0
```

### Pattern 2: Command Runner Helper

**What:** Wrapper function that runs a command and returns CommandResult.

**When to use:** All subprocess calls in tests.

**Example:**
```python
# Source: Python subprocess.run documentation
import subprocess
from pathlib import Path
from typing import List, Optional

def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None
) -> CommandResult:
    """
    Run a command and capture all output.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory (default: current)
        env: Environment variables (default: inherit)

    Returns:
        CommandResult with stdout, stderr, exit_code
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return CommandResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )
```

### Pattern 3: Git Repo Fixture with Yield

**What:** Pytest fixture that creates a temp git repo and cleans up after.

**When to use:** Tests that need a real git repository.

**Example:**
```python
# Source: pytest tmp_path documentation + git init pattern
import pytest
from pathlib import Path

@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """
    Create a temporary git repository.

    Uses tmp_path which is automatically cleaned up by pytest.
    Returns the repo path for test use.
    """
    # Initialize git repo
    run_command(["git", "init"], cwd=tmp_path)

    # Configure git for commits (needed for CI environments)
    run_command(["git", "config", "user.email", "test@test.com"], cwd=tmp_path)
    run_command(["git", "config", "user.name", "Test User"], cwd=tmp_path)

    return tmp_path
```

### Pattern 4: Repo with Initial Commit Fixture

**What:** Git repo with an initial commit already made.

**When to use:** Most tests need at least one commit to work with.

**Example:**
```python
@pytest.fixture
def git_repo_with_commit(git_repo: Path) -> Path:
    """Git repo with initial commit."""
    # Create a file
    readme = git_repo / "README.md"
    readme.write_text("# Test Repository\n")

    # Commit it
    run_command(["git", "add", "README.md"], cwd=git_repo)
    run_command(["git", "commit", "-m", "Initial commit"], cwd=git_repo)

    return git_repo
```

### Pattern 5: Comparison Utilities

**What:** Functions for exact and semantic output comparison.

**When to use:** All output assertions.

**Example:**
```python
# Source: Python difflib documentation
import difflib
import re

def compare_exact(expected: str, actual: str) -> bool:
    """Exact string comparison."""
    return expected == actual

def compare_semantic(expected: str, actual: str) -> bool:
    """
    Semantic comparison ignoring:
    - Leading/trailing whitespace per line
    - Multiple consecutive spaces
    - Empty lines
    """
    def normalize(text: str) -> List[str]:
        lines = []
        for line in text.splitlines():
            # Strip leading/trailing whitespace
            line = line.strip()
            # Collapse multiple spaces
            line = re.sub(r'\s+', ' ', line)
            # Skip empty lines
            if line:
                lines.append(line)
        return lines

    return normalize(expected) == normalize(actual)

def diff_lines(expected: str, actual: str) -> str:
    """Generate human-readable diff for assertion messages."""
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile='expected',
        tofile='actual',
    )
    return ''.join(diff)
```

### Pattern 6: Assertion Helpers

**What:** Custom assertions that provide good error messages.

**When to use:** All test comparisons.

**Example:**
```python
def assert_commands_match(
    git_result: CommandResult,
    gitsl_result: CommandResult,
    mode: str = "exact"
) -> None:
    """
    Assert that git and gitsl produced equivalent output.

    Args:
        git_result: Result from running git command
        gitsl_result: Result from running gitsl command
        mode: "exact" or "semantic"
    """
    # Exit codes must always match exactly
    assert git_result.exit_code == gitsl_result.exit_code, (
        f"Exit code mismatch: git={git_result.exit_code}, "
        f"gitsl={gitsl_result.exit_code}"
    )

    # Compare output based on mode
    compare_fn = compare_exact if mode == "exact" else compare_semantic

    if not compare_fn(git_result.stdout, gitsl_result.stdout):
        diff = diff_lines(git_result.stdout, gitsl_result.stdout)
        raise AssertionError(
            f"stdout mismatch ({mode} mode):\n{diff}"
        )
```

### Anti-Patterns to Avoid

- **Not capturing stderr:** Always capture both stdout and stderr. Errors often go to stderr.
- **Using shell=True:** Security risk and hides errors. Use list of args instead.
- **Hardcoding paths:** Always use `tmp_path` or fixtures. Never test in current directory.
- **Ignoring exit codes:** Always compare exit codes. Many tools use non-zero for warnings too.
- **Forgetting git config:** In CI, git commits fail without user.name/user.email configured.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Temp directories | `os.makedirs()` + cleanup | pytest `tmp_path` | Automatic cleanup, unique paths |
| Subprocess output | Manual Popen | `subprocess.run(capture_output=True)` | Simpler, handles encoding |
| Diff generation | Custom line-by-line | `difflib.unified_diff()` | Standard format, edge cases handled |
| String comparison | Manual loop | `difflib.SequenceMatcher` | Similarity scoring if needed |
| Test isolation | Manual chdir | `cwd` parameter to subprocess | No global state changes |

**Key insight:** The stdlib has all the comparison tools needed. External diff libraries add complexity without benefit.

## Common Pitfalls

### Pitfall 1: Git Not Configured in CI

**What goes wrong:** `git commit` fails with "Please tell me who you are" error.

**Why it happens:** CI environments don't have global git config.

**How to avoid:** Configure git in the fixture:
```python
run_command(["git", "config", "user.email", "test@test.com"], cwd=repo)
run_command(["git", "config", "user.name", "Test User"], cwd=repo)
```

**Warning signs:** Tests pass locally, fail in CI.

### Pitfall 2: Subprocess Output Encoding

**What goes wrong:** Bytes instead of strings, encoding errors.

**Why it happens:** Forgetting `text=True` in subprocess.run().

**How to avoid:** Always use `text=True`:
```python
subprocess.run(cmd, capture_output=True, text=True)
```

**Warning signs:** `b'output'` in test failures instead of `'output'`.

### Pitfall 3: Working Directory Pollution

**What goes wrong:** Tests interfere with each other via shared state.

**Why it happens:** Using `os.chdir()` instead of subprocess `cwd` parameter.

**How to avoid:** Never chdir. Pass `cwd=` to all subprocess calls.

**Warning signs:** Tests pass individually, fail when run together.

### Pitfall 4: Trailing Newline Differences

**What goes wrong:** Output "matches" visually but fails assertion.

**Why it happens:** One output has trailing newline, other doesn't.

**How to avoid:** Normalize in semantic comparison or assert on stripped output:
```python
assert git_result.stdout.rstrip() == gitsl_result.stdout.rstrip()
```

**Warning signs:** Diff shows empty line at end.

### Pitfall 5: Non-Deterministic Output

**What goes wrong:** Tests fail intermittently.

**Why it happens:** Timestamps, process IDs, or hashes in output.

**How to avoid:** For human-readable output, use semantic comparison. For commands with timestamps, strip or normalize them:
```python
def strip_timestamps(output: str) -> str:
    """Remove ISO timestamps from output."""
    return re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', output)
```

**Warning signs:** Test passes sometimes, fails other times.

### Pitfall 6: Running gitsl Wrong

**What goes wrong:** Tests import gitsl but don't test the CLI properly.

**Why it happens:** Testing imported functions instead of the actual script.

**How to avoid:** For E2E tests, always run gitsl via subprocess:
```python
def run_gitsl(args: List[str], cwd: Path) -> CommandResult:
    """Run gitsl as subprocess - tests the actual CLI."""
    gitsl_path = Path(__file__).parent.parent / "gitsl.py"
    return run_command(["python", str(gitsl_path)] + args, cwd=cwd)
```

**Warning signs:** Tests pass but actual CLI behaves differently.

## Code Examples

### Complete conftest.py

```python
# Source: pytest fixtures documentation + subprocess patterns
"""
Shared test fixtures for gitsl E2E testing.
"""
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytest


# ============================================================
# RESULT CONTAINER
# ============================================================

@dataclass
class CommandResult:
    """Result of running a command via subprocess."""
    stdout: str
    stderr: str
    exit_code: int

    @property
    def success(self) -> bool:
        return self.exit_code == 0


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> CommandResult:
    """
    Run a command and capture all output.
    """
    # Merge with current environment if custom env provided
    full_env = None
    if env is not None:
        full_env = os.environ.copy()
        full_env.update(env)

    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=full_env,
        capture_output=True,
        text=True,
    )
    return CommandResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )


# ============================================================
# GIT COMMAND HELPERS
# ============================================================

def run_git(args: List[str], cwd: Path, env: Optional[dict] = None) -> CommandResult:
    """Run git command in specified directory."""
    return run_command(["git"] + args, cwd=cwd, env=env)


def run_gitsl(args: List[str], cwd: Path, env: Optional[dict] = None) -> CommandResult:
    """Run gitsl command in specified directory."""
    # Get path to gitsl.py relative to tests directory
    gitsl_path = Path(__file__).parent.parent / "gitsl.py"
    return run_command(["python", str(gitsl_path)] + args, cwd=cwd, env=env)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """
    Create a temporary git repository.

    Configured with test user for commits.
    Automatically cleaned up after test.
    """
    # Initialize repo
    run_git(["init"], cwd=tmp_path)

    # Configure for CI environments
    run_git(["config", "user.email", "test@test.com"], cwd=tmp_path)
    run_git(["config", "user.name", "Test User"], cwd=tmp_path)

    return tmp_path


@pytest.fixture
def git_repo_with_commit(git_repo: Path) -> Path:
    """Git repo with initial commit."""
    readme = git_repo / "README.md"
    readme.write_text("# Test Repository\n")

    run_git(["add", "README.md"], cwd=git_repo)
    run_git(["commit", "-m", "Initial commit"], cwd=git_repo)

    return git_repo


@pytest.fixture
def git_repo_with_changes(git_repo_with_commit: Path) -> Path:
    """Git repo with uncommitted changes."""
    # Modify existing file
    readme = git_repo_with_commit / "README.md"
    readme.write_text("# Test Repository\n\nModified content.\n")

    # Add untracked file
    new_file = git_repo_with_commit / "new_file.txt"
    new_file.write_text("New untracked file\n")

    return git_repo_with_commit


@pytest.fixture
def git_repo_with_branch(git_repo_with_commit: Path) -> Path:
    """Git repo with a feature branch."""
    run_git(["branch", "feature"], cwd=git_repo_with_commit)
    return git_repo_with_commit
```

### Complete Comparison Helpers

```python
# tests/helpers/comparison.py
# Source: Python difflib documentation
"""
Output comparison utilities for E2E testing.
"""
import difflib
import re
from typing import List

from .commands import CommandResult


def normalize_for_semantic(text: str) -> List[str]:
    """
    Normalize text for semantic comparison.

    - Strips leading/trailing whitespace per line
    - Collapses multiple whitespace to single space
    - Removes empty lines
    """
    lines = []
    for line in text.splitlines():
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)
        if line:
            lines.append(line)
    return lines


def compare_exact(expected: str, actual: str) -> bool:
    """Exact string comparison."""
    return expected == actual


def compare_semantic(expected: str, actual: str) -> bool:
    """Compare ignoring whitespace differences."""
    return normalize_for_semantic(expected) == normalize_for_semantic(actual)


def generate_diff(expected: str, actual: str, context_lines: int = 3) -> str:
    """Generate unified diff for error messages."""
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile='expected',
        tofile='actual',
        n=context_lines,
    )
    return ''.join(diff)


def assert_output_match(
    expected: str,
    actual: str,
    mode: str = "exact",
    message: str = "Output mismatch"
) -> None:
    """
    Assert outputs match according to mode.

    Args:
        expected: Expected output
        actual: Actual output
        mode: "exact" or "semantic"
        message: Custom message prefix

    Raises:
        AssertionError with diff on mismatch
    """
    compare_fn = compare_exact if mode == "exact" else compare_semantic

    if not compare_fn(expected, actual):
        diff = generate_diff(expected, actual)
        raise AssertionError(f"{message} ({mode} mode):\n{diff}")


def assert_commands_equal(
    git_result: CommandResult,
    gitsl_result: CommandResult,
    mode: str = "exact"
) -> None:
    """
    Assert git and gitsl produced equivalent results.

    Always compares exit codes exactly.
    Compares stdout using specified mode.
    """
    # Exit codes must match
    assert git_result.exit_code == gitsl_result.exit_code, (
        f"Exit code mismatch: "
        f"git={git_result.exit_code}, gitsl={gitsl_result.exit_code}\n"
        f"git stderr: {git_result.stderr}\n"
        f"gitsl stderr: {gitsl_result.stderr}"
    )

    # Compare stdout
    assert_output_match(
        git_result.stdout,
        gitsl_result.stdout,
        mode=mode,
        message="stdout mismatch"
    )
```

### Example Test File

```python
# tests/test_harness.py
"""
Tests for the test harness itself.

Validates that fixtures and helpers work correctly before
using them to test gitsl.
"""
from pathlib import Path

import pytest

from conftest import run_git, run_gitsl, CommandResult


class TestCommandResult:
    """Test CommandResult dataclass."""

    def test_success_property_true(self):
        result = CommandResult(stdout="", stderr="", exit_code=0)
        assert result.success is True

    def test_success_property_false(self):
        result = CommandResult(stdout="", stderr="error", exit_code=1)
        assert result.success is False


class TestRunGit:
    """Test run_git helper."""

    def test_captures_stdout(self, git_repo: Path):
        result = run_git(["status"], cwd=git_repo)
        assert "On branch" in result.stdout

    def test_captures_exit_code_success(self, git_repo: Path):
        result = run_git(["status"], cwd=git_repo)
        assert result.exit_code == 0

    def test_captures_exit_code_failure(self, git_repo: Path):
        result = run_git(["status", "nonexistent"], cwd=git_repo)
        assert result.exit_code != 0


class TestGitRepoFixture:
    """Test git_repo fixture."""

    def test_creates_git_directory(self, git_repo: Path):
        assert (git_repo / ".git").is_dir()

    def test_is_valid_repo(self, git_repo: Path):
        result = run_git(["status"], cwd=git_repo)
        assert result.success


class TestGitRepoWithCommit:
    """Test git_repo_with_commit fixture."""

    def test_has_initial_commit(self, git_repo_with_commit: Path):
        result = run_git(["log", "--oneline"], cwd=git_repo_with_commit)
        assert "Initial commit" in result.stdout

    def test_has_readme(self, git_repo_with_commit: Path):
        readme = git_repo_with_commit / "README.md"
        assert readme.exists()


class TestGitRepoWithChanges:
    """Test git_repo_with_changes fixture."""

    def test_has_modified_file(self, git_repo_with_changes: Path):
        result = run_git(["status", "--porcelain"], cwd=git_repo_with_changes)
        assert " M README.md" in result.stdout

    def test_has_untracked_file(self, git_repo_with_changes: Path):
        result = run_git(["status", "--porcelain"], cwd=git_repo_with_changes)
        assert "?? new_file.txt" in result.stdout
```

## Subprocess vs Import for Testing

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| Subprocess | Tests actual CLI, catches shebang/path issues | Slower, harder to debug | E2E tests (this phase) |
| Import | Faster, direct access to internals | Doesn't test CLI integration | Unit tests (not this phase) |

**Recommendation for Phase 2:** Use subprocess exclusively. This tests the actual user experience. Unit tests via import can be added later for faster development cycles.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `tempfile.mkdtemp()` + manual cleanup | pytest `tmp_path` fixture | pytest 3.9+ | Automatic cleanup |
| `subprocess.Popen()` | `subprocess.run(capture_output=True)` | Python 3.7+ | Simpler API |
| Manual diff loops | `difflib` module | Long-standing | Standardized format |

## Open Questions

1. **Sapling in tests:** Should tests also run real `sl` commands to verify gitsl output matches sl behavior? For Phase 2, stick to git-only. Testing against sl can be added when we have actual command implementations.

2. **Test parallelism:** Should tests run in parallel with pytest-xdist? For Phase 2, not needed. Sequential tests are simpler to debug. Can add later if tests become slow.

3. **Comparison mode per command:** How do we indicate which comparison mode to use per test? Options:
   - Parameter to assertion function (recommended for Phase 2)
   - Pytest marker (can add later if needed)
   - Separate test classes (too rigid)

## Sources

### Primary (HIGH confidence)
- [pytest tmp_path documentation](https://docs.pytest.org/en/stable/how-to/tmp_path.html) - Temp directory fixtures
- [pytest capture documentation](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) - stdout/stderr capture
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - subprocess.run API
- [Python tempfile documentation](https://docs.python.org/3.12/library/tempfile.html) - Temp directory patterns
- [Python difflib documentation](https://docs.python.org/3/library/difflib.html) - Comparison utilities

### Secondary (MEDIUM confidence)
- [pytest fixtures guide](https://betterstack.com/community/guides/testing/pytest-fixtures-guide/) - Fixture organization patterns
- [pytest conftest best practices](https://pytest-with-eric.com/pytest-best-practices/pytest-conftest/) - conftest.py patterns
- [subprocess capture patterns](https://csatlas.com/python-subprocess-run-stdout-stderr/) - subprocess.run examples

### Project Prior Art (HIGH confidence)
- `.planning/research/STACK.md` - Established subprocess patterns for gitsl
- `.planning/phases/01-script-skeleton/01-RESEARCH.md` - DataClass patterns used

## Metadata

**Confidence breakdown:**
- Test structure: HIGH - pytest official documentation
- Subprocess capture: HIGH - Python official documentation
- Fixture patterns: HIGH - pytest official documentation
- Comparison utilities: HIGH - difflib official documentation
- Git repo fixtures: HIGH - standard pytest patterns

**Research date:** 2026-01-18
**Valid until:** 90 days (stable pytest and stdlib patterns)
