# Phase 4: Direct Command Mappings - Research

**Researched:** 2026-01-18
**Domain:** Git-to-Sapling command translation, CLI passthrough patterns
**Confidence:** HIGH

## Summary

Phase 4 extends the execution pipeline from Phase 3 to support five direct command mappings where git commands translate to sl equivalents. Four of these (status, log, diff, init) are straightforward 1:1 command name translations with argument passthrough. One (rev-parse --short HEAD to whereami) requires special handling because output formats differ.

The existing infrastructure from Phase 3 is well-suited for this work:
- `cmd_status.py` serves as the template for all new handlers
- `run_sl()` in `common.py` handles subprocess execution with passthrough
- E2E test infrastructure from Phase 2 provides all needed fixtures

**Primary recommendation:** Create `cmd_log.py`, `cmd_diff.py`, `cmd_init.py`, and `cmd_rev_parse.py` following the exact pattern established in `cmd_status.py`. For `rev-parse --short HEAD`, output truncation is needed (sl whereami returns 40 chars, git returns 7). Update gitsl.py dispatch to route to these handlers.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already established in common.py |
| sys | stdlib | Exit codes, stdout writing | Already in use |
| typing | stdlib | Type hints | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| dataclasses | stdlib | ParsedCommand | Already defined in common.py |
| shlex | stdlib | Debug output formatting | Already in common.py |

**Installation:**
```bash
# No new dependencies - all patterns established in Phase 3
```

## Architecture Patterns

### Current Project Structure
```
gitsl/
├── gitsl.py           # Entry point with dispatch
├── common.py          # ParsedCommand, run_sl(), debug helpers
├── cmd_status.py      # Handler for 'git status' -> 'sl status'
└── tests/
    ├── conftest.py    # Fixtures: git_repo, git_repo_with_commit, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # assert_commands_equal()
    ├── test_harness.py
    └── test_execution.py
```

### Pattern 1: Simple Command Handler
**What:** Command handlers that pass through to sl with same command name
**When to use:** For CMD-01, CMD-04, CMD-05, CMD-06 (status, log, diff, init)

**Example:**
```python
# cmd_log.py - follows exact pattern from cmd_status.py
"""Handler for 'git log' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translates to 'sl log' and passes through all arguments.
    """
    return run_sl(["log"] + parsed.args)
```

### Pattern 2: Entry Point Dispatch Extension
**What:** Adding new commands to gitsl.py dispatch
**When to use:** For each new command handler

**Current pattern in gitsl.py:**
```python
# Dispatch to command handlers
if parsed.command == "status":
    return cmd_status.handle(parsed)

# Extend with new commands:
if parsed.command == "log":
    return cmd_log.handle(parsed)
if parsed.command == "diff":
    return cmd_diff.handle(parsed)
if parsed.command == "init":
    return cmd_init.handle(parsed)
if parsed.command == "rev-parse":
    return cmd_rev_parse.handle(parsed)
```

### Pattern 3: Output-Transforming Handler (rev-parse)
**What:** Handler that needs to modify sl output before returning
**When to use:** For CMD-07 where sl whereami output needs truncation

**Example:**
```python
# cmd_rev_parse.py
"""Handler for 'git rev-parse' command."""

import subprocess
import sys
from common import ParsedCommand


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rev-parse' command.

    Special case: --short HEAD translates to 'sl whereami' with output truncation.
    """
    # Check for --short HEAD pattern
    if "--short" in parsed.args and "HEAD" in parsed.args:
        # sl whereami outputs 40-char hash, git rev-parse --short outputs 7
        result = subprocess.run(
            ["sl", "whereami"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Truncate to 7 chars like git rev-parse --short
            short_hash = result.stdout.strip()[:7]
            print(short_hash)
        else:
            # Pass through error
            sys.stderr.write(result.stderr)
        return result.returncode

    # Other rev-parse variants - fall through to passthrough or error
    # For now, only --short HEAD is implemented
    sys.stderr.write("gitsl: rev-parse only supports --short HEAD\n")
    return 1
```

