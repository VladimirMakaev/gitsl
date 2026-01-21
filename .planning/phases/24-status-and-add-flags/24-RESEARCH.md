# Phase 24: Status and Add Flags - Research

**Researched:** 2026-01-21
**Domain:** Git status/add flag translation to Sapling equivalents
**Confidence:** HIGH

## Summary

This phase extends gitsl's `status` and `add` commands with additional flag support. The existing implementations handle core functionality (porcelain/short output transformation, -A/--all, -u/--update) but need enhancement for filtering, verbosity, and behavioral flags.

For status, the key flags are: `--ignored` (show ignored files), `-b/--branch` (show branch info), `-v/--verbose` (show textual changes), and `-u/--untracked-files[=<mode>]` (control untracked file display). Sapling's status command has direct equivalents for most of these: `-i` for ignored, but branch display and verbose diff output require custom handling.

For add, the existing implementation handles -A/--all and -u/--update. This phase adds: `--dry-run/-n` (preview mode), `-f/--force` (add ignored files), and `-v/--verbose` (show files as added). Sapling's add command supports `-n/--dry-run` directly. There is no `--force` equivalent in sl add, so we need alternative handling for adding ignored files.

**Primary recommendation:** Extend cmd_status.py with flag parsing for --ignored, -b, -v, and -u modes. Extend cmd_add.py with --dry-run, --force, and --verbose support. Follow the established pattern from cmd_diff.py for flag parsing with warnings for unsupported features.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Run sl commands with output capture | Already used in cmd_status.py, cmd_add.py |
| sys | stdlib | stderr output for warnings | Standard pattern from cmd_diff.py |
| common.ParsedCommand | internal | Argument parsing | Existing gitsl pattern |
| common.run_sl | internal | Execute sl with passthrough | Standard execution for pass-through flags |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| re | stdlib | Pattern matching for complex flags | Only if needed for value parsing |

**Installation:**
No additional dependencies required - stdlib only.

## Architecture Patterns

### Recommended Command Structure

Both handlers follow the established pattern from cmd_diff.py:

```
cmd_status.py / cmd_add.py
handle()
    # Flag categories for translation:
    # 1. Direct pass-through flags (--ignored -> -i)
    # 2. Flags requiring output transformation (-b for branch)
    # 3. Flags requiring value parsing (-u<mode>)
    # 4. Warning flags (unsupported features)
    # 5. Remaining args pass-through
```

### Pattern 1: Status Flag Translation

**What:** Parse git status flags and translate to sl status equivalents
**When to use:** For flags that have direct sl equivalents
**Example:**
```python
# Source: https://sapling-scm.com/docs/commands/status/
# STAT-01: --ignored -> sl status -i
if arg == '--ignored':
    sl_args.append('-i')

# STAT-03: -v/--verbose - show verbose output
elif arg in ('-v', '--verbose'):
    verbose_count += 1  # Track multiple -v flags
```

### Pattern 2: Untracked Files Mode Parsing

**What:** Handle -u/--untracked-files with optional mode value
**When to use:** For flags with optional attached values
**Example:**
```python
# STAT-05: -u/--untracked-files[=<mode>]
# Modes: no, normal, all
elif arg.startswith('-u') and len(arg) > 2:
    # Attached value: -uall
    untracked_mode = arg[2:]
elif arg == '-u':
    # Check for separate value or use default 'all'
    if i + 1 < len(parsed.args) and not parsed.args[i + 1].startswith('-'):
        i += 1
        untracked_mode = parsed.args[i]
    else:
        untracked_mode = 'all'  # git default when -u has no value
elif arg.startswith('--untracked-files'):
    if '=' in arg:
        untracked_mode = arg.split('=', 1)[1]
    else:
        untracked_mode = 'all'
```

### Pattern 3: Add Flag Translation

**What:** Parse git add flags and translate to sl add equivalents
**When to use:** For extending add command functionality
**Example:**
```python
# Source: https://sapling-scm.com/docs/commands/add/
# ADD-03: --dry-run/-n passes through
if arg in ('-n', '--dry-run'):
    sl_args.append('-n')

# ADD-04: -f/--force - no direct equivalent, need workaround
elif arg in ('-f', '--force'):
    force_add = True  # Handle specially - may need to remove from .gitignore temporarily

# ADD-05: -v/--verbose - need to capture output and print file names
elif arg in ('-v', '--verbose'):
    verbose = True
```

