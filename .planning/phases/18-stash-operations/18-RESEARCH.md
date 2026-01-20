# Phase 18: Stash Operations - Research

**Researched:** 2026-01-20
**Domain:** Git-to-Sapling command translation for stash/shelve workflow
**Confidence:** HIGH

## Summary

Phase 18 implements the git stash workflow by translating to Sapling's shelve/unshelve commands. The git stash metaphor (saving work-in-progress temporarily) maps well to Sapling's shelve concept, but with some differences in command syntax and reference handling:

- `git stash` -> `sl shelve` (save pending changes)
- `git stash push` -> `sl shelve` (explicit save)
- `git stash -m "msg"` -> `sl shelve -m "msg"` (save with message)
- `git stash pop` -> `sl unshelve` (apply and remove)
- `git stash apply` -> `sl unshelve --keep` (apply but keep)
- `git stash list` -> `sl shelve --list` (show all shelved changes)
- `git stash drop` -> `sl shelve --delete <name>` (remove without applying)

The key challenge is **stash reference handling**: git uses `stash@{N}` syntax to reference stashes by index, while Sapling uses named shelves (e.g., `default`, `default-01`). For Phase 18 requirements, only operations on the most recent stash are needed, so this gap is manageable. The `git stash drop` command requires special handling because `sl shelve --delete` requires a name argument, while git defaults to the most recent stash.

**Conflict handling** is important: both git stash pop and sl unshelve can result in merge conflicts. When sl unshelve encounters a conflict, it returns exit code 1 and leaves the repo in a conflict state that requires `sl unshelve --continue` or `sl unshelve --abort` to resolve.

**Primary recommendation:** Create a single handler file (`cmd_stash.py`) that implements subcommand dispatch (push/pop/apply/list/drop). For `drop` without arguments, parse `sl shelve --list` output to find the most recent shelve name before deleting.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already established in common.py |
| sys | stdlib | Exit codes, stderr writing | Already in use |
| typing | stdlib | Type hints | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| dataclasses | stdlib | ParsedCommand | Already defined in common.py |
| common.run_sl | local | Subprocess passthrough | All handlers |

### New Helper Needed
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess.run (capture) | stdlib | Capture sl output | For drop to get shelve name |

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
├── cmd_*.py           # Existing handlers (19 total after Phase 17)
└── tests/
    ├── conftest.py    # Fixtures: git_repo, sl_repo, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # Comparison helpers
    └── test_*.py      # E2E tests
```

### Pattern 1: Subcommand Dispatch
**What:** Single handler that dispatches based on first argument
**When to use:** For git stash which has subcommands (push, pop, apply, list, drop)
**Example:**
```python
# cmd_stash.py
"""Handler for 'git stash' command."""

import subprocess
import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git stash' command.

    Translations:
    - git stash           -> sl shelve
    - git stash push      -> sl shelve
    - git stash -m "msg"  -> sl shelve -m "msg"
    - git stash pop       -> sl unshelve
    - git stash apply     -> sl unshelve --keep
    - git stash list      -> sl shelve --list
    - git stash drop      -> sl shelve --delete <most-recent>
    """
    args = list(parsed.args)

    # No subcommand = stash (same as push)
    if not args:
        return run_sl(["shelve"])

    subcommand = args[0]
    subargs = args[1:]

    if subcommand == "push":
        return _handle_push(subargs)

    if subcommand == "pop":
        return _handle_pop(subargs)

    if subcommand == "apply":
        return _handle_apply(subargs)

    if subcommand == "list":
        return _handle_list(subargs)

    if subcommand == "drop":
        return _handle_drop(subargs)

    # Check if first arg is a flag (e.g., -m) - treat as push
    if subcommand.startswith("-"):
        return _handle_push(args)

    # Unknown subcommand - pass through
    return run_sl(["shelve"] + args)
```

### Pattern 2: Capturing Output for State Detection
**What:** Capture sl output to make decisions before executing another command
**When to use:** For git stash drop without arguments (need to find most recent shelve name)
**Example:**
```python
def _get_most_recent_shelve() -> str | None:
    """Get the name of the most recent shelve, or None if no shelves exist."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    # Output format: "name    (age)    message"
    first_line = result.stdout.strip().split('\n')[0]
    # Name is first whitespace-separated token
    shelve_name = first_line.split()[0]
    return shelve_name


