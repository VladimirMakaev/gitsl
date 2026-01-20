---
phase: 20-critical-safety-fixes
plan: 01
subsystem: commands
tags: [safety, commit, checkout, branch, flag-translation]

# Dependency graph
requires:
  - phase: none (first phase in v1.3)
    provides: existing command handlers
provides:
  - SAFE-01: commit -a flag safety (removes flag to prevent untracked file addition)
  - SAFE-02: checkout -f flag translation (-f -> -C for sl goto)
  - SAFE-03: checkout -m flag passthrough (-m -> -m for sl goto)
  - SAFE-04: branch -D safety (already implemented, verified with tests)
affects: [command-handlers, flag-compatibility]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Flag filtering: Remove dangerous flags before passing to sl"
    - "Flag translation: Map git flags to equivalent sl flags"

key-files:
  created: []
  modified:
    - cmd_commit.py
    - cmd_checkout.py
    - tests/test_commit.py
    - tests/test_checkout.py

key-decisions:
  - "Remove -a/--all from commit entirely rather than translate (semantic difference too dangerous)"
  - "Translate -f/--force to -C for goto paths (matches sl goto -C semantics)"
  - "Pass through -m/--merge to -m for goto paths (same semantics in sl)"

patterns-established:
  - "Safety flag handling: Filter or translate flags with dangerous semantic differences"
  - "SAFE requirements: All safety-critical translations tested with E2E tests"

# Metrics
duration: 22min
completed: 2026-01-20
---

# Phase 20 Plan 01: Critical Safety Fixes Summary

**Safety flag handling for commit -a, checkout -f/-m ensuring git-compatible behavior without data loss**

## Performance

- **Duration:** 22 min
- **Started:** 2026-01-20T23:18:08Z
- **Completed:** 2026-01-20T23:40:42Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Implemented SAFE-01: `git commit -a` removes flag to prevent sl from adding untracked files
- Implemented SAFE-02: `git checkout -f` translates to `sl goto -C` for clean checkout
- Implemented SAFE-03: `git checkout -m` passes through to `sl goto -m` for merge behavior
- Verified SAFE-04: `git branch -D` already correctly translates to `sl bookmark -d` (preserves commits)
- Added 6 new E2E tests covering all safety requirements
- Full test suite passes (197 tests)

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement safety flag handling** - `b447953` (feat)
2. **Task 2: Add E2E tests for safety requirements** - `63d1b1f` (test)

## Files Created/Modified

- `cmd_commit.py` - Filter -a/--all flags before passing to sl commit
- `cmd_checkout.py` - Add _translate_goto_flags() function, translate -f to -C and pass -m through
- `tests/test_commit.py` - Added TestCommitSafety class with 2 tests for SAFE-01
- `tests/test_checkout.py` - Added TestCheckoutForce (2 tests) and TestCheckoutMerge (2 tests)

## Decisions Made

1. **Remove -a flag entirely rather than translate** - The semantic difference between git -a (stages tracked modified files) and sl -A (adds untracked files) is too dangerous. Simply removing the flag is the safest approach since git users expect staging before commit anyway.

2. **Use _translate_goto_flags helper function** - Centralizes flag translation logic for goto paths, making it easy to add more translations later.

3. **Apply translation only to goto paths** - File restoration (revert) paths don't need force/merge flag translation since they have different semantics.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - implementation was straightforward.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Safety foundations complete for commit, checkout, and branch commands
- Ready for next phase to add more flag compatibility
- All 4 SAFE requirements validated with passing tests

---
*Phase: 20-critical-safety-fixes*
*Completed: 2026-01-20*
