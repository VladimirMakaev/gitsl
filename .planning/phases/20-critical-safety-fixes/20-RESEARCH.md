# Phase 20: Critical Safety Fixes - Research

**Researched:** 2026-01-20
**Domain:** Git-to-Sapling flag translation safety
**Confidence:** HIGH

## Summary

This research investigates the four critical safety requirements for GitSL that protect users from destructive or unexpected behavior when using flags that have semantic differences between git and Sapling (sl).

The current implementations were analyzed:
- `cmd_commit.py`: Simple pass-through, does not handle `-a` flag specially
- `cmd_checkout.py`: Complex disambiguation logic, but no `-f` or `-m` flag handling
- `cmd_branch.py`: Already correctly translates `-D` to `-d` (safety implemented)

All requirements are well-understood with clear implementation paths. The key insight is that semantic differences between git and sl flags can cause data loss or unexpected file additions if not properly handled.

**Primary recommendation:** Implement targeted flag filtering/translation in each command handler, with comprehensive test coverage for the safety-critical behaviors.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib | 3.8+ | Core implementation | Already used throughout project |
| pytest | existing | Test framework | Already used for all tests |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shutil | stdlib | Check for sl availability | Test skip conditions |

No new dependencies required - all changes are to existing command handlers.

## Architecture Patterns

### Existing Project Structure
```
gitsl/
├── cmd_commit.py       # Handle commit command
├── cmd_checkout.py     # Handle checkout command
├── cmd_branch.py       # Handle branch command
├── common.py           # ParsedCommand, run_sl()
└── tests/
    ├── test_commit.py
    ├── test_checkout.py
    └── test_branch.py
```

### Pattern 1: Flag Filtering (for SAFE-01)
**What:** Remove flags before passing to sl when semantics differ dangerously
**When to use:** When git flag would cause unintended behavior in sl
**Example:**
```python
# Source: Existing pattern in cmd_branch.py (lines 21-24)
def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # Remove -a/--all flags - git commits tracked changes only,
    # sl -A adds untracked files (dangerous semantic difference)
    args = [a for a in args if a not in ('-a', '--all')]

    return run_sl(["commit"] + args)
```

### Pattern 2: Flag Translation (for SAFE-02, SAFE-03)
**What:** Translate git flags to equivalent sl flags
**When to use:** When git flag has a semantic equivalent in sl with different name
**Example:**
```python
# Source: Existing pattern in cmd_branch.py (line 24)
# Translate -D to -d for safety
args = ['-d' if a == '-D' else a for a in args]

# For checkout -f -> goto -C
args = ['-C' if a in ('-f', '--force') else a for a in args]
```

### Pattern 3: Context-Aware Flag Handling (for checkout)
**What:** Handle flags differently based on checkout mode (branch switch vs file restore)
**When to use:** When a flag applies only to certain uses of a multi-purpose command
**Example:**
```python
# -f and -m only apply to branch switching (goto), not file restoration (revert)
# Current checkout code already distinguishes these modes
if is_revision:
    # Switching branches - handle -f/-m flags for goto
    goto_args = translate_checkout_flags(args)
    return run_sl(["goto"] + goto_args)
else:
    # Restoring files - -f/-m have different meaning or don't apply
    return run_sl(["revert"] + args)
```

### Anti-Patterns to Avoid
- **Blind pass-through of flags:** Never assume git flags have same meaning in sl
- **Forgetting long-form flags:** Always handle both `-f` and `--force` variants
- **Missing test coverage for safety:** All safety translations MUST have explicit tests

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Argument parsing | Custom parser | List comprehensions | Simple flag filtering is sufficient |
| Command execution | subprocess directly | `run_sl()` from common.py | Handles I/O passthrough correctly |

**Key insight:** The existing patterns in `cmd_branch.py` for `-D` to `-d` translation are the template for all safety fixes.

## Common Pitfalls

### Pitfall 1: Forgetting Long-Form Flags
**What goes wrong:** Handling `-a` but not `--all`, allowing dangerous behavior
**Why it happens:** Developer only tests short form
**How to avoid:** Always list both forms in translations: `('-a', '--all')`
**Warning signs:** Test only uses short form

### Pitfall 2: Passing Through Unknown Flags
**What goes wrong:** New git flags get passed directly to sl, may have different semantics
**Why it happens:** Pass-through is the default behavior
**How to avoid:** Document expected flags, warn on unknown flags in debug mode
**Warning signs:** User reports unexpected behavior

### Pitfall 3: Not Testing Both Sides
**What goes wrong:** Test verifies flag is removed but not that behavior is correct
**Why it happens:** Testing only the translation, not the outcome
**How to avoid:** Test that untracked files are NOT added when using -a
**Warning signs:** Test mocks sl instead of running actual commands