def _handle_drop(args: list) -> int:
    """Handle git stash drop -> sl shelve --delete."""
    if args:
        # Specific stash reference provided (e.g., stash@{1})
        # For v1.2, we don't translate stash@{N} syntax
        # Just pass through - sl will error if format wrong
        return run_sl(["shelve", "--delete"] + args)

    # No args: delete most recent
    shelve_name = _get_most_recent_shelve()
    if shelve_name is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    return run_sl(["shelve", "--delete", shelve_name])
```

### Pattern 3: Simple Flag Passthrough
**What:** Pass arguments directly after command name translation
**When to use:** For push/pop/apply/list where flags match or don't require translation
**Example:**
```python
def _handle_push(args: list) -> int:
    """Handle git stash push -> sl shelve."""
    # -m/--message works the same in both
    return run_sl(["shelve"] + args)


def _handle_pop(args: list) -> int:
    """Handle git stash pop -> sl unshelve."""
    # Both pop the most recent by default
    return run_sl(["unshelve"] + args)


def _handle_apply(args: list) -> int:
    """Handle git stash apply -> sl unshelve --keep."""
    return run_sl(["unshelve", "--keep"] + args)


def _handle_list(args: list) -> int:
    """Handle git stash list -> sl shelve --list."""
    return run_sl(["shelve", "--list"] + args)
```

### Anti-Patterns to Avoid
- **Passing stash@{N} syntax to sl:** Sapling uses named shelves, not indexed stashes
- **Ignoring conflict state:** Both pop and apply can fail with conflicts
- **Calling run_sl for state queries:** Use subprocess.run with capture_output for queries
- **Assuming exit codes match:** git returns 1 for "no stashes", sl returns 255

## Command Mappings Analysis

### STASH-01: git stash -> sl shelve

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash` | `sl shelve` | YES - direct |
| Effect | Save dirty state, revert to clean | Same | YES |
| Untracked | Not saved by default | Not saved by default | YES |
| Exit code | 0 on success | 0 on success | YES |
| Output | "Saved working directory..." | "shelved as <name>" | Different text |

**Verified via CLI:**
```
$ sl shelve
shelved as default
1 files updated, 0 files merged, 0 files removed, 0 files unresolved
```

**Implementation:** Direct passthrough after command name change.

### STASH-02: git stash push -> sl shelve

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash push` | `sl shelve` | YES |
| With message | `git stash push -m "msg"` | `sl shelve -m "msg"` | YES |
| With paths | `git stash push -- <path>` | `sl shelve <path>` | Different syntax |
| Exit code | 0 on success | 0 on success | YES |

**Implementation:** Strip "push" subcommand, pass remaining args to shelve.

### STASH-03: git stash -m "msg" -> sl shelve -m "msg"

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Flag | -m, --message | -m, --message | YES - same |
| Position | After stash or push | After shelve | YES |

**Verified via CLI:**
```
$ sl shelve -m "my saved changes"
shelved as default
```

**Implementation:** Pass -m flag through unchanged.

### STASH-04: git stash pop -> sl unshelve

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash pop` | `sl unshelve` | Name change |
| Effect | Apply and remove | Apply and remove | YES |
| Conflict | Apply fails, stash kept | Conflict state, stash kept | Similar |
| Exit code | 0 on success | 0 on success | YES |
| No stash | Exit 1, "No stash entries found." | Exit 255, "no shelved changes..." | Different code |

**Verified via CLI:**
```
$ sl unshelve
unshelving change 'default'
```