### Anti-Patterns to Avoid

- **Different handler interfaces:** All handlers must follow `handle(parsed: ParsedCommand) -> int`. Don't create handlers with different signatures.

- **Capturing output when passthrough works:** Only use capture_output for rev-parse where we need to transform output. Use run_sl() passthrough for log, diff, init, status.

- **Duplicating run_sl() logic:** Don't copy subprocess.run() patterns into handlers. Use `run_sl()` from common.py.

- **Forgetting to import handlers in gitsl.py:** Each new cmd_*.py needs an import statement in gitsl.py.

## Command Mappings Analysis

### CMD-01: git status -> sl status

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git status` | `sl status` | YES - direct |
| Exit code 0 | Clean working tree | Clean working tree | YES |
| Exit code != 0 | Not a repo, error | Not a repo, error | YES |
| Output format | Verbose by default | Verbose by default | Different but acceptable |
| Flags | --porcelain, --short, etc. | --porcelain, --short, etc. | Partially - Phase 6 |

**Implementation:** Already done in cmd_status.py. Passthrough with run_sl().

### CMD-04: git log -> sl log

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git log` | `sl log` | YES - direct |
| Default format | commit/author/date/message | changeset/user/date/summary | Different but acceptable |
| Exit code | 0 on success | 0 on success | YES |
| Common flags | --oneline, -n, --graph | --oneline (via template), -l, --graph | Partially - Phase 7 |

**Implementation:** Passthrough with run_sl(["log"] + parsed.args).

### CMD-05: git diff -> sl diff

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git diff` | `sl diff` | YES - direct |
| Default behavior | Working tree vs index | Working tree vs parent | Slightly different semantics |
| Output format | Unified diff | Unified diff | Nearly identical |
| Exit code | 0 (always, by default) | 0 (always, by default) | YES |
| Flags | --cached, --staged, etc. | --change, etc. | Different - out of scope |

**Output comparison (from research):**
```
# git diff output:
diff --git a/README.md b/README.md
index 9daeafb..6ef215e 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@

# sl diff output:
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,1 +1,2 @@
```

Minor differences: git shows index hash, sl shows line count format differently.

**Implementation:** Passthrough with run_sl(["diff"] + parsed.args).

### CMD-06: git init -> sl init

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git init` | `sl init` | YES - direct |
| Creates | .git/ directory | .hg/ directory | Different but expected |
| Exit code | 0 on success | 0 on success | YES |
| Default branch | master (with hint) | master (with hint) | YES |
| Verbose output | "Initialized empty Git repository" | (silent on success) | Different |

**Implementation:** Passthrough with run_sl(["init"] + parsed.args).

### CMD-07: git rev-parse --short HEAD -> sl whereami

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git rev-parse --short HEAD` | `sl whereami` | Requires translation |
| Output | 7-char hash | 40-char hash | NEED TRUNCATION |
| Newline | Includes trailing \n | Includes trailing \n | YES |
| Exit code | 0 on success | 0 on success | YES |
| Error case | 128 if not a repo | Non-zero if not a repo | Compatible |

**Output comparison:**
```
# git rev-parse --short HEAD
82f27e0

# sl whereami (raw)
2fed1c0a6732f6f8b36c5204da21adc078838989