### Pitfall 4: Order-Dependent Flag Processing
**What goes wrong:** Flag position in args causes it to be missed
**Why it happens:** Some implementations only check first N args
**How to avoid:** Process entire args list: `[a for a in args if a not in flags]`
**Warning signs:** `git commit -m "msg" -a` works but `git commit -a -m "msg"` doesn't

## Code Examples

### SAFE-01: Commit -a Flag Removal
```python
# Source: Analysis of git commit --help and sl help commit
# git -a: stage tracked modified/deleted files only
# sl -A: addremove - adds untracked files too (DANGEROUS)

def handle(parsed: ParsedCommand) -> int:
    args = list(parsed.args)

    # CRITICAL: Remove -a/--all flags
    # git: stages tracked modified/deleted files
    # sl -A: adds untracked files (semantic mismatch!)
    args = [a for a in args if a not in ('-a', '--all')]

    return run_sl(["commit"] + args)
```

### SAFE-02: Checkout -f Translation
```python
# Source: Analysis of git checkout --help and sl help goto
# git checkout -f: throw away local changes, switch branch
# sl goto -C: discard uncommitted changes (clean)

def translate_checkout_flags(args: List[str]) -> List[str]:
    """Translate git checkout flags to sl goto flags."""
    result = []
    for arg in args:
        if arg in ('-f', '--force'):
            result.append('-C')  # sl goto --clean
        else:
            result.append(arg)
    return result
```

### SAFE-03: Checkout -m Translation
```python
# Source: Analysis of git checkout --help and sl help goto
# git checkout -m: merge local changes during switch
# sl goto -m: merge uncommitted changes (same semantics!)

def translate_checkout_flags(args: List[str]) -> List[str]:
    """Translate git checkout flags to sl goto flags."""
    result = []
    for arg in args:
        if arg in ('-f', '--force'):
            result.append('-C')  # --clean
        elif arg in ('-m', '--merge'):
            result.append('-m')  # Same flag, passes through
        else:
            result.append(arg)
    return result
```

### SAFE-04: Branch -D Translation (Already Implemented)
```python
# Source: cmd_branch.py lines 21-24
# git -D: force delete label, commits preserved
# sl -D: delete label AND strip commits (DESTRUCTIVE!)

args = ['-d' if a == '-D' else a for a in args]
```

### Test Pattern for Safety Requirements
```python
# Source: Existing pattern in test_branch.py

class TestCommitSafety:
    """SAFE-01: git commit -a should not add untracked files."""

    def test_commit_a_does_not_add_untracked(self, sl_repo_with_commit: Path):
        """git commit -a ignores untracked files (removes flag)."""
        # Create untracked file
        (sl_repo_with_commit / "untracked.txt").write_text("new\n")

        # Modify tracked file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        # Commit with -a
        result = run_gitsl(["commit", "-a", "-m", "test"], cwd=sl_repo_with_commit)

        # Untracked file should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "untracked.txt" in status.stdout  # Still shows as untracked
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pass-through all flags | Flag filtering/translation | This phase | Prevents data loss |

**Current state of implementations:**
- `cmd_commit.py`: Full pass-through (needs SAFE-01)
- `cmd_checkout.py`: No flag handling (needs SAFE-02, SAFE-03)
- `cmd_branch.py`: Already has SAFE-04 implemented

## Open Questions

None - all requirements are clearly understood with verified implementations.

## Sources

### Primary (HIGH confidence)
- Local file analysis: `/Users/vmakaev/NonWork/gitsl/cmd_commit.py` - verified current implementation
- Local file analysis: `/Users/vmakaev/NonWork/gitsl/cmd_checkout.py` - verified current implementation
- Local file analysis: `/Users/vmakaev/NonWork/gitsl/cmd_branch.py` - verified SAFE-04 implementation
- `git commit --help` - verified -a flag semantics
- `git checkout --help` - verified -f and -m flag semantics
- `sl help commit` - verified -A (addremove) semantics
- `sl help goto` - verified -C (clean) and -m (merge) semantics

### Secondary (MEDIUM confidence)
- Existing test files verified pattern for E2E testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependencies needed
- Architecture: HIGH - existing patterns in codebase are perfect templates
- Pitfalls: HIGH - based on direct analysis of semantic differences

**Research date:** 2026-01-20
**Valid until:** Indefinite - core git/sl semantics are stable

## Implementation Summary

| Requirement | File | Current State | Change Needed |
|-------------|------|---------------|---------------|
| SAFE-01 | cmd_commit.py | Pass-through | Remove `-a`/`--all` flags |
| SAFE-02 | cmd_checkout.py | No handling | Add `-f`→`-C` translation |
| SAFE-03 | cmd_checkout.py | No handling | Pass through `-m` (same) |
| SAFE-04 | cmd_branch.py | Implemented | Add test coverage only |

**Complexity Assessment:**
- SAFE-01: Simple (2-3 lines, add tests)
- SAFE-02: Medium (integrate into existing checkout logic)
- SAFE-03: Simple (may already work, verify with tests)
- SAFE-04: Simple (tests only, implementation complete)
