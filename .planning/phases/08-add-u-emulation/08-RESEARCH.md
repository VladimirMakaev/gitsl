# Phase 8: Add -u Emulation - Research

**Researched:** 2026-01-18
**Domain:** Git/Sapling command translation, staging behavior differences
**Confidence:** HIGH

## Summary

This research investigates how to implement `git add -u` (update) functionality using Sapling commands. The key finding is that Sapling and Git have fundamentally different staging models:

1. **Git** requires explicit `git add` for BOTH new files AND modified tracked files
2. **Sapling** auto-includes modified tracked files in commits (like Mercurial) - no explicit staging needed

For `git add -u` specifically:
- Modified tracked files: NO ACTION needed in Sapling (already auto-staged)
- Deleted tracked files: Must run `sl remove --mark <file>` to mark for removal
- Untracked files: IGNORED by -u (this is the key difference from -A)

**Primary recommendation:** Implement `git add -u` by querying `sl status -d -n` to find deleted tracked files, then running `sl remove --mark` on each. Modified files need no action.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already used throughout codebase |
| common.py | local | ParsedCommand, run_sl | Established project pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shlex | stdlib | Command parsing/quoting | For files with spaces if needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual status parsing | sl status -0 | -0 uses null separators for safer parsing with spaces |
| Multiple sl remove calls | Single sl remove --mark <files...> | Single call is more efficient |

**Installation:**
No additional packages needed - uses Python stdlib and existing project modules.

## Architecture Patterns

### Recommended Implementation Location
```
cmd_add.py  # Add -u/-update handling alongside existing -A/--all
```

### Pattern 1: Capture and Process Status Output
**What:** Query sl status to find files needing action, then execute sl commands
**When to use:** When git command semantics differ from sl passthrough
**Example:**
```python
# Source: Pattern from cmd_status.py (capture_output)
import subprocess

def get_deleted_files() -> list:
    """Get list of deleted (missing) tracked files."""
    result = subprocess.run(
        ['sl', 'status', '-d', '-n'],  # -d=deleted, -n=no-status-prefix
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return []
    # Split on newlines, filter empty
    return [f for f in result.stdout.splitlines() if f]
```

### Pattern 2: Conditional Flag Handling
**What:** Check for specific flags and branch to different behaviors
**When to use:** When a single git command has multiple modes
**Example:**
```python
# Source: cmd_add.py existing pattern
def handle(parsed: ParsedCommand) -> int:
    if "-u" in parsed.args or "--update" in parsed.args:
        return handle_update(parsed)
    if "-A" in parsed.args or "--all" in parsed.args:
        return handle_all(parsed)
    # Default behavior
    return run_sl(["add"] + parsed.args)
```

### Anti-Patterns to Avoid
- **Trying to stage modified files:** Sapling auto-stages modified tracked files. Running `sl add` on them returns "already tracked!" message.
- **Using run_sl() for capture:** When you need to process output, use `subprocess.run(capture_output=True)` directly.
- **Parsing status with prefix:** Use `-n` flag to get just filenames, simpler parsing.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finding deleted files | Walking filesystem | `sl status -d -n` | Handles all edge cases |
| Marking deleted for removal | Custom rm tracking | `sl remove --mark` | The --mark flag is designed for this |
| Handling pathspecs | Custom path matching | Pass pathspec to `sl status -d <path>` | Sapling handles pathspec matching |

**Key insight:** Sapling's status command with filtering flags (`-m`, `-d`, `-n`, `-0`) provides all the information needed. Don't reimplement file tracking.

## Common Pitfalls

### Pitfall 1: Assuming Modified Files Need Action
**What goes wrong:** Trying to run `sl add` on modified tracked files
**Why it happens:** Git requires explicit staging of modifications; Sapling doesn't
**How to avoid:** Only act on deleted files (`!` status in sl status)
**Warning signs:** "already tracked!" messages from sl add

### Pitfall 2: Files With Spaces in Names
**What goes wrong:** Parsing `sl status` output breaks when filenames contain spaces
**Why it happens:** Default line parsing assumes no spaces in filename
**How to avoid:** Either:
  - Trust that `sl status -n` output format is unambiguous (status removed, just filename per line)
  - Use `sl status -n -0` for null-separated output if paranoid
**Warning signs:** Tests with "file with spaces.txt" fail

### Pitfall 3: Ignoring Empty Results
**What goes wrong:** Running `sl remove --mark` with no arguments
**Why it happens:** No deleted files to process
**How to avoid:** Check if file list is empty before running sl remove
**Warning signs:** "sl remove: not enough arguments" error

### Pitfall 4: Forgetting Pathspec Support
**What goes wrong:** `git add -u path/` ignores the path and updates all files
**Why it happens:** Not passing pathspec to `sl status` query
**How to avoid:** Pass remaining args (after stripping -u/--update) to sl status
**Warning signs:** E2E tests with subdirectory pathspecs fail

## Code Examples

Verified patterns from official sources:

### Get Deleted Files (sl status -d -n)
```python
# Source: sl help status verification in test environment
import subprocess
from typing import List

def get_deleted_files(pathspec: List[str] = None) -> List[str]:
    """
    Get list of deleted tracked files.

    Args:
        pathspec: Optional list of paths to filter

    Returns:
        List of filenames that are deleted (missing from disk but tracked)
    """
    cmd = ['sl', 'status', '-d', '-n']  # -d=deleted, -n=no-status-prefix
    if pathspec:
        cmd.extend(pathspec)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    return [f for f in result.stdout.splitlines() if f.strip()]
```

### Mark Deleted Files for Removal (sl remove --mark)
```python
# Source: sl help remove verification in test environment
import subprocess
from typing import List

def mark_deleted_for_removal(files: List[str]) -> int:
    """
    Mark already-deleted files for removal in next commit.

    Args:
        files: List of filenames to mark for removal

    Returns:
        Exit code (0 for success)
    """
    if not files:
        return 0  # Nothing to do

    result = subprocess.run(
        ['sl', 'remove', '--mark'] + files
    )
    return result.returncode
```

### Complete git add -u Handler
```python
# Source: Integration of verified patterns
import subprocess
from common import ParsedCommand, run_sl
from typing import List

def handle_update(parsed: ParsedCommand) -> int:
    """
    Handle 'git add -u' (update) command.

    Stages only tracked files:
    - Modified files: No action (Sapling auto-stages)
    - Deleted files: Mark for removal with sl remove --mark

    Does NOT add untracked files.
    """
    # Extract pathspec (remaining args after -u/--update)
    pathspec = [a for a in parsed.args if a not in ('-u', '--update')]

    # Find deleted tracked files
    deleted_files = get_deleted_files(pathspec)

    # Mark deleted files for removal
    if deleted_files:
        result = subprocess.run(['sl', 'remove', '--mark'] + deleted_files)
        return result.returncode

    return 0
```

## Behavior Comparison

### git add -u vs git add -A

| Behavior | git add -u | git add -A |
|----------|-----------|-----------|
| Modified tracked files | Stage | Stage |
| Deleted tracked files | Mark for removal | Mark for removal |
| New untracked files | IGNORE | Add/stage |
| Sapling equivalent | sl remove --mark (for deleted) | sl addremove |

### sl status Flag Reference

| Flag | Description | Output Example |
|------|-------------|----------------|
| -m | Modified files only | `M filename.txt` |
| -d | Deleted (missing) files only | `! filename.txt` |
| -a | Added files only | `A filename.txt` |
| -u | Unknown (untracked) files only | `? filename.txt` |
| -n | No status prefix | `filename.txt` |
| -0 | Null-separated output | `filename.txt\0` |

### Sapling Status Codes

| Code | Meaning | git add -u Action |
|------|---------|-------------------|
| M | Modified | None (auto-staged) |
| A | Added | None (already added) |
| R | Removed | None (already marked) |
| ! | Deleted/Missing | Run `sl remove --mark` |
| ? | Untracked | IGNORE |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual file tracking | sl status with filters | N/A | Use sl's built-in filtering |
| sl forget for removal | sl remove --mark | N/A | --mark is cleaner for already-deleted files |

**Deprecated/outdated:**
- None identified - Sapling's status and remove commands are stable

## Open Questions

Things that couldn't be fully resolved:

1. **Pathspec behavior with -u**
   - What we know: `git add -u subdir/` only affects files in subdir
   - What's verified: `sl status -d subdir/` correctly filters by path
   - Recommendation: Pass pathspec to sl status query, implementation should work

2. **Dry-run support (-n flag)**
   - What we know: git add supports -n/--dry-run
   - What's unclear: Should Phase 8 implement --dry-run for -u?
   - Recommendation: Out of scope for FLAG-03, could be added later

## Test Scenarios

Based on success criteria from phase description:

### Scenario 1: Modified + Untracked
```
Setup:
- tracked.txt (tracked, modified)
- untracked.txt (new, not tracked)

Run: git add -u

Expected:
- tracked.txt: No action needed (Sapling auto-stages)
- untracked.txt: NOT touched (still shows as ?)
```

### Scenario 2: Deleted Tracked File
```
Setup:
- tracked.txt (tracked, deleted from disk)

Run: git add -u

Expected:
- tracked.txt: Marked for removal (R status after)
```

### Scenario 3: Both Modified and Deleted
```
Setup:
- modified.txt (tracked, modified)
- deleted.txt (tracked, deleted from disk)
- untracked.txt (new, not tracked)

Run: git add -u

Expected:
- modified.txt: No action needed
- deleted.txt: Marked for removal
- untracked.txt: NOT touched
```

## Sources

### Primary (HIGH confidence)
- `sl help status` - Output format, flag documentation
- `sl help remove` - The --mark flag for already-deleted files
- `git add --help` - Official -u/--update behavior description
- Local testing in /tmp/gitsl-test and /tmp/git-test

### Secondary (MEDIUM confidence)
- Existing codebase patterns (cmd_status.py, cmd_add.py)

### Tertiary (LOW confidence)
- None - all findings verified locally

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses existing project patterns
- Architecture: HIGH - Pattern follows cmd_status.py capture_output approach
- Behavior mapping: HIGH - Verified with actual sl/git testing
- Pitfalls: HIGH - Identified through actual testing

**Research date:** 2026-01-18
**Valid until:** Indefinite (core VCS behavior, unlikely to change)
