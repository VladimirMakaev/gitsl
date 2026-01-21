# Phase 26: Stash and Checkout/Switch/Restore Flags - Research

**Researched:** 2026-01-21
**Domain:** Git-to-Sapling flag translation for stash, checkout, switch, and restore commands
**Confidence:** HIGH

## Summary

Phase 26 extends the existing stash, checkout, switch, and restore command handlers to support additional flags required for full working tree management. The current implementations handle basic operations but lack support for several commonly-used flags.

The stash command extensions focus on: untracked files (-u), patch mode (-i for sl), show with stats, stash@{n} reference syntax, keep-index warnings, all files including ignored (-a), quiet mode, selective file stashing, and stash branch creation. Most flags have direct sl shelve equivalents.

The switch/checkout extensions add: force creation with -C, force/discard changes with -f, merge with -m, and detach mode. The restore extensions add: source revision, staged warning, quiet mode, and worktree flag handling.

**Primary recommendation:** Extend existing handlers following the established flag extraction pattern from cmd_branch.py and cmd_commit.py. Use warnings for semantic mismatches (keep-index, staged). Implement stash@{n} reference translation via shelve list parsing.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Run sl commands, capture output | Already in cmd_stash.py |
| sys | stdlib | stderr output, exit codes | Standard I/O handling |
| typing | stdlib | Type hints | Function signatures |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| os | stdlib | Check file existence | Disambiguation logic |
| common.run_sl | local | Subprocess passthrough | All handlers |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom stash@{n} parsing | Pass through to sl | Custom gives better git compat |

**Installation:**
No additional dependencies required - uses stdlib only.

## Architecture Patterns

### Recommended Project Structure
```
gitsl/
+-- cmd_stash.py      # Extended with STSH-01 through STSH-10
+-- cmd_checkout.py   # Extended with CHKT-05, CHKT-06
+-- cmd_switch.py     # Extended with CHKT-01, CHKT-02, CHKT-07 through CHKT-09
+-- cmd_restore.py    # Extended with CHKT-03, CHKT-04, CHKT-10, CHKT-11
+-- tests/
    +-- test_stash_flags.py      # New flag tests
    +-- test_checkout_flags.py   # Extended checkout tests
    +-- test_switch_flags.py     # New flag tests
    +-- test_restore_flags.py    # New flag tests
```

### Pattern 1: Flag Extraction with Special Handling
**What:** Extract git flags, translate to sl equivalents, handle edge cases
**When to use:** All flag translation handlers
**Example:**
```python
# Source: cmd_commit.py pattern
def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # Extract flags with their values
    include_untracked = False
    quiet = False
    message = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ('-u', '--include-untracked'):
            include_untracked = True
            i += 1
            continue
        if arg in ('-q', '--quiet'):
            quiet = True
            i += 1
            continue
        if arg in ('-m', '--message'):
            if i + 1 < len(args):
                message = args[i + 1]
                i += 2
                continue
        # ... remaining args
        remaining.append(arg)
        i += 1
```

### Pattern 2: Stash Reference Translation
**What:** Convert git stash@{n} syntax to sl shelve names
**When to use:** For any command accepting stash references (pop, apply, drop, show)
**Example:**
```python
# Source: Analysis of sl shelve --list output
import re

def translate_stash_ref(ref: str) -> Optional[str]:
    """Convert stash@{n} to sl shelve name."""
    match = re.match(r'stash@\{(\d+)\}', ref)
    if not match:
        return ref  # Not stash syntax, pass through

    index = int(match.group(1))

    # Get list of shelves (ordered most recent first)
    result = subprocess.run(
        ["sl", "shelve", "--list", "--template", "{name}\n"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None

    shelves = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
    if index < len(shelves):
        return shelves[index]
    return None  # Index out of range
```

### Pattern 3: Warning for Unsupported Semantics
**What:** Warn user when a flag has no semantic equivalent
**When to use:** For --keep-index, --staged
**Example:**
```python
# Source: cmd_commit.py pattern for --no-verify
if keep_index:
    print("Warning: -k/--keep-index has no effect. "
          "Sapling has no staging area to keep indexed.",
          file=sys.stderr)
```

### Anti-Patterns to Avoid
- **Passing unsupported flags directly:** Always filter or translate flags
- **Ignoring long-form flags:** Handle both `-u` and `--include-untracked`
- **Silent failures:** Warn when a flag cannot be supported

## Git to Sapling Flag Mapping

