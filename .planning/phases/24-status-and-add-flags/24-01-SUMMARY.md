---
phase: 24-status-and-add-flags
plan: 01
subsystem: cli
tags: [status, add, flags, sl, sapling]

# Dependency graph
requires:
  - phase: 23-diff-and-show-flags
    provides: Flag translation patterns and warning patterns
provides:
  - Status flag translation with 5 flags (STAT-01 through STAT-05)
  - Add flag translation with 3 flags (ADD-03 through ADD-05)
  - Warnings for unsupported git features (-f/--force for add)
affects: [24-status-and-add-flags, testing-phases]

# Tech tracking
tech-stack:
  added: []
  patterns: [flag-translation-with-warnings, branch-header-query, untracked-mode-filtering]

key-files:
  created: []
  modified: [cmd_status.py, cmd_add.py]

key-decisions:
  - "Use sl log template for branch header in status -b output"
  - "Print note for -v/--verbose since Sapling -v has different meaning"
  - "Print warning for -f/--force since Sapling cannot force-add ignored files"

patterns-established:
  - "Branch query: sl log -r . --template {activebookmark}"
  - "Untracked mode filtering: -mard flag to exclude untracked files"

# Metrics
duration: 4min
completed: 2026-01-21
---

# Phase 24 Plan 01: Status and Add Flags Summary

**Status and add flag translation with support for --ignored, -b/--branch, -u modes, --dry-run, and --verbose**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-21T17:55:46Z
- **Completed:** 2026-01-21T17:59:58Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Extended cmd_status.py with 5 flag translations (STAT-01 through STAT-05)
- Extended cmd_add.py with 3 flag translations (ADD-03 through ADD-05)
- Implemented --ignored flag for showing ignored files (!! in porcelain)
- Implemented -b/--branch flag for branch header in status output
- Implemented -u/--untracked-files modes (no/normal/all) for filtering untracked
- Implemented --dry-run/-n for add preview mode
- Implemented warning for -f/--force (Sapling limitation)
- Implemented -v/--verbose for showing files being added

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend cmd_status.py with STAT-01 through STAT-05 flags** - `78978bb` (feat)
2. **Task 2: Extend cmd_add.py with ADD-03 through ADD-05 flags** - `1675fba` (feat)

## Files Created/Modified
- `cmd_status.py` - Extended from 110 to 195 lines with 5 flag translations and branch header support
- `cmd_add.py` - Extended from 78 to 151 lines with 3 flag translations and refactored handler structure

## Decisions Made
- Use `sl log -r . --template "{activebookmark}"` to query current branch name for -b/--branch output. If empty, show "(detached)".
- Print a note for -v/--verbose flag since Sapling -v shows repo state info, not staged diffs like git.
- Print a warning for -f/--force flag since Sapling cannot force-add ignored files. Continue with normal add operation.
- Use -mard filter for -uno (untracked mode: no) to show only modified, added, removed, deleted files.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Verification Results

All 24 existing tests pass (11 status + 13 add):
- TestPorcelainUntracked (2 tests)
- TestPorcelainAdded (1 test)
- TestPorcelainModified (1 test)
- TestPorcelainRemoved (1 test)
- TestPorcelainMissing (1 test)
- TestPorcelainCleanRepo (1 test)
- TestPorcelainMixedStates (1 test)
- TestShortFlag (2 tests)
- TestNormalStatusPassthrough (1 test)
- TestAddBasic (2 tests)
- TestAddAll (3 tests)
- TestAddUpdate (5 tests)
- TestAddDot (3 tests)

Manual verification of new flags:
- `git status --ignored --porcelain` shows ignored files with !! code
- `git status -b --short` shows `## branch` header
- `git status -uno --porcelain` suppresses untracked files
- `git add -n file` shows preview without adding
- `git add -f file` prints warning about Sapling limitation
- `git add -A -n` shows all files that would be added/removed

## Next Phase Readiness
- Status and add commands fully support common git flags
- Ready for Phase 24-02 tests
- All 8 requirements (STAT-01 through STAT-05, ADD-03 through ADD-05) implemented

---
*Phase: 24-status-and-add-flags*
*Completed: 2026-01-21*