**Conflict handling verified:**
```
$ sl unshelve
unshelving change 'default'
rebasing shelved changes
merging test.txt
warning: 1 conflicts while merging test.txt!
unresolved conflicts (see 'sl resolve', then 'sl unshelve --continue')
Exit code: 1
```

**Implementation:** Command name change to unshelve.

### STASH-05: git stash apply -> sl unshelve --keep

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash apply` | `sl unshelve --keep` | Add --keep flag |
| Effect | Apply but keep stash | Apply but keep shelve | YES |
| Flag | (default behavior) | --keep, -k | Need to add |

**Verified via CLI:**
```
$ sl unshelve --keep
unshelving change 'default'
$ sl shelve --list
default    (1s ago)    my saved changes  # Still present
```

**Implementation:** Add --keep flag to unshelve.

### STASH-06: git stash list -> sl shelve --list

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash list` | `sl shelve --list` | Add --list flag |
| Output format | `stash@{0}: WIP on branch: msg` | `name    (age)    message` | Different |
| Empty | No output | No output | YES |
| Exit code | 0 | 0 | YES |

**Git output:**
```
stash@{0}: On master: my custom message
stash@{1}: WIP on master: 032b48f Initial
```

**Sapling output:**
```
default-01      (1s ago)    new shelve
default         (63s ago)   first change
```

**Implementation:** Translate to --list flag. Output format differs but acceptable for v1.2.

### STASH-07: git stash drop -> sl shelve --delete

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git stash drop` | `sl shelve --delete <name>` | NAME REQUIRED |
| No args | Drops stash@{0} | Error! Requires name | MUST HANDLE |
| With ref | `git stash drop stash@{1}` | `sl shelve --delete <name>` | Different syntax |
| No stash | Exit 1, "No stash entries found." | Exit 255, "no shelved changes specified!" | Different |

**sl requires name:**
```
$ sl shelve --delete
abort: no shelved changes specified!
```

**Implementation:** For no-args case, query most recent shelve name first, then delete.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stash storage | Custom temp file system | sl shelve | Already handles bundling |
| Conflict detection | Custom merge check | sl unshelve exit code | Returns 1 on conflict |
| Stash listing | Custom tracking | sl shelve --list | Already formatted |
| Command dispatch | Manual if/elif in main | Separate cmd_*.py files | ARCH-03 compliance |

**Key insight:** The main complexity is the stash drop without arguments case. All other operations are straightforward command/flag translations.

## Common Pitfalls

### Pitfall 1: stash@{N} Reference Syntax
**What goes wrong:** User expects stash@{1} to work
**Why it happens:** Git uses index syntax, Sapling uses named shelves
**How to avoid:** For v1.2, document that named shelves are used; operations on most recent work
**Warning signs:** Error from sl about invalid name
**Exit code:** sl error

### Pitfall 2: Drop Without Arguments
**What goes wrong:** sl shelve --delete fails without name
**Why it happens:** sl requires explicit shelve name, git defaults to most recent
**How to avoid:** Query shelve list, extract most recent name, then delete
**Warning signs:** "no shelved changes specified!" error
**Exit code:** 255 from sl

### Pitfall 3: Conflict on Pop/Apply
**What goes wrong:** Unshelve fails, user stuck in conflict state
**Why it happens:** Shelved changes conflict with current state
**How to avoid:** Document conflict resolution (sl unshelve --continue or --abort)
**Warning signs:** Exit code 1, conflict messages in stderr
**Exit code:** 1

### Pitfall 4: Different Exit Codes for Empty Stash
**What goes wrong:** Scripts expecting git exit code 1 get 255
**Why it happens:** sl uses different error codes
**How to avoid:** For drop, check for empty list before calling sl
**Warning signs:** Unexpected exit codes in tests

### Pitfall 5: Testing Without Initial Commit
**What goes wrong:** Shelve operations fail
**Why it happens:** Can't shelve in empty repository
**How to avoid:** Use sl_repo_with_commit fixture
**Warning signs:** Errors about no commits

## Code Examples

### cmd_stash.py (Complete)
```python
"""Handler for 'git stash' command."""