# sl whereami | cut -c1-7
2fed1c0
```

**Implementation:** Special handler that captures output and truncates to 7 chars.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Command dispatch | if/elif chains in main() | Separate cmd_*.py files | ARCH-03 compliance, maintainability |
| Subprocess passthrough | Custom pipe handling | run_sl() from common.py | Already tested, handles edge cases |
| Exit code propagation | Custom error handling | Return subprocess returncode | Established pattern |
| Test fixtures | Manual repo setup | git_repo fixtures from conftest.py | DRY, tested |

**Key insight:** Phase 3 established all the infrastructure. Phase 4 is about replicating the cmd_status.py pattern 4 more times, plus one special case for rev-parse.

## Common Pitfalls

### Pitfall 1: Using capture_output When Not Needed
**What goes wrong:** Output appears after command completes instead of streaming
**Why it happens:** Copying rev-parse pattern to log/diff handlers
**How to avoid:** Only use capture_output in cmd_rev_parse.py. All others use run_sl() passthrough.
**Warning signs:** `git log` output appears all at once after completion

### Pitfall 2: Forgetting to Add Import in gitsl.py
**What goes wrong:** Command falls through to STUB handler
**Why it happens:** Creating cmd_*.py but not updating gitsl.py
**How to avoid:** Each new file needs: `import cmd_X` and `if parsed.command == "X": return cmd_X.handle(parsed)`
**Warning signs:** "[STUB] Would process: git log" instead of actual output

### Pitfall 3: Wrong Hash Length for rev-parse
**What goes wrong:** Output doesn't match git behavior
**Why it happens:** Using sl's 12-char short hash or full 40-char hash
**How to avoid:** Explicitly truncate to 7 characters: `hash[:7]`
**Warning signs:** Test comparing git and gitsl rev-parse output fails

### Pitfall 4: Testing Against Wrong Repo Type
**What goes wrong:** Tests pass/fail incorrectly
**Why it happens:** git_repo fixture creates .git/ but sl expects .hg/
**How to avoid:** Use appropriate fixtures - git_repo for testing git commands, create sl_repo fixture if needed for sl commands
**Warning signs:** "not a repository" errors in tests that should pass

### Pitfall 5: Inconsistent Argument Handling
**What goes wrong:** Arguments not passed through correctly
**Why it happens:** Manually constructing argument lists instead of using parsed.args
**How to avoid:** Always use `run_sl([command] + parsed.args)` pattern
**Warning signs:** `git log -5` works but `git log -n 5` doesn't

## Test Patterns

### E2E Test Pattern for Simple Passthrough
```python
# test_cmd_log.py
"""E2E tests for git log command."""

import shutil
import pytest
from conftest import run_gitsl

sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestLogBasic:
    """CMD-04: git log translates to sl log."""

    def test_log_succeeds_in_repo_with_commit(self, git_repo_with_commit):
        """git log in repo with commits returns exit code 0."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        assert result.exit_code == 0

    def test_log_shows_output(self, git_repo_with_commit):
        """git log produces non-empty output."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        # Either stdout or stderr should have content
        assert result.stdout != "" or result.stderr != ""
```

### E2E Test Pattern for Output Transformation
```python
# test_cmd_rev_parse.py
"""E2E tests for git rev-parse command."""

import shutil
import pytest
from conftest import run_gitsl, run_git

sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestRevParseShortHead:
    """CMD-07: git rev-parse --short HEAD translates to sl whereami."""

    def test_rev_parse_short_head_returns_7_chars(self, git_repo_with_commit):
        """Output is exactly 7 characters (plus newline)."""
        result = run_gitsl(["rev-parse", "--short", "HEAD"], cwd=git_repo_with_commit)
        assert result.exit_code == 0
        # Output should be 7 hex chars + newline
        output = result.stdout.strip()
        assert len(output) == 7
        assert all(c in "0123456789abcdef" for c in output)
