# Phase 5: File Operation Commands - Research

**Researched:** 2026-01-18
**Domain:** Git-to-Sapling file staging and commit translation
**Confidence:** HIGH

## Summary

Phase 5 implements three file operation commands: `git add`, `git commit`, and `git add -A`. These are straightforward passthrough commands where git commands map directly to sl equivalents with minimal translation:

- `git add <files>` -> `sl add <files>` (direct passthrough)
- `git commit -m "message"` -> `sl commit -m "message"` (direct passthrough)
- `git add -A` -> `sl addremove` (flag translation required)

The existing infrastructure from Phases 3-4 is well-suited for this work. The `cmd_add.py` handler is the most interesting because it needs to detect `-A` or `--all` flags and translate to `sl addremove`. The `cmd_commit.py` handler is a simple passthrough following the existing pattern.

**Primary recommendation:** Create `cmd_add.py` with special handling for `-A`/`--all` flags (maps to `sl addremove`), and `cmd_commit.py` as a simple passthrough. Both follow the established `handle(ParsedCommand) -> int` interface.

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

**Installation:**
```bash
# No new dependencies - all patterns established in Phases 3-4
```

## Architecture Patterns

### Current Project Structure
```
gitsl/
├── gitsl.py           # Entry point with dispatch
├── common.py          # ParsedCommand, run_sl(), debug helpers
├── cmd_status.py      # Handler for 'git status' -> 'sl status'
├── cmd_log.py         # Handler for 'git log' -> 'sl log'
├── cmd_diff.py        # Handler for 'git diff' -> 'sl diff'
├── cmd_init.py        # Handler for 'git init' -> 'sl init'
├── cmd_rev_parse.py   # Handler for 'git rev-parse' (special)
├── cmd_add.py         # NEW: Handler for 'git add'
├── cmd_commit.py      # NEW: Handler for 'git commit'
└── tests/
    ├── conftest.py    # Fixtures: git_repo, sl_repo, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # assert_commands_equal()
    └── test_*.py
```

### Pattern 1: Simple Command Passthrough
**What:** Command handlers that pass through to sl with same command name
**When to use:** For `git commit` which maps directly to `sl commit`

**Example:**
```python
# cmd_commit.py
"""Handler for 'git commit' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git commit' command.

    Translates to 'sl commit' and passes through all arguments.
    """
    return run_sl(["commit"] + parsed.args)
```

### Pattern 2: Flag Translation Handler
**What:** Handler that detects specific flags and translates to different command
**When to use:** For `git add -A` which must become `sl addremove`

**Example:**
```python
# cmd_add.py
"""Handler for 'git add' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git add' command.

    - git add <files> -> sl add <files>
    - git add -A / git add --all -> sl addremove
    """
    # Check for -A or --all flag
    if "-A" in parsed.args or "--all" in parsed.args:
        # Remove the flag and use addremove instead
        filtered_args = [a for a in parsed.args if a not in ("-A", "--all")]
        return run_sl(["addremove"] + filtered_args)

    # Standard add passthrough
    return run_sl(["add"] + parsed.args)
```

### Pattern 3: Entry Point Dispatch Extension
**What:** Adding new commands to gitsl.py dispatch
**When to use:** For each new command handler

**Current pattern in gitsl.py:**
```python
import cmd_add
import cmd_commit

# In main(), after existing dispatches:
if parsed.command == "add":
    return cmd_add.handle(parsed)

if parsed.command == "commit":
    return cmd_commit.handle(parsed)
```

### Anti-Patterns to Avoid

- **Complex flag parsing when simple detection works:** For `-A`/`--all`, just check if flag is in args list. Don't use argparse or similar.

- **Modifying parsed.args in place:** Create a new filtered list rather than mutating the original.

- **Forgetting to import handlers in gitsl.py:** Each new cmd_*.py needs an import statement in gitsl.py.

## Command Mappings Analysis

### CMD-02: git add <files> -> sl add <files>

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git add file.txt` | `sl add file.txt` | YES - direct |
| Multiple files | `git add a.txt b.txt` | `sl add a.txt b.txt` | YES |
| All files (no arg) | Not standard | `sl add` (adds all) | Different semantics |
| Exit code 0 | Success | Success | YES |
| Exit code != 0 | File not found: 128 | File not found: 1 | Different codes, both non-zero |
| Already tracked | No-op, exit 0 | Prints warning, exit 0 | YES |

**Semantic difference:** `sl add` with no arguments adds all untracked files. `git add` with no arguments is an error. However, for this phase, we're only implementing `git add <files>` (with explicit files) per CMD-02.

**Implementation:** Passthrough with `run_sl(["add"] + parsed.args)`.

### CMD-03: git commit -m "message" -> sl commit -m "message"

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git commit -m "msg"` | `sl commit -m "msg"` | YES - direct |
| Exit code 0 | Commit created | Commit created | YES |
| Exit code 1 | Nothing to commit | Nothing changed | YES |
| Message flag | `-m "message"` | `-m "message"` | YES |
| Multiple -m | Supported | Supported | YES |

