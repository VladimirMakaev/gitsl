# Phase 28: Clone, Rm, Mv, Clean, Config Flags - Research

**Researched:** 2026-01-22
**Domain:** Git command flag translation to Sapling
**Confidence:** HIGH

## Summary

Phase 28 implements comprehensive flag support for five utility commands: clone, rm, mv, clean, and config. These commands have basic implementations that pass through to Sapling but lack flag translations.

Research reveals that most git flags have direct or close Sapling equivalents, with a few exceptions requiring warnings. Key translations include:
- Clone: `-b` branch becomes `-u` updaterev, `--depth` becomes `--shallow` (deprecated/no-op)
- Rm: `--cached` has no equivalent (Sapling has no staging area) - requires warning
- Mv: Direct pass-through for most flags, `-k` (skip errors) has no equivalent
- Clean: `-x` becomes `--ignored`, `-X` (ignored only) requires filtering logic
- Config: `--global` becomes `--user`, scopes work similarly but with different flag names

**Primary recommendation:** Implement flag handlers following the established pattern from cmd_grep.py and cmd_blame.py - explicit flag parsing with translations, warnings for unsupported flags, and pass-through for remaining args.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python 3.x | 3.9+ | Handler implementation | Project standard |
| pytest | Latest | E2E testing | Project standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess | stdlib | Running sl commands | All handlers use run_sl() |

**No additional dependencies required.** This phase extends existing command handlers.

## Current Implementation Summary

### cmd_clone.py (Minimal)
```python
def handle(parsed: ParsedCommand) -> int:
    return run_sl(["clone"] + parsed.args)
```
No flag handling - passes everything through.

### cmd_rm.py (Basic)
```python
def handle(parsed: ParsedCommand) -> int:
    filtered_args = [a for a in parsed.args if a not in ('-r', '--recursive')]
    return run_sl(["remove"] + filtered_args)
```
Only filters out `-r/--recursive` (sl remove is recursive by default).

### cmd_mv.py (Minimal)
```python
def handle(parsed: ParsedCommand) -> int:
    return run_sl(["rename"] + parsed.args)
```
No flag handling - passes everything through.

### cmd_clean.py (Moderate)
```python
def handle(parsed: ParsedCommand) -> int:
    # Handles -f, -n, -d flags
    # Enforces git's requireForce safety requirement
```
Handles basic flags (-f, -d, -n), needs -x, -X, -e.

### cmd_config.py (Basic)
```python
def handle(parsed: ParsedCommand) -> int:
    # Handles --list/-l
    # Defaults to --local for writes
```
Handles --list and --local default, needs --get, --unset, scope flags, --show-origin, --all.

## Sapling Command Reference

### sl clone
| Flag | Description |
|------|-------------|
| `-U/--noupdate` | Clone without checkout |
| `-u/--updaterev REV` | Revision or branch to check out |
| `--shallow` | DEPRECATED - has no effect (default: True) |
| `--git` | Force git protocol |
| `-q/--quiet` | Suppress output (global) |
| `-v/--verbose` | Enable additional output (global) |

**Key findings:**
- No `-b/--branch` - use `-u/--updaterev` instead
- `--shallow` is deprecated and has no effect (Sapling uses lazy fetching by default)
- No `--single-branch` equivalent - Sapling's model differs
- No `-o/--origin` - Sapling configures remotes differently
- No `--recursive/--recurse-submodules` - submodules work differently
- No `--no-tags` - tags handled differently in Sapling

### sl remove (alias: rm)
| Flag | Description |
|------|-------------|
| `--mark` | Mark as deletion for already missing files |
| `-f/--force` | Forget added files, delete modified files |
| `-I/--include PATTERN` | Include files matching pattern |
| `-X/--exclude PATTERN` | Exclude files matching pattern |
| `-q/--quiet` | Suppress output (global) |
| `-v/--verbose` | Enable additional output (global) |

**Key findings:**
- No `--cached` equivalent - Sapling has no staging area
- No `-n/--dry-run` - must use different approach
- No `-r/--recursive` needed - recursive by default
- `-q/--quiet` is global flag, works automatically

### sl rename (aliases: move, mv)
| Flag | Description |
|------|-------------|
| `--mark` | Mark a rename that has already occurred |
| `--amend` | Amend current commit to mark rename |
| `-f/--force` | Forcibly copy over existing managed file |
| `-n/--dry-run` | Do not perform actions, just print output |
| `-I/--include PATTERN` | Include files matching pattern |
| `-X/--exclude PATTERN` | Exclude files matching pattern |
| `-q/--quiet` | Suppress output (global) |
| `-v/--verbose` | Enable additional output (global) |

