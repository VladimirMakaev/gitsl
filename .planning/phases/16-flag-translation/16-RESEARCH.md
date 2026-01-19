# Phase 16: Flag Translation Commands - Research

**Researched:** 2026-01-19
**Domain:** Git-to-Sapling command translation for clean, config, switch
**Confidence:** HIGH

## Summary

Phase 16 implements three git commands that require meaningful flag translation rather than simple passthrough. Unlike Phase 15's direct mappings, these commands have semantic differences between git and Sapling that require careful handling:

- `git clean` -> `sl purge` (different command name, different safety model)
- `git config` -> `sl config` (same name, different flag syntax)
- `git switch` -> `sl goto` or `sl bookmark` (different command based on intent)

The key challenge is that `git clean` requires `-f` (force) for destructive operations by default, while `sl purge` does NOT require any force flag. This creates a safety concern that must be addressed: gitsl should enforce the `-f` or `-n` requirement before executing sl purge to prevent accidental data loss.

All three commands follow the established `cmd_*.py` handler pattern from Phase 15, but with flag transformation logic in addition to command name mapping.

**Primary recommendation:** Create three handler files (`cmd_clean.py`, `cmd_config.py`, `cmd_switch.py`) that translate flags appropriately. The clean handler MUST validate that `-f` or `-n` is present before executing sl purge, mimicking git's safety behavior.

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
├── cmd_*.py           # Existing handlers (14 total after Phase 15)
└── tests/
    ├── conftest.py    # Fixtures: git_repo, sl_repo, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # Comparison helpers
    └── test_*.py      # E2E tests