import subprocess
import sys
from common import ParsedCommand, run_sl


def _get_most_recent_shelve() -> str | None:
    """Get the name of the most recent shelve, or None if no shelves exist."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    # Output format: "name    (age)    message"
    first_line = result.stdout.strip().split('\n')[0]
    # Name is first whitespace-separated token
    shelve_name = first_line.split()[0]
    return shelve_name


def _handle_push(args: list) -> int:
    """Handle git stash push -> sl shelve."""
    return run_sl(["shelve"] + args)


def _handle_pop(args: list) -> int:
    """Handle git stash pop -> sl unshelve."""
    return run_sl(["unshelve"] + args)


def _handle_apply(args: list) -> int:
    """Handle git stash apply -> sl unshelve --keep."""
    return run_sl(["unshelve", "--keep"] + args)


def _handle_list(args: list) -> int:
    """Handle git stash list -> sl shelve --list."""
    return run_sl(["shelve", "--list"] + args)


def _handle_drop(args: list) -> int:
    """
    Handle git stash drop -> sl shelve --delete.

    git stash drop without args deletes most recent.
    sl shelve --delete requires a name.
    """
    if args:
        # Specific stash reference provided
        # For v1.2, pass through - sl may error if format wrong
        return run_sl(["shelve", "--delete"] + args)

    # No args: delete most recent
    shelve_name = _get_most_recent_shelve()
    if shelve_name is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    return run_sl(["shelve", "--delete", shelve_name])


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git stash' command.

    Translations:
    - git stash           -> sl shelve
    - git stash push      -> sl shelve
    - git stash -m "msg"  -> sl shelve -m "msg"
    - git stash pop       -> sl unshelve
    - git stash apply     -> sl unshelve --keep
    - git stash list      -> sl shelve --list
    - git stash drop      -> sl shelve --delete <most-recent>
    """
    args = list(parsed.args)

    # No subcommand = stash (same as push)
    if not args:
        return run_sl(["shelve"])

    subcommand = args[0]
    subargs = args[1:]

    if subcommand == "push":
        return _handle_push(subargs)

    if subcommand == "pop":
        return _handle_pop(subargs)

    if subcommand == "apply":
        return _handle_apply(subargs)

    if subcommand == "list":
        return _handle_list(subargs)

    if subcommand == "drop":
        return _handle_drop(subargs)

    # Check if first arg is a flag (e.g., -m) - treat as push
    if subcommand.startswith("-"):
        return _handle_push(args)

    # Unknown subcommand - pass through to shelve
    return run_sl(["shelve"] + args)
```

### Updated gitsl.py Dispatch
```python
# Add import at top
import cmd_stash

# In main(), add dispatch case:
if parsed.command == "stash":
    return cmd_stash.handle(parsed)