**Key findings:**
- `-f/--force` passes through directly
- `-n/--dry-run` passes through directly
- `-v/--verbose` is global flag, works automatically
- No `-k` (skip errors) equivalent - needs warning or emulation

### sl clean (alias: purge)
| Flag | Description |
|------|-------------|
| `-a/--abort-on-err` | Abort if an error occurs |
| `--all` | Delete ignored files too (DEPRECATED) |
| `--ignored` | Delete ignored files too |
| `--dirs` | Delete empty directories |
| `--files` | Delete files (implied by default) |
| `-p/--print` | Print filenames instead of deleting |
| `-0/--print0` | NUL-terminate output (implies -p) |
| `-I/--include PATTERN` | Include files matching pattern |
| `-X/--exclude PATTERN` | Exclude files matching pattern |
| `-q/--quiet` | Suppress output (global) |
| `-v/--verbose` | Enable additional output (global) |

**Key findings:**
- `git -x` (remove ignored too) -> `sl --ignored`
- `git -X` (ONLY ignored) -> `sl --ignored` with file filtering (complex)
- `git -e <pattern>` -> `sl -X <pattern>` (exclude pattern - same letter, different meaning!)
- `--files` and `--dirs` handle what git's `-d` does

### sl config
| Flag | Description |
|------|-------------|
| `-u/--user` | Edit user-level config |
| `-l/--local` | Edit repository-level config |
| `-g/--global` | Edit system config (DEPRECATED, alias for --system) |
| `-s/--system` | Edit system-wide config |
| `-d/--delete` | Delete specified config items |
| `--debug` | Show source (filename:line) for each config item |
| `-T/--template` | Display with template (EXPERIMENTAL) |

**Key findings:**
- git `--global` -> sl `--user` (user-level config)
- git `--local` -> sl `--local` (same)
- git `--system` -> sl `--system` (same)
- git `--get` -> sl just reads by default (no flag needed)
- git `--unset` -> sl `--delete`
- git `--show-origin` -> sl `--debug` (shows source)
- git `--list/-l` -> sl with no args shows all config
- git `--all` (multi-valued) -> No direct equivalent, needs custom handling

## Flag Translation Table

### Clone Flags (CLON-*)

| Git Flag | Sapling Flag | Action | Confidence |
|----------|--------------|--------|------------|
| `-b <branch>/--branch` | `-u <bookmark>` | Translate to updaterev | HIGH |
| `--depth <n>` | `--shallow` | Warn: deprecated, pass through | HIGH |
| `--single-branch` | (none) | Warn: not applicable | HIGH |
| `-o/--origin <name>` | (none) | Warn: remotes work differently | HIGH |
| `-n/--no-checkout` | `-U/--noupdate` | Translate | HIGH |
| `--recursive/--recurse-submodules` | (none) | Warn: submodules unsupported | HIGH |
| `--no-tags` | (none) | Warn: not applicable | HIGH |
| `-q/--quiet` | `-q/--quiet` | Pass through (global) | HIGH |
| `-v/--verbose` | `-v/--verbose` | Pass through (global) | HIGH |

### Rm Flags (RM-*)

| Git Flag | Sapling Flag | Action | Confidence |
|----------|--------------|--------|------------|
| `-f/--force` | `-f/--force` | Pass through | HIGH |
| `--cached` | (none) | Warn: no staging area | HIGH |
| `-n/--dry-run` | (none) | Warn: not supported, suggest status | HIGH |
| `-q/--quiet` | `-q/--quiet` | Pass through (global) | HIGH |
| `-r/--recursive` | (remove) | Filter out (recursive by default) | HIGH |

### Mv Flags (MV-*)

| Git Flag | Sapling Flag | Action | Confidence |
|----------|--------------|--------|------------|
| `-f/--force` | `-f/--force` | Pass through | HIGH |
| `-k` | (none) | Warn: skip errors not supported | HIGH |
| `-v/--verbose` | `-v/--verbose` | Pass through (global) | HIGH |
| `-n/--dry-run` | `-n/--dry-run` | Pass through | HIGH |

### Clean Flags (CLEN-*)

| Git Flag | Sapling Flag | Action | Confidence |
|----------|--------------|--------|------------|
| `-x` | `--ignored` | Translate: remove ignored too | HIGH |
| `-X` | (complex) | Warn: ONLY ignored is complex | MEDIUM |
| `-e <pattern>` | `-X <pattern>` | Translate: exclude pattern | HIGH |
| `-f` | (safety check) | Already implemented | HIGH |
| `-d` | `--files --dirs` | Already implemented | HIGH |
| `-n` | `--print` | Already implemented | HIGH |