### Anti-Patterns to Avoid

- **Silent flag dropping:** If a flag can't be translated, warn the user rather than silently ignoring.
- **Breaking existing functionality:** Ensure --porcelain and --short continue to work with new flags.
- **Complex parsing for simple cases:** Use simple string matching when possible; only use regex for complex value parsing.

## Git to Sapling Flag Mapping Tables

### Status Flags

| Git Flag | Sapling Equivalent | Notes | Confidence |
|----------|-------------------|-------|------------|
| `--ignored` | `-i` | Direct translation - STAT-01 | HIGH |
| `-b/--branch` | Custom output | sl status doesn't show branch; need to query separately | MEDIUM |
| `-v/--verbose` | `-v` | sl status -v shows repo state info (different meaning) | LOW |
| `--porcelain` | Transform output | Already implemented in Phase 6 | HIGH |
| `--short/-s` | Transform output | Already implemented in Phase 6 | HIGH |
| `-u/--untracked-files=no` | Omit `-u` flag | Don't include untracked in output | HIGH |
| `-u/--untracked-files=normal` | Default behavior | sl shows untracked by default | HIGH |
| `-u/--untracked-files=all` | Already default | sl shows individual files in directories | MEDIUM |

### Add Flags

| Git Flag | Sapling Equivalent | Notes | Confidence |
|----------|-------------------|-------|------------|
| `-A/--all` | `addremove` | Already implemented - ADD-01 verification | HIGH |
| `-u/--update` | Custom handling | Already implemented - ADD-02 verification | HIGH |
| `-n/--dry-run` | `-n` | Direct translation - ADD-03 | HIGH |
| `-f/--force` | No direct equivalent | Need workaround for ignored files - ADD-04 | LOW |
| `-v/--verbose` | Custom output | Capture and print file names - ADD-05 | MEDIUM |

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Ignored file display | Custom ignore parsing | sl status -i | Built-in Sapling flag |
| Branch name retrieval | Parsing .sl/bookmarks | sl log -r . --template "{activebookmark}" | Template approach consistent with codebase |
| Dry-run for add | Custom file listing | sl add -n | Native sl support |
| Untracked file filtering | Manual filtering | sl status -u (for unknown only) | Built-in filtering flags |

**Key insight:** Sapling's status command has rich filtering flags (-m, -a, -r, -d, -c, -u, -i) that can be combined. Leverage these rather than post-processing output.

## Common Pitfalls

### Pitfall 1: Branch Display Mismatch

**What goes wrong:** Using sl status -b which doesn't exist, or wrong output format
**Why it happens:** git status -b shows branch header; sl status doesn't have this feature
**How to avoid:** Query branch separately: `sl log -r . --template "{activebookmark}"` and prepend to output
**Warning signs:** Missing branch info or error from invalid flag

### Pitfall 2: Verbose Flag Semantic Difference

**What goes wrong:** sl status -v shows repo state (merge, rebase), not diffs like git status -v
**Why it happens:** Different meaning of -v between git and sl
**How to avoid:** For git -v behavior (show staged changes), need to run sl diff and append to output
**Warning signs:** Users expecting diff output, getting state info

### Pitfall 3: Force Add Without Native Support

**What goes wrong:** Trying to pass -f to sl add which doesn't support it
**Why it happens:** sl add has no --force flag for ignored files
**How to avoid:** Consider alternative approaches:
  1. Warn that -f is not directly supported
  2. Potentially modify sl add behavior with --include pattern
  3. Document limitation
**Warning signs:** sl add returning errors for ignored files

### Pitfall 4: Untracked Mode Default Confusion