**Verified output comparison:**
```
# git commit -m "test"
[master abc1234] test
 1 file changed, 1 insertion(+)

# sl commit -m "test"
(no output on success, only if interactive)
```

**Implementation:** Passthrough with `run_sl(["commit"] + parsed.args)`.

### CMD-08: git add -A -> sl addremove

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git add -A` | `sl addremove` | Requires translation |
| Command | `git add --all` | `sl addremove` | Requires translation |
| Behavior | Stage all changes | Stage all changes | YES |
| New files | Tracked | Added | YES |
| Deleted files | Removed from index | Removed | YES |
| Modified files | Staged | Already tracked | YES |
| Exit code 0 | Success | Success | YES |

**Key insight:** `git add -A` (or `--all`) stages ALL changes: new files, modified files, and deleted files. Sapling's `sl addremove` does the same: adds new files and removes deleted files. Modified files are already tracked in both systems.

**Implementation:** Detect `-A` or `--all` in args, translate to `sl addremove`.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Command execution | Custom subprocess handling | run_sl() from common.py | Already tested, handles passthrough |
| Flag parsing | argparse, getopt | Simple `in` check | Only need to detect presence, not parse values |
| Test fixtures | Manual repo setup | sl_repo fixtures from conftest.py | Already available, tested |

**Key insight:** Flag detection for `-A`/`--all` is trivial. Don't over-engineer with a parsing library.

## Common Pitfalls

### Pitfall 1: Treating `-A` as Requiring Passthrough
**What goes wrong:** `git add -A` passes `-A` to `sl add`, which doesn't understand it
**Why it happens:** Assuming all flags pass through
**How to avoid:** Check for `-A`/`--all` and translate to `sl addremove`
**Warning signs:** Error from sl about unknown option

### Pitfall 2: Forgetting --all Variant
**What goes wrong:** `git add --all` not handled, only `-A`
**Why it happens:** Checking only short flag form
**How to avoid:** Check for both `-A` and `--all` in args
**Warning signs:** E2E tests with `--all` fail

### Pitfall 3: Not Filtering -A from Args
**What goes wrong:** `sl addremove -A` is called, which is invalid
**Why it happens:** Forgetting to remove the flag after translation
**How to avoid:** Filter out `-A`/`--all` when using addremove
**Warning signs:** Error from sl about unknown option

### Pitfall 4: Testing with git_repo Instead of sl_repo
**What goes wrong:** Tests pass but don't verify actual sl behavior
**Why it happens:** Using git_repo fixture which creates .git/ not .hg/
**How to avoid:** Use sl_repo fixtures for testing gitsl add/commit
**Warning signs:** "not inside a repository" errors

### Pitfall 5: Not Handling Exit Codes
**What goes wrong:** Exit codes not propagated correctly
**Why it happens:** Forgetting to return run_sl() result
**How to avoid:** Always `return run_sl([...])`, never just call it
**Warning signs:** Exit code always 0 regardless of sl result

## Test Patterns

### E2E Test Pattern for git add
```python
# test_cmd_add.py
"""E2E tests for git add command."""

import shutil
import pytest
from pathlib import Path
from conftest import run_gitsl, run_command

sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestAddBasic:
    """CMD-02: git add <files> translates to sl add <files>."""

    def test_add_new_file_succeeds(self, sl_repo: Path):
        """git add stages a new file."""
        # Create a new file
        new_file = sl_repo / "test.txt"
        new_file.write_text("test content\n")

        # Add via gitsl
        result = run_gitsl(["add", "test.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl status
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A test.txt" in status.stdout

    def test_add_multiple_files(self, sl_repo: Path):
        """git add can stage multiple files at once."""
        (sl_repo / "a.txt").write_text("a\n")
        (sl_repo / "b.txt").write_text("b\n")

        result = run_gitsl(["add", "a.txt", "b.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A a.txt" in status.stdout
        assert "A b.txt" in status.stdout


class TestAddAll:
    """CMD-08: git add -A translates to sl addremove."""

    def test_add_all_stages_new_files(self, sl_repo_with_commit: Path):
        """git add -A stages new untracked files."""
        (sl_repo_with_commit / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "-A"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "A new.txt" in status.stdout

    def test_add_all_long_form(self, sl_repo_with_commit: Path):
        """git add --all works the same as -A."""
        (sl_repo_with_commit / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "--all"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
```

### E2E Test Pattern for git commit
```python
# test_cmd_commit.py
"""E2E tests for git commit command."""

import shutil
import pytest
from pathlib import Path
from conftest import run_gitsl, run_command

sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestCommitBasic:
    """CMD-03: git commit -m translates to sl commit -m."""

    def test_commit_with_message_succeeds(self, sl_repo: Path):
        """git commit -m creates a commit with the message."""
        # Create and add a file
        (sl_repo / "test.txt").write_text("test\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        # Commit via gitsl
        result = run_gitsl(["commit", "-m", "Test commit"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify commit exists with correct message
        log = run_command(["sl", "log", "--limit", "1"], cwd=sl_repo)
        assert "Test commit" in log.stdout

    def test_commit_nothing_returns_nonzero(self, sl_repo_with_commit: Path):
        """git commit with nothing staged returns non-zero."""
        result = run_gitsl(["commit", "-m", "Empty"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0


class TestWorkflow:
    """Integration: add -> commit -> status shows clean."""

    def test_add_commit_workflow(self, sl_repo: Path):
        """Full add -> commit workflow results in clean status."""
        # Create file
        (sl_repo / "file.txt").write_text("content\n")

        # Add
        add_result = run_gitsl(["add", "file.txt"], cwd=sl_repo)
        assert add_result.exit_code == 0

        # Commit
        commit_result = run_gitsl(["commit", "-m", "Add file"], cwd=sl_repo)
        assert commit_result.exit_code == 0

        # Status should be clean
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert status.stdout.strip() == ""
```

## Code Examples

### Complete Handler: cmd_add.py
```python
"""Handler for 'git add' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git add' command.

    Translations:
    - git add <files>  -> sl add <files>
    - git add -A       -> sl addremove
    - git add --all    -> sl addremove
    """
    # Check for -A or --all flag -> translate to addremove
    if "-A" in parsed.args or "--all" in parsed.args:
        # Filter out the -A/--all flag
        filtered_args = [a for a in parsed.args if a not in ("-A", "--all")]
        return run_sl(["addremove"] + filtered_args)

    # Standard add passthrough
    return run_sl(["add"] + parsed.args)
```

### Complete Handler: cmd_commit.py
```python
"""Handler for 'git commit' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git commit' command.

    Translates to 'sl commit' and passes through all arguments.
    """
    return run_sl(["commit"] + parsed.args)
```

### Updated gitsl.py Dispatch Section
```python
import cmd_status
import cmd_log
import cmd_diff
import cmd_init
import cmd_rev_parse
import cmd_add      # NEW
import cmd_commit   # NEW

# In main(), add to dispatch:
if parsed.command == "add":
    return cmd_add.handle(parsed)

if parsed.command == "commit":
    return cmd_commit.handle(parsed)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A | Established in Phases 3-4 | 2026-01-18 | Foundation for all command handlers |

**This is a green field build.** No legacy patterns to replace.

## Open Questions

1. **git add . Behavior**
   - What we know: `sl add` with no args adds all files, `git add .` adds all in current dir
   - What's unclear: Whether to support `git add .` in Phase 5
   - Recommendation: Defer - CMD-02 specifies `git add <files>`, not directory patterns

2. **Other add flags (-u, -p, etc.)**
   - What we know: git add has many flags (-u, -p, -i, etc.)
   - What's unclear: Which are supported by sl add
   - Recommendation: Defer - Phase 5 scope is explicit file adds and -A only

3. **commit flags beyond -m**
   - What we know: git commit has many flags (-a, --amend, etc.)
   - What's unclear: Which map to sl commit
   - Recommendation: Passthrough all for now - sl commit is quite compatible

## Sources

### Primary (HIGH confidence)
- Existing codebase: gitsl.py, common.py, cmd_status.py - Actual implementation patterns
- Existing tests: conftest.py, test_execution.py - E2E test patterns, sl_repo fixtures
- Direct CLI testing: Verified git/sl command behavior in /tmp test repos
- sl help output: `sl help add`, `sl help commit`, `sl help addremove`

### Secondary (MEDIUM confidence)
- git manpages: `git add --help`, `git commit --help`

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phases 3-4, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern exactly
- Command mappings: HIGH - Verified with actual CLI testing
- Pitfalls: HIGH - Based on actual codebase analysis and command testing

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable patterns, no external API changes expected)