```

### Pattern 1: Safety Validation Before Passthrough
**What:** Validate required flags before executing destructive command
**When to use:** For git clean (requires -f or -n before executing sl purge)
**Example:**
```python
# cmd_clean.py
"""Handler for 'git clean' command."""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clean' command.

    SAFETY: git clean requires -f (force) or -n (dry-run) to run.
    sl purge does NOT require this - it just runs.
    We enforce git's safety model: reject without -f or -n.
    """
    args = parsed.args

    # Check for force or dry-run flags (git's safety requirement)
    has_force = '-f' in args or '--force' in args
    has_dry_run = '-n' in args or '--dry-run' in args

    if not has_force and not has_dry_run:
        print("fatal: clean.requireForce is true and -f not given: refusing to clean",
              file=sys.stderr)
        return 128

    # Build sl purge command
    sl_args = ["purge"]

    # Handle dry-run: git clean -n -> sl purge --print
    if has_dry_run:
        sl_args.append("--print")
        # Filter out -n/--dry-run from args
        args = [a for a in args if a not in ('-n', '--dry-run')]

    # Handle directories: git clean -d -> sl purge --dirs
    if '-d' in args:
        sl_args.append("--dirs")
        args = [a for a in args if a != '-d']

    # Filter out -f/--force (not needed by sl purge)
    args = [a for a in args if a not in ('-f', '--force')]

    return run_sl(sl_args + args)
```

### Pattern 2: Flag Syntax Translation
**What:** Translate git flag syntax to sl equivalent
**When to use:** For git config (--list vs no flag, read vs set based on args)
**Example:**
```python
# cmd_config.py
"""Handler for 'git config' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git config' command.

    Translations:
    - git config <key>          -> sl config <key>
    - git config <key> <value>  -> sl config --local <key> <value>
    - git config --list         -> sl config
    """
    args = parsed.args

    # git config --list -> sl config (no args)
    if '--list' in args or '-l' in args:
        filtered = [a for a in args if a not in ('--list', '-l')]
        return run_sl(["config"] + filtered)

    # Check if setting a value (has both key and value)
    # Filter out scope flags first
    scope_flags = ('--global', '--local', '--system', '--file')
    non_scope_args = [a for a in args if not a.startswith(scope_flags)]

    if len(non_scope_args) >= 2:
        # Setting a value: git config key value -> sl config --local key value
        # Check if --local, --global, or --system already specified
        has_scope = any(a in args for a in ('--global', '--local', '--system'))
        if not has_scope:
            # Default to --local for writes (git's default for repo)
            return run_sl(["config", "--local"] + args)

    return run_sl(["config"] + args)
```

### Pattern 3: Intent-Based Command Selection
**What:** Choose different sl commands based on git flag
**When to use:** For git switch (-c creates bookmark, no flag goes to existing)
**Example:**
```python
# cmd_switch.py
"""Handler for 'git switch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git switch' command.

    Translations:
    - git switch <branch>      -> sl goto <bookmark>
    - git switch -c <name>     -> sl bookmark <name>
    """
    args = parsed.args

    # git switch -c <name> -> sl bookmark <name>
    if '-c' in args or '--create' in args:
        # Find the -c flag and get the name after it
        filtered = []
        skip_next = False
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if arg in ('-c', '--create'):
                skip_next = True
                # Next arg is the new branch name
                if i + 1 < len(args):
                    branch_name = args[i + 1]
                    return run_sl(["bookmark", branch_name])
            else:
                filtered.append(arg)
        # Fallback if no name found
        return run_sl(["bookmark"] + filtered)

    # Standard switch -> goto
    return run_sl(["goto"] + args)
```

### Anti-Patterns to Avoid
- **Passing through without safety check:** NEVER pass git clean to sl purge without verifying -f or -n
- **Assuming write scope:** git config writes default to local repo, sl config needs explicit --local
- **Conflating switch -c with goto -B:** They have different semantics

## Command Mappings Analysis

### CLEAN-01, CLEAN-02, CLEAN-03: git clean -> sl purge

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git clean` | `sl purge` / `sl clean` | Name change |
| Force flag | Required (-f) unless clean.requireForce=false | Not required | SAFETY ISSUE |
| Dry-run | -n/--dry-run | --print | Flag translation |
| Directories | -d (needed for untracked dirs) | --dirs (for empty dirs only) | Different semantics |
| Exit code | 128 if no -f | 0 on success | Must emulate |

**Flag compatibility (verified via CLI):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -f, --force | Not needed | sl purge just runs |
| -n, --dry-run | --print, -p | Different flag name |
| -d | --dirs | Different semantics - git removes untracked dirs, sl removes empty dirs |
| -x | --ignored | Remove ignored files too |
| -X | N/A | Remove ONLY ignored (not supported directly) |
| -e <pattern> | -X, --exclude | Same purpose |
| -i | N/A | Interactive mode (not supported) |

**CRITICAL SAFETY CONSIDERATION:**
Git clean requires `-f` by default to prevent accidental deletion. Sapling purge has no such protection. The gitsl handler MUST:
1. Check for `-f` or `-n` flag
2. Return exit code 128 with error message if neither present
3. Only then execute sl purge

**Implementation:** Safety validation + flag translation.

### CONFIG-01, CONFIG-02, CONFIG-03: git config -> sl config

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git config` | `sl config` | YES - direct |
| Read | `git config <key>` | `sl config <key>` | YES |
| Write | `git config <key> <value>` | `sl config --local <key> <value>` | Needs --local |
| List | `git config --list` | `sl config` (no args) | Flag translation |
| Exit code | 0 on success, 1 if not found | 0 on success | Compatible |

**Flag compatibility (verified via CLI):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| --list, -l | (no args) | sl config with no args lists all |
| --global | --user | Different flag name |
| --local | --local | Same flag |
| --system | --system | Same flag |
| --get | N/A | sl config <key> just gets |
| --unset | --delete | Same purpose, different flag |

**Implementation:** Flag translation with scope handling.

### SWITCH-01, SWITCH-02: git switch -> sl goto/bookmark

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Switch | `git switch <branch>` | `sl goto <bookmark>` | Command change |
| Create | `git switch -c <name>` | `sl bookmark <name>` | Different command |
| Force create | `git switch -C <name>` | `sl bookmark -f <name>` | Need -f flag |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via CLI):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -c, --create | sl bookmark <name> | Different command entirely |
| -C, --force-create | sl bookmark -f <name> | Need to add -f |
| --detach | sl goto <commit> | Just goto works for detached |

**Note on git switch vs sl goto:**
- `sl goto` is for navigation to a commit/bookmark
- `sl bookmark` creates a new bookmark at current commit
- `git switch -c` creates AND switches to new branch
- For `git switch -c <name>`, we create bookmark first, which is already at current commit

**Implementation:** Intent-based command selection.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Safety validation | Custom file deletion check | Simple flag check | git uses flag check only |
| Command dispatch | Manual if/elif in main | Separate cmd_*.py files | ARCH-03 compliance |
| Subprocess passthrough | Custom pipe handling | run_sl() from common.py | Already tested |
| Exit code propagation | Custom error handling | Return subprocess returncode | Established pattern |
| Test fixtures | Manual repo setup | sl_repo fixtures from conftest.py | Already available |

**Key insight:** The "flag translation" is light logic, not complex transformation. Keep handlers simple.

## Common Pitfalls

### Pitfall 1: Skipping Clean Safety Check
**What goes wrong:** Users accidentally delete files without -f flag
**Why it happens:** sl purge doesn't require -f, so passthrough works but isn't safe
**How to avoid:** ALWAYS validate -f or -n before calling sl purge
**Warning signs:** Files deleted without user explicitly using -f
**Exit code:** Must return 128 (git's exit code for this error)

### Pitfall 2: Config Write Without Scope
**What goes wrong:** sl config may not write to expected location
**Why it happens:** git config defaults to local, sl config may need explicit flag
**How to avoid:** Add --local for writes when no scope specified
**Warning signs:** Config values not persisting or going to wrong file

### Pitfall 3: Switch -c Without Bookmark Creation
**What goes wrong:** User expects to be on new branch but isn't
**Why it happens:** sl goto doesn't create bookmarks
**How to avoid:** Use sl bookmark for -c flag, not sl goto
**Warning signs:** Bookmark not found errors after switch -c

### Pitfall 4: Confusing clean -d Semantics
**What goes wrong:** Users expect -d to remove untracked directories
**Why it happens:** git clean -d removes untracked dirs, sl purge --dirs removes EMPTY dirs
**How to avoid:** Document this difference; sl purge already removes untracked dir contents
**Warning signs:** Empty directories remain after git clean -fd

### Pitfall 5: Testing Without Force Flag
**What goes wrong:** Tests fail because clean rejects without -f
**Why it happens:** Forgetting that gitsl enforces git's safety requirement
**How to avoid:** Always use -f or -n in tests
**Warning signs:** Exit code 128 in tests

## Code Examples

### cmd_clean.py
```python
"""Handler for 'git clean' command."""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clean' command.

    Translations:
    - git clean -f      -> sl purge (force required by gitsl)
    - git clean -fd     -> sl purge (dirs included by default)
    - git clean -n      -> sl purge --print (dry run)

    SAFETY: git requires -f or -n to run. We enforce this.
    """
    args = list(parsed.args)

    # Check for force or dry-run flags (git's safety requirement)
    has_force = '-f' in args or '--force' in args
    has_dry_run = '-n' in args or '--dry-run' in args

    if not has_force and not has_dry_run:
        print("fatal: clean.requireForce is true and -f not given: refusing to clean",
              file=sys.stderr)
        return 128

    sl_args = []

    # Handle dry-run: -n -> --print
    if has_dry_run:
        sl_args.append("--print")
        args = [a for a in args if a not in ('-n', '--dry-run')]

    # Filter out -f/--force (not needed by sl purge)
    args = [a for a in args if a not in ('-f', '--force')]

    # Filter out -d (sl purge includes untracked dirs by default)
    args = [a for a in args if a != '-d']

    return run_sl(["purge"] + sl_args + args)