```

## Fixture Considerations

The existing test fixtures from Phase 2 use `git init` to create repos. For testing gitsl commands that delegate to sl:

1. **git_repo** creates a .git/ repo via `git init`
2. **sl commands expect .hg/** repo via `sl init`

**Options:**
1. Create parallel sl_repo fixtures for sl-based tests
2. Use git_repo fixtures but accept that sl commands will see "not a repository"
3. Have test assertions be flexible about output

**Recommendation:** For Phase 4 success criteria testing, we may need sl_repo fixtures. However, the existing tests in test_execution.py work because they run gitsl which calls sl, and sl works in the git_repo directory (or fails appropriately in non-repo directories).

Actually, examining test_execution.py more closely: it uses git_repo but calls run_gitsl(["status"]) which internally calls `sl status`. This works because sl can operate in any directory (it just reports no repo found). The tests check exit codes and that output is produced.

For proper E2E testing of command behavior, we need repos that sl recognizes. This may require sl_repo fixtures.

## Code Examples

### Complete Handler: cmd_log.py
```python
"""Handler for 'git log' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translates to 'sl log' and passes through all arguments.
    """
    return run_sl(["log"] + parsed.args)
```

### Complete Handler: cmd_diff.py
```python
"""Handler for 'git diff' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git diff' command.

    Translates to 'sl diff' and passes through all arguments.
    """
    return run_sl(["diff"] + parsed.args)
```

### Complete Handler: cmd_init.py
```python
"""Handler for 'git init' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git init' command.

    Translates to 'sl init' and passes through all arguments.
    """
    return run_sl(["init"] + parsed.args)
```

### Complete Handler: cmd_rev_parse.py
```python
"""Handler for 'git rev-parse' command."""

import subprocess
import sys
from common import ParsedCommand


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rev-parse' command.

    Currently only supports: --short HEAD -> sl whereami (truncated)
    """
    # Check for --short HEAD pattern
    if "--short" in parsed.args and "HEAD" in parsed.args:
        result = subprocess.run(
            ["sl", "whereami"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # sl whereami returns 40 chars, git rev-parse --short returns 7
            short_hash = result.stdout.strip()[:7]
            print(short_hash)
        else:
            sys.stderr.write(result.stderr)
        return result.returncode

    # Unsupported rev-parse variants
    sys.stderr.write("gitsl: rev-parse currently only supports --short HEAD\n")
    return 1
```

### Updated gitsl.py Dispatch Section
```python
import cmd_status
import cmd_log
import cmd_diff
import cmd_init
import cmd_rev_parse

# In main():
# Dispatch to command handlers
if parsed.command == "status":
    return cmd_status.handle(parsed)
if parsed.command == "log":
    return cmd_log.handle(parsed)
if parsed.command == "diff":
    return cmd_diff.handle(parsed)
if parsed.command == "init":
    return cmd_init.handle(parsed)
if parsed.command == "rev-parse":
    return cmd_rev_parse.handle(parsed)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A | Established in Phase 3 | 2026-01-18 | Foundation for all command handlers |

**This is a green field build.** No legacy patterns to replace.

## Open Questions

1. **sl_repo Fixture for Testing**
   - What we know: Current fixtures use git init, sl commands need .hg/
   - What's unclear: Whether E2E tests should use sl repos or just verify basic functionality
   - Recommendation: Create sl_repo fixture for proper E2E testing of sl command behavior

2. **rev-parse Argument Order**
   - What we know: `git rev-parse --short HEAD` is the documented pattern
   - What's unclear: Should we also handle `git rev-parse HEAD --short`?
   - Recommendation: Start with documented order only, expand if needed

3. **Output Format Differences**
   - What we know: git and sl have different verbose output for status, log, diff
   - What's unclear: Whether callers rely on specific output format
   - Recommendation: Accept differences for Phase 4, defer exact format matching to later phases

## Sources

### Primary (HIGH confidence)
- Existing codebase: gitsl.py, common.py, cmd_status.py - Actual implementation patterns
- Existing tests: test_execution.py, conftest.py - E2E test patterns
- Direct CLI testing: Compared git and sl command outputs on local system

### Secondary (MEDIUM confidence)
- Sapling help output: `sl whereami --help`, `sl help templates` - Command behavior
- Git documentation: `git rev-parse --help` - Expected behavior

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 3, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern exactly
- Pitfalls: HIGH - Based on actual codebase analysis

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable patterns, no external API changes expected)