### Stash Flags (STSH-01 through STSH-10)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| `-u`/`--include-untracked` | `-u` or `--unknown` | Same semantics: include untracked files | HIGH |
| `-m`/`--message` | `-m` or `--message` | Same semantics: shelve description | HIGH |
| `stash show --stat` | `sl shelve -p <name> \| diffstat` or `--stat` | `sl shelve --stat` shows diff stats | HIGH |
| `stash@{n}` | Shelve name lookup via list | Parse sl shelve --list, use nth name | HIGH |
| `-p`/`--patch` | `-i` or `--interactive` | Interactive mode for shelving | HIGH |
| `-k`/`--keep-index` | Warning only | Sapling has no staging area | HIGH |
| `-a`/`--all` | `-A` + `-u` (addremove + unknown) | Include ignored files too | MEDIUM |
| `-q`/`--quiet` | No direct flag | Suppress output manually | MEDIUM |
| `push <pathspec>` | `sl shelve <pathspec>` | Selective file stashing | HIGH |
| `stash branch <name>` | Custom: unshelve + bookmark | Create branch from stash contents | HIGH |

### Switch Flags (CHKT-01, CHKT-02, CHKT-07 through CHKT-09)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| `-c`/`--create` | `sl bookmark <name>` + `sl goto` | Already partially implemented | HIGH |
| `-C`/`--force-create` | `sl bookmark -f <name>` + `sl goto` | Force overwrite existing | HIGH |
| `-d`/`--detach` | `sl goto --inactive` | Switch without activating bookmark | HIGH |
| `-f`/`--force`/`--discard-changes` | `sl goto -C` (clean) | Discard local changes | HIGH |
| `-m`/`--merge` | `sl goto -m` (merge) | Merge local changes during switch | HIGH |

### Checkout Flags (CHKT-05, CHKT-06)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| `--detach` | `sl goto --inactive` | sl doesn't have attached concept | HIGH |
| `-t`/`--track` | Track upstream (custom impl) | Set up remote tracking | MEDIUM |

### Restore Flags (CHKT-03, CHKT-04, CHKT-10, CHKT-11)

| Git Flag | Sl Equivalent | Notes | Confidence |
|----------|---------------|-------|------------|
| `--source=<tree>`/`-s <tree>` | `sl revert -r <rev>` | Restore from specific revision | HIGH |
| `--staged`/`-S` | Warning only | Sapling has no staging area | HIGH |
| `-q`/`--quiet` | No direct equivalent | Suppress output manually | MEDIUM |
| `-W`/`--worktree` | Default behavior | Always restores working tree | HIGH |

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stash reference parsing | Full regex parser | Simple stash@{n} match | Only one format used |
| Diff stats | Custom diff parser | sl shelve --stat or diffstat pipe | Built-in functionality |
| Branch creation | Manual bookmark + goto | Existing _handle_create_branch | Already implemented |
| Quiet mode | Complete output suppression | subprocess capture | Simple capture is sufficient |

**Key insight:** Most flags have direct sl equivalents. The main complexity is stash@{n} translation and stash branch creation.

## Common Pitfalls

### Pitfall 1: stash@{n} Index Direction
**What goes wrong:** Assuming stash@{0} is oldest instead of most recent
**Why it happens:** Git stash indexes from most recent (0) to oldest
**How to avoid:** sl shelve --list outputs most recent first; index directly matches
**Warning signs:** Wrong stash is selected

### Pitfall 2: --keep-index Expects Staging
**What goes wrong:** User expects indexed changes to remain
**Why it happens:** Sapling has no staging area concept
**How to avoid:** Print clear warning that flag is ignored
**Warning signs:** User reports missing indexed changes

### Pitfall 3: stash branch Requires Specific Sequence
**What goes wrong:** Branch created but changes not applied
**Why it happens:** Need to: 1) goto parent of stash, 2) create bookmark, 3) unshelve
**How to avoid:** Follow git's exact sequence: create branch, apply stash, drop stash
**Warning signs:** Empty branch or lingering stash

### Pitfall 4: switch -C vs checkout -B Semantics
**What goes wrong:** Force-create doesn't update existing bookmark
**Why it happens:** -C should reset to current commit if exists
**How to avoid:** Use `sl bookmark -f` which updates if exists
**Warning signs:** Bookmark at old commit

### Pitfall 5: Quiet Mode Output Leakage
**What goes wrong:** Some output still appears despite -q
**Why it happens:** Not capturing subprocess output when quiet
**How to avoid:** Use subprocess capture and discard stdout when quiet
**Warning signs:** Output appears when user expected silence

### Pitfall 6: --all Stash Includes Ignored
**What goes wrong:** -a only stashes untracked, not ignored
**Why it happens:** git -a includes ignored, sl -u does not
**How to avoid:** May need to explicitly add ignored files or warn
**Warning signs:** Ignored files not included

