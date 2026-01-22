---
phase: 26-stash-and-checkout-switch-restore-flags
plan: 01
subsystem: working-tree-commands
tags: [stash, switch, restore, checkout, flags, shelve, goto, revert]

dependency_graph:
  requires:
    - Phase 17 (stash, switch, restore, checkout base commands)
  provides:
    - STSH-01 through STSH-10 flag handling
    - CHKT-01 through CHKT-11 flag handling
  affects:
    - Phase 26-02 (E2E tests for these flags)

tech_stack:
  added: []
  patterns:
    - stash@{n} reference translation via shelve list parsing
    - Quiet mode via subprocess capture
    - Warning pattern for staging area flags

key_files:
  created: []
  modified:
    - cmd_stash.py
    - cmd_switch.py
    - cmd_restore.py
    - cmd_checkout.py

decisions:
  - id: STSH-04-TRANSLATION
    choice: Parse stash@{n} syntax and lookup shelve name via sl shelve --list
    rationale: Git stash@{0} is most recent, sl shelve --list outputs most recent first
  - id: STSH-05-INTERACTIVE
    choice: Translate -p/--patch to -i for interactive shelving
    rationale: sl shelve uses -i for interactive mode, same semantic
  - id: STSH-10-BRANCH
    choice: Implement stash branch as bookmark creation + unshelve
    rationale: Git stash branch creates branch and applies stash; sl needs two steps
  - id: CHKT-05-DETACH
    choice: Translate --detach to --inactive for goto
    rationale: sl goto --inactive prevents bookmark activation
  - id: CHKT-06-TRACK
    choice: Accept track flag with note about limited emulation
    rationale: Sapling tracking differs from git; accept flag for compatibility

metrics:
  duration: 10 minutes
  completed: 2026-01-22
---

# Phase 26 Plan 01: Stash and Checkout/Switch/Restore Flags Summary

**One-liner:** Extended stash with stash@{n} translation, show/branch subcommands, and -u/-m/-p/-k/-a/-q flags; extended switch/restore/checkout with create/force/detach/source/staged flags.

## What Was Built

### Task 1: Extended cmd_stash.py (STSH-01 through STSH-10)

Added comprehensive flag support for stash command:

- **STSH-01 (-u/--include-untracked):** Translates to `sl shelve -u` for including untracked files
- **STSH-02 (-m/--message):** Translates to `sl shelve -m` for stash description
- **STSH-03 (show --stat):** New `_handle_show` function with `sl shelve --stat`
- **STSH-04 (stash@{n}):** New `_translate_stash_ref` and `_get_all_shelve_names` for index-to-name lookup
- **STSH-05 (-p/--patch):** Translates to `sl shelve -i` for interactive mode
- **STSH-06 (-k/--keep-index):** Warning printed (no staging area in Sapling)
- **STSH-07 (-a/--all):** Translates to -u with note about ignored files
- **STSH-08 (-q/--quiet):** Suppress output via subprocess capture
- **STSH-09 (pathspec):** Pass through file paths to sl shelve
- **STSH-10 (stash branch):** New `_handle_branch` for bookmark creation + unshelve

### Task 2: Extended cmd_switch.py, cmd_restore.py, cmd_checkout.py (CHKT-01 through CHKT-11)

**cmd_switch.py:**
- **CHKT-01 (-c/--create):** Create bookmark and goto
- **CHKT-02 (-C/--force-create):** Force-create bookmark with -f flag
- **CHKT-07 (-d/--detach):** Add --inactive to goto
- **CHKT-08 (-f/--force/--discard-changes):** Add -C to goto for clean switch
- **CHKT-09 (-m/--merge):** Add -m to goto for merge mode

**cmd_restore.py:**
- **CHKT-03 (-s/--source):** Add -r to revert for specific revision
- **CHKT-04 (--staged/-S):** Print warning about no staging area
- **CHKT-10 (-q/--quiet):** Suppress output via subprocess capture
- **CHKT-11 (-W/--worktree):** Skip flag (default behavior)

**cmd_checkout.py:**
- **CHKT-05 (--detach):** Add --inactive to goto
- **CHKT-06 (-t/--track):** Print note about limited tracking emulation

## Key Changes

### New Functions in cmd_stash.py

```python
def _get_all_shelve_names() -> list:
    """Get list of shelve names in order (most recent first)."""

def _translate_stash_ref(ref: str) -> Optional[str]:
    """Convert git stash@{n} to sl shelve name."""

def _handle_show(args: list) -> int:
    """Handle git stash show [--stat] [-p] [stash@{n}]."""

def _handle_branch(args: list) -> int:
    """Handle git stash branch <name> [stash@{n}]."""
```

### Flag Translation Patterns

| Git Flag | Sapling Equivalent | Command |
|----------|-------------------|---------|
| stash -u | shelve -u | Include untracked |
| stash -p | shelve -i | Interactive mode |
| stash@{n} | shelve name lookup | Index translation |
| switch -C | bookmark -f + goto | Force create |
| switch -d | goto --inactive | Detach mode |
| restore -s | revert -r | Source revision |
| checkout --detach | goto --inactive | Detach mode |

## Verification Results

- All 15 existing stash tests pass
- All 26 existing switch/restore/checkout tests pass
- All 41 relevant tests pass in 71 seconds
- Import verification successful for all modified modules

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Hash | Message |
|------|---------|
| 2b3b37d | feat(26-01): extend stash handler with comprehensive flag support |
| 8cbb544 | feat(26-01): extend switch, restore, checkout handlers with flag support |

## Next Phase Readiness

Ready for Phase 26-02: E2E tests for stash and checkout/switch/restore flags.

**Files to test:**
- cmd_stash.py: All STSH-01 through STSH-10 requirements
- cmd_switch.py: All CHKT-01, CHKT-02, CHKT-07 through CHKT-09 requirements
- cmd_restore.py: All CHKT-03, CHKT-04, CHKT-10, CHKT-11 requirements
- cmd_checkout.py: All CHKT-05, CHKT-06 requirements

**No blockers or concerns.**
