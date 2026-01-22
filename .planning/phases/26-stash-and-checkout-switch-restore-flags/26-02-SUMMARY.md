---
phase: 26-stash-and-checkout-switch-restore-flags
plan: 02
subsystem: testing
tags: [stash, switch, restore, checkout, flags, e2e-tests, pytest]

dependency_graph:
  requires:
    - Phase 26-01 (stash and checkout/switch/restore flags implementation)
  provides:
    - E2E tests for STSH-01 through STSH-10
    - E2E tests for CHKT-01 through CHKT-11
  affects:
    - Future flag phases (test patterns)

tech_stack:
  added: []
  patterns:
    - Stash flags test pattern with shelve verification
    - Switch/restore/checkout flag tests with bookmark verification

key_files:
  created:
    - tests/test_stash_flags.py
    - tests/test_switch_flags.py
    - tests/test_restore_flags.py
    - tests/test_checkout_flags.py
  modified: []

key_decisions:
  - "Test stash@{n} by creating multiple stashes and verifying index-to-name translation"
  - "Verify warning messages by checking stderr contains relevant keywords"
  - "Test interactive mode (-p) by checking flag acceptance rather than behavior"

patterns_established:
  - "Stash flag tests: Create changes, stash with flag, verify via sl shelve --list"
  - "Reference syntax tests: Create multiple stashes, verify stash@{n} selects correct one"
  - "Warning tests: Check stderr contains relevant keyword (staging, keep-index, track)"

metrics:
  duration: 25min
  completed: 2026-01-22
---

# Phase 26 Plan 02: Stash and Checkout/Switch/Restore Flags Tests Summary

**Comprehensive E2E tests for all 21 stash and checkout/switch/restore flag requirements covering stash@{n} translation, show/branch subcommands, and all flag variants**

## Performance

- **Duration:** 25 min
- **Started:** 2026-01-22T02:07:00Z
- **Completed:** 2026-01-22T02:32:00Z
- **Tasks:** 2
- **Files created:** 4

## Accomplishments

- Created 19 tests for stash flags (STSH-01 through STSH-10)
- Created 8 tests for switch flags (CHKT-01, CHKT-02, CHKT-07, CHKT-08, CHKT-09)
- Created 7 tests for restore flags (CHKT-03, CHKT-04, CHKT-10, CHKT-11)
- Created 3 tests for checkout flags (CHKT-05, CHKT-06)
- All 37 new tests pass, full suite of 391 tests pass with no regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create test_stash_flags.py for STSH-01 through STSH-10** - `a8c8b0c` (test)
2. **Task 2: Create switch, restore, checkout flag tests** - `b2f7a7d` (test)

## Files Created

- `tests/test_stash_flags.py` - E2E tests for stash flags (370 lines, 19 tests)
  - STSH-01: -u/--include-untracked
  - STSH-02: -m/--message
  - STSH-03: stash show --stat
  - STSH-04: stash@{n} reference syntax
  - STSH-05: -p/--patch interactive mode
  - STSH-06: -k/--keep-index warning
  - STSH-07: -a/--all includes all files
  - STSH-08: -q/--quiet suppresses output
  - STSH-09: stash push <pathspec>
  - STSH-10: stash branch <name>

- `tests/test_switch_flags.py` - E2E tests for switch flags (155 lines, 8 tests)
  - CHKT-01: -c/--create
  - CHKT-02: -C/--force-create
  - CHKT-07: -d/--detach
  - CHKT-08: -f/--force/--discard-changes
  - CHKT-09: -m/--merge

- `tests/test_restore_flags.py` - E2E tests for restore flags (133 lines, 7 tests)
  - CHKT-03: -s/--source
  - CHKT-04: --staged/-S warning
  - CHKT-10: -q/--quiet
  - CHKT-11: -W/--worktree

- `tests/test_checkout_flags.py` - E2E tests for checkout flags (65 lines, 3 tests)
  - CHKT-05: --detach
  - CHKT-06: -t/--track

## Decisions Made

1. **Test stash@{n} by index verification:** Create multiple stashes and verify that stash@{0} references most recent, stash@{1} references second most recent, etc.

2. **Verify warning messages via stderr keywords:** Rather than checking exact message text, verify stderr contains relevant keywords (staging, keep-index, track).

3. **Test interactive mode by flag acceptance:** Since -p/--patch requires TTY, verify the flag is accepted (no "unknown flag" error) rather than testing interactive behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Verification Results

- **Stash flags tests:** 19 passed (33.26s)
- **Switch/restore/checkout tests:** 18 passed (25.03s)
- **Full test suite:** 391 passed (1228.68s / 20:28)

## Next Phase Readiness

Phase 26 complete. Ready for Phase 27 (Push, Pull, Fetch, Remote Flags).

**No blockers or concerns.**

---
*Phase: 26-stash-and-checkout-switch-restore-flags*
*Completed: 2026-01-22*