## Code Examples

Verified patterns from sl help and existing codebase:

### STSH-01: Include Untracked (-u)
```python
# sl shelve -u stores unknown files in the shelve
def _handle_push(args: list) -> int:
    sl_args = ['shelve']
    remaining = []

    for arg in args:
        if arg in ('-u', '--include-untracked'):
            sl_args.append('-u')  # sl uses same flag
        else:
            remaining.append(arg)

    return run_sl(sl_args + remaining)
```

### STSH-03: Show with Stats
```python
def _handle_show(args: list) -> int:
    """Handle git stash show [--stat] [stash@{n}]."""
    show_stat = '--stat' in args or '-p' not in args  # git default is stat
    show_patch = '-p' in args or '--patch' in args
    stash_ref = None

    for arg in args:
        if arg.startswith('stash@{'):
            stash_ref = translate_stash_ref(arg)

    if stash_ref is None:
        stash_ref = _get_most_recent_shelve()

    if stash_ref is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    if show_patch:
        return run_sl(['shelve', '-p', stash_ref])
    else:
        return run_sl(['shelve', '--stat', stash_ref])
```

### STSH-04: stash@{n} Reference Translation
```python
import re
from typing import Optional

def translate_stash_ref(ref: str) -> Optional[str]:
    """Convert git stash@{n} to sl shelve name."""
    match = re.match(r'stash@\{(\d+)\}', ref)
    if not match:
        return ref  # Pass through non-stash syntax

    index = int(match.group(1))
    shelves = _get_all_shelve_names()

    if index < len(shelves):
        return shelves[index]

    print(f"error: stash@{{{index}}} does not exist", file=sys.stderr)
    return None

def _get_all_shelve_names() -> list:
    """Get list of shelve names in order (most recent first)."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    names = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            # Format: "name    (age)    message"
            names.append(line.split()[0])
    return names
```

### STSH-06: Keep-Index Warning
```python
# Source: cmd_commit.py pattern for unsupported flags
if keep_index:
    print("Warning: -k/--keep-index has no effect. "
          "Sapling has no staging area; all changes are shelved.",
          file=sys.stderr)
```

### STSH-10: Stash Branch
```python
def _handle_stash_branch(args: list) -> int:
    """
    Handle git stash branch <name> [stash@{n}].

    Creates branch from stash: 1) goto parent, 2) create bookmark, 3) unshelve
    """
    if not args:
        print("error: stash branch requires a branch name", file=sys.stderr)
        return 1

    branch_name = args[0]
    stash_ref = args[1] if len(args) > 1 else None

    # Translate stash reference if provided
    shelve_name = None
    if stash_ref:
        shelve_name = translate_stash_ref(stash_ref)
        if shelve_name is None:
            return 1
    else:
        shelve_name = _get_most_recent_shelve()
        if shelve_name is None:
            print("No stash entries found.", file=sys.stderr)
            return 1

    # Create bookmark
    result = run_sl(['bookmark', branch_name])
    if result != 0:
        return result

    # Unshelve (apply and delete)
    return run_sl(['unshelve', shelve_name])
```

### CHKT-01, CHKT-02: Switch Create/Force-Create
```python
def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # Extract flags
    create = False
    force_create = False
    detach = False
    force = False
    merge = False
    branch_name = None

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ('-c', '--create'):
            create = True
            if i + 1 < len(args):
                branch_name = args[i + 1]
                i += 2
                continue

        if arg in ('-C', '--force-create'):
            force_create = True
            if i + 1 < len(args):
                branch_name = args[i + 1]
                i += 2
                continue

        if arg in ('-d', '--detach'):
            detach = True
            i += 1
            continue

        if arg in ('-f', '--force', '--discard-changes'):
            force = True
            i += 1
            continue

        if arg in ('-m', '--merge'):
            merge = True
            i += 1
            continue

        remaining.append(arg)
        i += 1

    # Handle create modes
    if create and branch_name:
        result = run_sl(['bookmark', branch_name])
        if result != 0:
            return result
        return run_sl(['goto', branch_name])

    if force_create and branch_name:
        # Use -f to force update if exists
        result = run_sl(['bookmark', '-f', branch_name])
        if result != 0:
            return result
        return run_sl(['goto', branch_name])

    # Build goto command
    goto_args = ['goto']

    if force:
        goto_args.append('-C')  # Clean/discard changes
    if merge:
        goto_args.append('-m')
    if detach:
        goto_args.append('--inactive')

    goto_args.extend(remaining)
    return run_sl(goto_args)
```