```

### cmd_config.py
```python
"""Handler for 'git config' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git config' command.

    Translations:
    - git config <key>          -> sl config <key>
    - git config <key> <value>  -> sl config --local <key> <value>
    - git config --list         -> sl config
    """
    args = list(parsed.args)

    # git config --list -> sl config (no args)
    if '--list' in args or '-l' in args:
        args = [a for a in args if a not in ('--list', '-l')]
        return run_sl(["config"] + args)

    # Count positional arguments (non-flag args)
    positional = [a for a in args if not a.startswith('-')]

    # If setting a value (key and value present)
    if len(positional) >= 2:
        # Check if scope already specified
        has_scope = any(a in args for a in ('--global', '--local', '--system', '--user'))
        if not has_scope:
            # Default to --local for writes (git's default)
            return run_sl(["config", "--local"] + args)

    return run_sl(["config"] + args)
```

### cmd_switch.py
```python
"""Handler for 'git switch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git switch' command.

    Translations:
    - git switch <branch>      -> sl goto <bookmark>
    - git switch -c <name>     -> sl bookmark <name>
    """
    args = list(parsed.args)

    # Check for create flag
    if '-c' in args or '--create' in args:
        # Extract branch name after -c
        for i, arg in enumerate(args):
            if arg in ('-c', '--create') and i + 1 < len(args):
                branch_name = args[i + 1]
                return run_sl(["bookmark", branch_name])

    # Standard switch -> goto
    return run_sl(["goto"] + args)
```

### Updated gitsl.py Dispatch
```python
# Add imports at top
import cmd_clean
import cmd_config
import cmd_switch

# In main(), add dispatch cases:
if parsed.command == "clean":
    return cmd_clean.handle(parsed)

if parsed.command == "config":
    return cmd_config.handle(parsed)

if parsed.command == "switch":
    return cmd_switch.handle(parsed)
```

## Test Patterns

### E2E Test for clean
```python
"""E2E tests for git clean command (CLEAN-01, CLEAN-02, CLEAN-03)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clean,
]


class TestCleanForce:
    """CLEAN-01: git clean -f translates to sl purge."""

    def test_clean_removes_untracked(self, sl_repo_with_commit: Path):
        """git clean -f removes untracked files."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        result = run_gitsl(["clean", "-f"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked.exists()

    def test_clean_requires_force(self, sl_repo_with_commit: Path):
        """git clean without -f fails with error."""
        result = run_gitsl(["clean"], cwd=sl_repo_with_commit)
        assert result.exit_code == 128
        assert "refusing to clean" in result.stderr


