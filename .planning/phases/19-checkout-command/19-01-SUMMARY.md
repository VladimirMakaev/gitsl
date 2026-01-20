---
phase: 19-checkout-command
plan: 01
subsystem: cli
tags: [checkout, goto, revert, bookmark, disambiguation]

# Dependency graph
requires:
  - phase: 17-branch-and-restore
    provides: cmd_switch.py flag detection pattern, cmd_restore.py revert passthrough
  - phase: 18-stash-operations
    provides: cmd_stash.py subprocess output capture pattern
provides:
  - cmd_checkout.py with full disambiguation logic
  - CHECKOUT-01 through CHECKOUT-06 requirement implementations
affects: [19-02-tests, future checkout enhancements]

# Tech tracking
tech-stack:
  added: []
  patterns: [revision validation via sl log -r, double-dash separator handling]

key-files:
  created: [cmd_checkout.py]
  modified: [gitsl.py]

key-decisions:
  - "Use sl log -r exit code to validate revision instead of parsing output"
  - "Error on ambiguity (both file and revision match) rather than silent priority"

patterns-established:
  - "_is_valid_revision(): subprocess capture pattern for checking revision validity"
  - "_split_at_separator(): double-dash argument splitting pattern"

# Metrics
duration: 2min
completed: 2026-01-20
---

# Phase 19 Plan 01: Checkout Command Handler Summary

**Checkout command handler with full disambiguation logic for branch, commit, and file operations via sl goto/revert/bookmark**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-20T01:51:41Z
- **Completed:** 2026-01-20T01:53:27Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created cmd_checkout.py with disambiguation logic for CHECKOUT-01 through CHECKOUT-06
- Implemented _is_valid_revision() to check if argument is valid revision via sl log -r
- Added _split_at_separator() for proper handling of -- file separator
- Created _handle_create_branch() for git checkout -b/-B branch creation
- Integrated checkout dispatch into gitsl.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Create checkout command handler with disambiguation** - `70de99a` (feat)
2. **Task 2: Update gitsl.py dispatch routing** - `652616c` (feat)

## Files Created/Modified
- `cmd_checkout.py` - Checkout command handler with disambiguation (155 lines)
- `gitsl.py` - Added import and dispatch for checkout command

## Decisions Made
- Use sl log -r exit code to validate revision: Simple, handles all revset syntax
- Error on ambiguity instead of silent priority: Matches git behavior, prevents wrong operation
- Use Tuple type hint for Python 3.8+ compatibility

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Checkout command implementation complete
- Ready for E2E tests in 19-02-PLAN.md
- All 6 CHECKOUT requirements implemented:
  - CHECKOUT-01: checkout <commit> -> goto <commit>
  - CHECKOUT-02: checkout <branch> -> goto <bookmark>
  - CHECKOUT-03: checkout <file> -> revert <file>
  - CHECKOUT-04: checkout -- <file> -> revert <file>
  - CHECKOUT-05: checkout -b <name> -> bookmark + goto
  - CHECKOUT-06: disambiguation logic with clear error

---
*Phase: 19-checkout-command*
*Completed: 2026-01-20*