```

## Test Patterns

### E2E Test for stash
```python
"""E2E tests for git stash command (STASH-01 through STASH-07)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.stash,
]


class TestStashBasic:
    """STASH-01: git stash translates to sl shelve."""

    def test_stash_saves_changes(self, sl_repo_with_commit: Path):
        """git stash saves pending changes."""
        # Create a modification
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        # Verify dirty state
        status_before = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status_before.stdout

        result = run_gitsl(["stash"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify clean state
        status_after = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status_after.stdout

        # Verify shelve exists
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" in shelves.stdout


class TestStashPush:
    """STASH-02: git stash push translates to sl shelve."""

    def test_stash_push(self, sl_repo_with_commit: Path):
        """git stash push saves pending changes."""
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        result = run_gitsl(["stash", "push"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status.stdout


class TestStashMessage:
    """STASH-03: git stash -m translates to sl shelve -m."""

    def test_stash_with_message(self, sl_repo_with_commit: Path):
        """git stash -m saves with custom message."""
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        result = run_gitsl(["stash", "-m", "my custom message"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "my custom message" in shelves.stdout


class TestStashPop:
    """STASH-04: git stash pop translates to sl unshelve."""

    def test_stash_pop_restores_and_removes(self, sl_repo_with_commit: Path):
        """git stash pop restores changes and removes stash."""
        # Setup: create and stash changes
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "pop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Changes restored
        assert test_file.read_text() == "modified content\n"

        # Stash removed
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" not in shelves.stdout


class TestStashApply:
    """STASH-05: git stash apply translates to sl unshelve --keep."""

    def test_stash_apply_restores_and_keeps(self, sl_repo_with_commit: Path):
        """git stash apply restores changes but keeps stash."""
        # Setup: create and stash changes
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "apply"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Changes restored
        assert test_file.read_text() == "modified content\n"

        # Stash still exists
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" in shelves.stdout


class TestStashList:
    """STASH-06: git stash list translates to sl shelve --list."""

    def test_stash_list_shows_shelves(self, sl_repo_with_commit: Path):
        """git stash list shows existing stashes."""
        # Create a stash
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve", "-m", "test stash"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "list"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "test stash" in result.stdout


class TestStashDrop:
    """STASH-07: git stash drop translates to sl shelve --delete."""

    def test_stash_drop_removes_most_recent(self, sl_repo_with_commit: Path):
        """git stash drop removes most recent stash."""
        # Create a stash
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "drop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Stash removed
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert shelves.stdout.strip() == ""

    def test_stash_drop_no_stash_error(self, sl_repo_with_commit: Path):
        """git stash drop with no stashes returns error."""
        result = run_gitsl(["stash", "drop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "No stash entries found" in result.stderr
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A - new phase | cmd_stash.py with subcommand dispatch | Building on Phase 17 | Adds subcommand handling |

**Key difference from git:**
- Git: Stashes are indexed (stash@{0}, stash@{1})
- Sapling: Shelves are named (default, default-01, default-02)

For v1.2, operations on "most recent" work correctly. Named access works with shelve names but not git's index syntax.

## Open Questions

1. **stash@{N} syntax translation**
   - What we know: Git uses stash@{0} index syntax; sl uses named shelves
   - What's unclear: Whether to parse and translate index to shelve name
   - Recommendation: For v1.2, document that index syntax is not supported; use most recent

2. **Exit code differences**
   - What we know: git returns 1 for "no stashes"; sl returns 255
   - What's unclear: Whether to normalize exit codes
   - Recommendation: For drop, return git-compatible exit code 1; for others, passthrough

3. **Conflict resolution workflow**
   - What we know: sl unshelve --continue/--abort handles conflicts
   - What's unclear: Whether to document git stash show equivalent
   - Recommendation: Accept sl's workflow; document conflict handling

4. **git stash show command**
   - What we know: Not in Phase 18 requirements (STASH-01 through STASH-07)
   - What's unclear: Whether it's commonly used
   - Recommendation: Document as future enhancement

## Sources

### Primary (HIGH confidence)
- Sapling CLI help: `sl help shelve`, `sl help unshelve` - Verified all flags and behavior
- Git man pages: `git stash --help` - Reference behavior
- Direct CLI testing: Verified shelve, unshelve, --keep, --delete, conflict handling

### Secondary (MEDIUM confidence)
- Phase 17 RESEARCH.md - Established patterns for subcommand handling
- Phase 16 RESEARCH.md - Established patterns for flag translation

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 17, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern with subcommand dispatch
- Command mappings: HIGH - Verified via CLI help and direct testing
- Drop handling: HIGH - Tested that sl requires name, verified parsing approach

**Research date:** 2026-01-20
**Valid until:** 2026-02-20 (30 days - stable patterns, core functionality documented)