class TestCleanForceDir:
    """CLEAN-02: git clean -fd translates to sl purge (dirs included)."""

    def test_clean_removes_untracked_dir(self, sl_repo_with_commit: Path):
        """git clean -fd removes untracked directories."""
        # Create untracked directory with file
        untracked_dir = sl_repo_with_commit / "untracked_dir"
        untracked_dir.mkdir()
        (untracked_dir / "file.txt").write_text("content\n")

        result = run_gitsl(["clean", "-fd"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked_dir.exists()


class TestCleanDryRun:
    """CLEAN-03: git clean -n translates to sl purge --print (dry run)."""

    def test_clean_dry_run_shows_files(self, sl_repo_with_commit: Path):
        """git clean -n shows files without removing."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        result = run_gitsl(["clean", "-n"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "untracked.txt" in result.stdout
        # File should still exist
        assert untracked.exists()
```

### E2E Test for config
```python
"""E2E tests for git config command (CONFIG-01, CONFIG-02, CONFIG-03)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.config,
]


class TestConfigRead:
    """CONFIG-01: git config <key> translates to sl config <key>."""

    def test_config_read_value(self, sl_repo: Path):
        """git config reads a config value."""
        # First set a value
        run_command(["sl", "config", "--local", "ui.username", "Test <test@test.com>"],
                    cwd=sl_repo)

        result = run_gitsl(["config", "ui.username"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "Test" in result.stdout


class TestConfigWrite:
    """CONFIG-02: git config <key> <value> translates to sl config."""

    def test_config_write_value(self, sl_repo: Path):
        """git config sets a config value."""
        result = run_gitsl(["config", "test.key", "test-value"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify value was set
        verify = run_command(["sl", "config", "test.key"], cwd=sl_repo)
        assert "test-value" in verify.stdout


class TestConfigList:
    """CONFIG-03: git config --list translates to sl config."""

    def test_config_list(self, sl_repo: Path):
        """git config --list shows all config."""
        result = run_gitsl(["config", "--list"], cwd=sl_repo)
        assert result.exit_code == 0
        # Should have some output (at least system config)
        assert len(result.stdout) > 0
```

### E2E Test for switch
```python
"""E2E tests for git switch command (SWITCH-01, SWITCH-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.switch,
]


class TestSwitchBranch:
    """SWITCH-01: git switch <branch> translates to sl goto <bookmark>."""

    def test_switch_to_bookmark(self, sl_repo_with_commit: Path):
        """git switch changes to existing bookmark."""
        # Create a bookmark
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["switch", "feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestSwitchCreate:
    """SWITCH-02: git switch -c <name> translates to sl bookmark <name>."""

    def test_switch_create_bookmark(self, sl_repo_with_commit: Path):
        """git switch -c creates new bookmark."""
        result = run_gitsl(["switch", "-c", "new-feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was created
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "new-feature" in bookmarks.stdout
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A - new phase | cmd_*.py with flag translation | Building on Phase 15 | Adds flag logic to handlers |

**This phase extends Phase 15 patterns with flag translation logic.** No new architectural decisions needed.

## Open Questions

1. **clean -d semantics difference**
   - What we know: git clean -d removes untracked directories; sl purge --dirs removes empty directories
   - What's unclear: Whether sl purge already removes untracked dir contents (making -d unnecessary)
   - Recommendation: Test shows sl purge removes untracked files INCLUDING those in dirs; -d can be ignored

2. **config --global vs --user**
   - What we know: git uses --global, sl uses --user for user-level config
   - What's unclear: Whether to translate --global to --user
   - Recommendation: For v1.2, pass through as-is; sl may accept --global as alias

3. **switch -C (force create)**
   - What we know: SWITCH-02 only covers -c, not -C
   - What's unclear: Whether to add -C support
   - Recommendation: Document as future enhancement; -c is the core requirement

## Sources

### Primary (HIGH confidence)
- Sapling CLI help: `sl help purge`, `sl help config`, `sl help goto`, `sl help bookmark` - Verified all command flags and behavior via direct CLI testing
- Git manual pages: `git clean --help`, `git config --help`, `git switch --help` - Reference behavior
- Existing codebase: cmd_rm.py, cmd_add.py patterns - Established handler patterns
- Direct CLI testing: Verified sl purge, sl config, sl goto behavior in test repository

### Secondary (MEDIUM confidence)
- STATE.md research notes: "Clean data safety - Phase 16 must enforce -f requirement before passing to sl purge"

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 15, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern with flag logic
- Command mappings: HIGH - Verified via CLI help and direct testing
- Safety model: HIGH - Tested git clean without -f, confirmed 128 exit code

**Research date:** 2026-01-19
**Valid until:** 2026-02-19 (30 days - stable patterns, safety model well-understood)