### Config Flags (CONF-*)

| Git Flag | Sapling Flag | Action | Confidence |
|----------|--------------|--------|------------|
| `--get` | (default) | No flag needed, pass key | HIGH |
| `--unset` | `--delete` | Translate | HIGH |
| `--list/-l` | (no args) | Already handled | HIGH |
| `--global` | `--user` | Translate | HIGH |
| `--local` | `--local` | Pass through | HIGH |
| `--system` | `--system` | Pass through | HIGH |
| `--show-origin` | `--debug` | Translate | HIGH |
| `--all` | (none) | Warn: multi-value not supported | MEDIUM |

## Implementation Approach

### Clone Handler Updates
1. Parse `-b/--branch <value>` and translate to `-u <value>`
2. Handle `--depth` with warning (no real effect in Sapling)
3. Translate `-n/--no-checkout` to `-U/--noupdate`
4. Warn for unsupported: `--single-branch`, `-o/--origin`, `--recursive`, `--no-tags`
5. Pass through `-q/--quiet` and `-v/--verbose` (global flags)

```python
# Pattern for branch translation
if arg in ('-b', '--branch'):
    if i + 1 < len(args):
        i += 1
        sl_args.extend(['-u', args[i]])
```

### Rm Handler Updates
1. Keep existing `-r/--recursive` filtering
2. Warn for `--cached` (no staging area)
3. Warn for `-n/--dry-run` (suggest `sl status` instead)
4. Pass through `-f/--force`, `-q/--quiet`

```python
# Pattern for --cached warning
if arg == '--cached':
    print("Warning: --cached not supported. Sapling has no staging area. "
          "File will remain on disk; use 'sl forget' to untrack.",
          file=sys.stderr)
```

### Mv Handler Updates
1. Pass through `-f/--force`, `-n/--dry-run`, `-v/--verbose`
2. Warn for `-k` (skip errors)

### Clean Handler Updates
1. Translate `-x` to `--ignored`
2. Handle `-X` (only ignored files) - complex, may need post-processing or warning
3. Translate `-e <pattern>` to `-X <pattern>`
4. Existing -f, -d, -n handling is correct

```python
# Pattern for -x translation
if arg == '-x':
    sl_args.append('--ignored')
elif arg == '-X':
    print("Warning: -X (only ignored files) has limited support. "
          "Using --ignored which removes all untracked and ignored.",
          file=sys.stderr)
    sl_args.append('--ignored')
elif arg == '-e':
    if i + 1 < len(args):
        i += 1
        sl_args.extend(['-X', args[i]])
```

### Config Handler Updates
1. Translate `--global` to `--user`
2. Translate `--unset` to `--delete`
3. Translate `--show-origin` to `--debug`
4. Warn for `--all` (multi-valued keys)
5. `--get` requires no translation (default behavior)

```python
# Pattern for scope translation
if arg == '--global':
    sl_args.append('--user')
elif arg == '--unset':
    sl_args.append('--delete')
elif arg == '--show-origin':
    sl_args.append('--debug')
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Config file parsing | Custom INI parser | sl config command | Sapling handles file locations |
| Shallow clone | Custom history truncation | Accept limitations | Sapling has lazy fetching |
| Submodule handling | Custom submodule logic | Warn and skip | Sapling handles repos differently |
| Multi-valued config | Custom value collection | Warn limitation | Complex to emulate git behavior |

## Common Pitfalls

### Pitfall 1: Global vs User Config Scope
**What goes wrong:** Assuming git's `--global` is system-wide
**Why it happens:** Naming confusion between git and Sapling
**How to avoid:** git `--global` = user level = sl `--user`
**Warning signs:** Config written to wrong file

### Pitfall 2: Staging Area Assumptions
**What goes wrong:** Trying to implement `--cached` behavior
**Why it happens:** Sapling has no staging area concept
**How to avoid:** Warn users and suggest alternatives (sl forget)
**Warning signs:** Any attempt to manipulate staged state

### Pitfall 3: Clean -X Semantics
**What goes wrong:** Assuming sl --ignored only removes ignored
**Why it happens:** git -X removes ONLY ignored, sl --ignored adds ignored to removals
**How to avoid:** Clear warning about semantic difference
**Warning signs:** User expects only ignored files removed

### Pitfall 4: Branch vs Bookmark
**What goes wrong:** Assuming git branches = sl bookmarks directly
**Why it happens:** Different mental models
**How to avoid:** Use -u (updaterev) for clone checkout target
**Warning signs:** Clone checking out wrong revision

### Pitfall 5: Dry-run Support Variations
**What goes wrong:** Assuming all commands support -n/--dry-run
**Why it happens:** Git has uniform -n support, Sapling varies
**How to avoid:** Check each command's help for dry-run support
**Warning signs:** rm doesn't support dry-run, rename does

## Test Strategy

### Test Structure Pattern
Follow existing test file patterns (test_grep_flags.py, test_blame_flags.py):

```python
"""E2E tests for git clone flags (CLON-01 through CLON-09)."""