**What goes wrong:** -u without value behaves differently than expected
**Why it happens:** git -u defaults to 'all' mode; sl shows untracked by default
**How to avoid:** Map modes correctly:
  - no: filter out untracked (don't use -u flag, use other filters)
  - normal: default sl behavior
  - all: also default sl behavior (shows files in untracked dirs)
**Warning signs:** Wrong set of files shown in status output

### Pitfall 5: Breaking Porcelain Output

**What goes wrong:** New flags interfere with --porcelain output transformation
**Why it happens:** Adding new flag handling without considering interaction with transform_to_porcelain()
**How to avoid:** Test all new flags in combination with --porcelain
**Warning signs:** Malformed porcelain output, extra content

### Pitfall 6: Addremove Dry-Run Interaction

**What goes wrong:** --dry-run not passed correctly when combined with -A
**Why it happens:** -A translates to addremove, need to pass -n to addremove not add
**How to avoid:** Ensure -n flag is preserved when translating -A to addremove
**Warning signs:** Dry-run not working with git add -A -n

## Code Examples

Verified patterns from official sources:

### Status --ignored Flag (STAT-01)

```python
# Source: https://sapling-scm.com/docs/commands/status/
# sl status -i shows ignored files

def handle(parsed: ParsedCommand) -> int:
    """Handle 'git status' command with flag translation."""
    sl_args = []
    needs_transform = False
    show_ignored = False
    show_branch = False
    verbose = 0
    untracked_mode = 'normal'  # Default

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # Existing: Check for porcelain/short flags
        if arg in ('--porcelain', '--short', '-s'):
            needs_transform = True

        # STAT-01: --ignored -> sl status -i
        elif arg == '--ignored':
            show_ignored = True

        # STAT-02: -b/--branch - add branch info
        elif arg in ('-b', '--branch'):
            show_branch = True

        # STAT-03: -v/--verbose
        elif arg in ('-v', '--verbose'):
            verbose += 1

        # STAT-05: -u/--untracked-files[=<mode>]
        elif arg.startswith('--untracked-files'):
            if '=' in arg:
                untracked_mode = arg.split('=', 1)[1]
            else:
                untracked_mode = 'all'
        elif arg == '-u':
            # Check for attached or separate value
            if i + 1 < len(parsed.args) and parsed.args[i + 1] in ('no', 'normal', 'all'):
                i += 1
                untracked_mode = parsed.args[i]
            else:
                untracked_mode = 'all'
        elif arg.startswith('-u') and len(arg) > 2:
            untracked_mode = arg[2:]

        else:
            sl_args.append(arg)

        i += 1

    # Build sl status command
    if show_ignored:
        sl_args.append('-i')

    # ... rest of implementation
```

### Status Branch Display (STAT-02)

```python
# Source: Pattern from existing codebase
# Need to query branch separately and prepend to output

def get_branch_header(cwd=None) -> str:
    """Get git-style branch header for status output."""
    result = subprocess.run(
        ['sl', 'log', '-r', '.', '--template', '{activebookmark}'],
        capture_output=True,
        text=True,
        cwd=cwd
    )
    branch = result.stdout.strip() or '(detached)'
    return f"## {branch}\n"
```

### Add Dry-Run Flag (ADD-03)

```python
# Source: https://sapling-scm.com/docs/commands/add/
# sl add -n shows what would be added

def handle(parsed: ParsedCommand) -> int:
    """Handle 'git add' command with flag translation."""

    # Check for flags
    dry_run = '-n' in parsed.args or '--dry-run' in parsed.args
    force = '-f' in parsed.args or '--force' in parsed.args
    verbose = '-v' in parsed.args or '--verbose' in parsed.args

    # Filter out processed flags
    remaining = [a for a in parsed.args
                 if a not in ('-n', '--dry-run', '-f', '--force', '-v', '--verbose')]

    # Check for -A/--all
    if '-A' in parsed.args or '--all' in parsed.args:
        remaining = [a for a in remaining if a not in ('-A', '--all')]
        cmd = ['addremove'] + remaining
        if dry_run:
            cmd.append('-n')
        return run_sl(cmd)

    # Standard add with flags
    cmd = ['add'] + remaining
    if dry_run:
        cmd.append('-n')

    # Verbose: would need to capture output and format
    if verbose:
        result = subprocess.run(['sl'] + cmd, capture_output=True, text=True)
        # Parse and print file names with "add 'filename'" format
        if result.stdout:
            for line in result.stdout.splitlines():
                if line.strip():
                    print(f"add '{line.strip()}'")
        return result.returncode

    return run_sl(cmd)
```

### Add Force Flag (ADD-04)

```python
# Source: Research - no direct sl equivalent
# Options for handling -f/--force:

# Option 1: Warn about limitation
if force:
    print("Warning: -f/--force not directly supported in Sapling.", file=sys.stderr)
    print("Ignored files cannot be force-added via gitsl.", file=sys.stderr)
    # Skip the flag, continue with normal add

# Option 2: Use --include to explicitly include files
# This requires knowing the ignore patterns, which is complex
```

### Porcelain Status Code Verification (STAT-04)

```python
# Source: Phase 6 research - existing mapping is comprehensive
# Verify coverage of all Sapling status codes

SL_TO_GIT_STATUS = {
    'M': ' M',  # Modified in working tree (not staged - sl has no staging)
    'A': 'A ',  # Added (will be committed - equivalent to staged in git)
    'R': 'D ',  # Removed (will be deleted - equivalent to staged deletion)
    '?': '??',  # Unknown/untracked
    '!': ' D',  # Missing (deleted from disk, not via sl rm)
    'I': '!!',  # Ignored (only with --ignored flag)
}

# All sl status codes are covered:
# M - modified: mapped
# A - added: mapped
# R - removed: mapped
# ? - unknown: mapped
# ! - missing: mapped
# I - ignored: mapped
# C - clean: not shown in status output (correctly excluded)
```

### Untracked Files Mode Handling (STAT-05)

```python
# Source: https://sapling-scm.com/docs/commands/status/
# sl status filtering flags: -u for unknown only

def apply_untracked_mode(sl_args: list, mode: str) -> list:
    """Apply untracked file mode to sl status args."""
    if mode == 'no':
        # Don't show untracked files
        # Use explicit filters: modified, added, removed, deleted only
        # Remove -u flag if present, add -mard
        sl_args = [a for a in sl_args if a != '-u']
        if '-mard' not in sl_args and '-A' not in sl_args:
            sl_args.append('-mard')
    elif mode == 'all':
        # Show all untracked including in untracked directories
        # This is sl default behavior, no extra flags needed
        pass
    elif mode == 'normal':
        # Normal mode - sl default behavior
        pass
    return sl_args
```

## Verification Requirements

Based on phase requirements, existing implementations need verification:

### STAT-04: Porcelain/Short Status Code Coverage

The existing SL_TO_GIT_STATUS mapping covers all sl status codes:
- M (modified) -> ' M'
- A (added) -> 'A '
- R (removed) -> 'D '
- ? (unknown) -> '??'
- ! (missing) -> ' D'
- I (ignored) -> '!!'

**Verification:** Add test cases ensuring all codes are emulated correctly.

### ADD-01: -A/--all -> addremove Verification

Existing implementation correctly translates:
```python
if "-A" in parsed.args or "--all" in parsed.args:
    filtered_args = [a for a in parsed.args if a not in ("-A", "--all")]
    return run_sl(["addremove"] + filtered_args)
```

**Verification:** Add comprehensive tests for -A with various file states.

### ADD-02: -u/--update Verification

Existing implementation handles:
- Modified files: No action (Sapling auto-stages)
- Deleted files: sl remove --mark
- Untracked files: Ignored (correct behavior)

**Verification:** Add edge case tests (files with spaces, pathspec combinations).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Basic status passthrough | Porcelain transformation | Phase 6 | Tool compatibility |
| Basic add passthrough | -A/-u handling | Phase 8 | Git workflow compatibility |
| No flag support | Extended flag support | Phase 24 | Full git status/add compatibility |

**Deprecated/outdated:**
- None - extending existing implementations

## Open Questions

Things that couldn't be fully resolved:

1. **Force add for ignored files**
   - What we know: sl add has no --force flag
   - What's unclear: Best approach - warn only, or try workaround?
   - Recommendation: Warn with clear message; document as limitation

2. **Verbose status output**
   - What we know: git -v shows staged changes (diff), git -vv shows unstaged too
   - What's unclear: Exact format expected by tools
   - Recommendation: sl has no staging; -v could show all uncommitted changes (sl diff)

3. **Branch with porcelain**
   - What we know: git status -sb shows branch in short format
   - What's unclear: Exact format for porcelain header
   - Recommendation: Use format `## branch...tracking` when -b is combined with --short

4. **Add verbose output format**
   - What we know: git add -v prints "add 'filename'" for each file
   - What's unclear: Exact behavior for directories, patterns
   - Recommendation: Capture sl add output and reformat

## Test Scenarios Required

### Status Tests

1. **STAT-01: --ignored shows ignored files**
```python
def test_status_ignored_flag(sl_repo_with_ignored):
    result = run_gitsl(["status", "--ignored"], cwd=sl_repo)
    assert ".ignored_file" in result.stdout
```

2. **STAT-02: -b shows branch info**
```python
def test_status_branch_flag(sl_repo_with_bookmark):
    result = run_gitsl(["status", "-b"], cwd=sl_repo)
    assert "## main" in result.stdout or "## default" in result.stdout
```

3. **STAT-03: -v shows verbose (with porcelain interaction)**
```python
def test_status_verbose_flag(sl_repo_with_changes):
    result = run_gitsl(["status", "-v"], cwd=sl_repo)
    # Should show status info
    assert result.exit_code == 0
```

4. **STAT-05: -u modes**
```python
def test_status_untracked_no(sl_repo_with_untracked):
    result = run_gitsl(["status", "-uno", "--porcelain"], cwd=sl_repo)
    assert "??" not in result.stdout
```

### Add Tests

5. **ADD-03: --dry-run shows what would be added**
```python
def test_add_dry_run(sl_repo):
    (sl_repo / "newfile.txt").write_text("content")
    result = run_gitsl(["add", "-n", "newfile.txt"], cwd=sl_repo)
    assert result.exit_code == 0
    # File should NOT be added
    status = run_command(["sl", "status"], cwd=sl_repo)
    assert "? newfile.txt" in status.stdout  # Still untracked
```

6. **ADD-04: --force warning**
```python
def test_add_force_warning(sl_repo_with_ignored):
    result = run_gitsl(["add", "-f", ".ignored_file"], cwd=sl_repo)
    assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()
```

7. **ADD-05: --verbose shows files**
```python
def test_add_verbose(sl_repo):
    (sl_repo / "newfile.txt").write_text("content")
    result = run_gitsl(["add", "-v", "newfile.txt"], cwd=sl_repo)
    assert "newfile.txt" in result.stdout
```

## Sources

### Primary (HIGH confidence)
- [Sapling status command documentation](https://sapling-scm.com/docs/commands/status/) - Official sl status flags
- [Sapling add command documentation](https://sapling-scm.com/docs/commands/add/) - Official sl add flags
- [Sapling addremove command documentation](https://sapling-scm.com/docs/commands/addremove/) - addremove with --dry-run
- [Git status documentation](https://git-scm.com/docs/git-status) - Official git status flags
- [Git add documentation](https://git-scm.com/docs/git-add) - Official git add flags
- Existing gitsl codebase - cmd_status.py, cmd_add.py, cmd_diff.py patterns

### Secondary (MEDIUM confidence)
- Phase 6 research - Status output emulation patterns
- Phase 8 research - Add -u emulation patterns
- Phase 23 research - Flag translation patterns from cmd_diff.py

### Tertiary (LOW confidence)
- None - all findings verified with official docs

## Metadata

**Confidence breakdown:**
- Status flag mapping: HIGH - Direct sl equivalents documented
- Add flag mapping: HIGH - Direct sl equivalents for -n, verified no -f
- Branch display: MEDIUM - Requires custom implementation
- Force add: LOW - No sl equivalent, workaround unclear
- Porcelain verification: HIGH - Existing implementation is comprehensive

**Research date:** 2026-01-21
**Valid until:** 60 days (stable domain, core VCS flags unlikely to change)