### CHKT-03: Restore with Source
```python
def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # Extract flags
    source = None
    staged = False
    quiet = False

    i = 0
    remaining = []
    while i < len(args):
        arg = args[i]

        if arg in ('-s', '--source'):
            if i + 1 < len(args):
                source = args[i + 1]
                i += 2
                continue
        elif arg.startswith('--source='):
            source = arg.split('=', 1)[1]
            i += 1
            continue

        if arg in ('-S', '--staged'):
            staged = True
            i += 1
            continue

        if arg in ('-q', '--quiet'):
            quiet = True
            i += 1
            continue

        if arg in ('-W', '--worktree'):
            # Default behavior in sl, just skip
            i += 1
            continue

        remaining.append(arg)
        i += 1

    # Warn about staged
    if staged:
        print("Warning: --staged has no effect. "
              "Sapling has no staging area.",
              file=sys.stderr)

    # Build revert command
    revert_args = ['revert']

    if source:
        revert_args.extend(['-r', source])

    revert_args.extend(remaining)

    if quiet:
        # Capture and discard output
        result = subprocess.run(
            ['sl'] + revert_args,
            capture_output=True
        )
        return result.returncode

    return run_sl(revert_args)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Basic stash ops only | Full stash flag support | Phase 26 | Enhanced workflow |
| Basic switch only | Full switch flag support | Phase 26 | Branch management |
| Simple restore | Source and quiet flags | Phase 26 | Precision restore |

**Deprecated/outdated:**
- None - this extends existing implementations

## Implementation Priority

Based on complexity and value:

1. **Simple translations (LOW effort):**
   - STSH-01: -u (same flag in sl)
   - STSH-02: -m (already works, extend handling)
   - STSH-08: -q (output suppression)
   - CHKT-10: -q (output suppression)
   - CHKT-11: -W (already default)

2. **Moderate complexity (MEDIUM effort):**
   - STSH-03: show --stat (use sl shelve --stat)
   - STSH-05: -p (translate to -i)
   - STSH-09: push pathspec (already works with shelve)
   - CHKT-01: switch -c (extend existing)
   - CHKT-02: switch -C (add force bookmark)
   - CHKT-03: restore -s (add -r to revert)
   - CHKT-07: switch -d (add --inactive)
   - CHKT-08: switch -f (add -C to goto)
   - CHKT-09: switch -m (add -m to goto)

3. **Custom implementations (HIGH effort):**
   - STSH-04: stash@{n} translation (list parsing)
   - STSH-10: stash branch (multi-step sequence)
   - CHKT-06: checkout --track (upstream setup)

4. **Warnings only:**
   - STSH-06: -k/--keep-index (no staging area)
   - STSH-07: -a/--all with ignored files (limited support)
   - CHKT-04: restore --staged (no staging area)
   - CHKT-05: checkout --detach (already detached-like)

## Open Questions

Things that couldn't be fully resolved:

1. **stash@{n} edge cases**
   - What we know: Basic index-to-name mapping works
   - What's unclear: How to handle stash@{-1} or other special refs
   - Recommendation: Support numeric only; error on special refs

2. **Ignored files with stash -a**
   - What we know: sl shelve -u handles untracked but not ignored
   - What's unclear: Whether sl shelve -A handles ignored
   - Recommendation: Document limitation; may need custom handling

3. **Track upstream for new branches**
   - What we know: -t/--track sets up remote tracking in git
   - What's unclear: Exact sl equivalent for tracking configuration
   - Recommendation: Pass through -t to sl bookmark; test behavior

4. **Quiet mode completeness**
   - What we know: Can capture and discard output
   - What's unclear: Whether exit codes are affected
   - Recommendation: Capture output only, preserve exit codes

## Sources

### Primary (HIGH confidence)
- `sl help shelve` - Verified flags: -u, -m, -i, --stat, -p, --list
- `sl help unshelve` - Verified flags: -k, --keep, -n, --name
- `sl help goto` - Verified flags: -C, -m, --inactive, -c, --check
- `sl help revert` - Verified flags: -r, --rev, -a, --all
- Existing gitsl patterns in cmd_branch.py, cmd_commit.py, cmd_checkout.py

### Secondary (MEDIUM confidence)
- Sapling documentation at sapling-scm.com/docs
- Existing test patterns in test_stash.py, test_checkout.py

### Tertiary (LOW confidence)
- None - all findings verified against sl help output

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Uses established stdlib patterns
- Architecture: HIGH - Follows existing codebase patterns
- Stash flag translations: HIGH - Verified via sl help
- Switch/restore translations: HIGH - Verified via sl help
- stash@{n} handling: MEDIUM - Requires testing to validate parsing

**Research date:** 2026-01-21
**Valid until:** 2026-02-21 (30 days - stable domain)