class TestClonePassThrough:
    """Tests for clone flags that pass through directly."""

class TestCloneTranslation:
    """Tests for clone flags that require translation."""

class TestCloneUnsupported:
    """Tests for clone flags that are unsupported (warn and skip)."""
```

### Test Categories by Command

**Clone:**
- CLON-01: Test `-b` translates to `-u` (verify bookmark checkout)
- CLON-02/03: Test `--depth`, `--single-branch` warnings
- CLON-04: Test `-o/--origin` warning
- CLON-05: Test `-n/--no-checkout` creates empty working dir
- CLON-06/07: Test `--recursive`, `--no-tags` warnings
- CLON-08/09: Test quiet/verbose pass through

**Rm:**
- RM-01: Test `-f/--force` removes modified file
- RM-02: Test `--cached` produces warning
- RM-03: Test `-n/--dry-run` warning (or emulation)
- RM-04: Test `-q/--quiet` suppresses output
- RM-05: Verify `-r` filtered out (already working)

**Mv:**
- MV-01: Test `-f/--force` overwrites existing
- MV-02: Test `-k` warning
- MV-03: Test `-v/--verbose` shows files
- MV-04: Test `-n/--dry-run` previews without moving

**Clean:**
- CLEN-01: Test `-x` removes ignored files too
- CLEN-02: Test `-X` behavior (warning or implementation)
- CLEN-03: Test `-e <pattern>` excludes matching files
- CLEN-04: Verify existing -f, -d, -n work

**Config:**
- CONF-01: Test `--get` reads specific key
- CONF-02: Test `--unset` removes key
- CONF-03: Test `--list/-l` shows all
- CONF-04: Test `--global` -> `--user` translation
- CONF-05: Test `--local` scope
- CONF-06: Test `--system` scope
- CONF-07: Test `--show-origin` shows file source
- CONF-08: Test `--all` warning

### Fixture Requirements
- `sl_repo_with_commit`: Most tests
- `sl_repo`: Config tests
- Clone tests need source repo to clone from (sl_repo_with_commit fixture)
- Clean tests need untracked and ignored files

## Edge Cases and Warnings

### Clone Edge Cases
1. **Cloning git URLs**: Sapling can clone from git repos with `--git` flag
2. **Remote name**: Sapling doesn't use "origin" concept the same way
3. **Shallow clone**: `--shallow` is deprecated and has no effect

### Rm Edge Cases
1. **Removing added-but-not-committed**: Needs `-f/--force`
2. **Removed file already gone**: Use `--mark` (sl behavior)

### Mv Edge Cases
1. **Moving to existing file**: Needs `-f/--force`
2. **Moving directory**: Works without -r (sl recursive by default)

### Clean Edge Cases
1. **-X (only ignored)**: Cannot easily replicate with sl purge
   - Option A: Warn and use --ignored (removes more than expected)
   - Option B: Custom implementation using sl status + file deletion
2. **Nested repositories**: git needs `-ff`, sl may handle differently
3. **Ignored vs Untracked distinction**: sl status -i vs -u

### Config Edge Cases
1. **Reading non-existent key**: Returns error code 1
2. **Multi-valued keys**: git --all returns all values, sl doesn't support
3. **Section.key=value format**: Can set via command line

## Sources

### Primary (HIGH confidence)
- Sapling CLI help: `sl help clone`, `sl help remove`, `sl help rename`, `sl help purge`, `sl config --help`
- Git documentation: https://git-scm.com/docs/git-clone, https://git-scm.com/docs/git-rm, https://git-scm.com/docs/git-mv, https://git-scm.com/docs/git-clean, https://git-scm.com/docs/git-config

### Secondary (MEDIUM confidence)
- Project codebase analysis: cmd_grep.py, cmd_blame.py (handler patterns)
- Project test patterns: test_grep_flags.py, test_blame_flags.py

## Metadata

**Confidence breakdown:**
- Clone translations: HIGH - verified with sl help clone
- Rm translations: HIGH - verified with sl help remove
- Mv translations: HIGH - verified with sl help rename
- Clean translations: HIGH - verified with sl help purge
- Config translations: HIGH - verified with sl config --help
- Test patterns: HIGH - verified from existing test files

**Research date:** 2026-01-22
**Valid until:** 2026-02-22 (30 days - stable domain)
