---
phase: 04-direct-command-mappings
plan: 02
subsystem: cli
tags: [rev-parse, sapling, whereami, hash-truncation]

# Dependency graph
requires:
  - phase: 03-execution-pipeline
    provides: subprocess execution infrastructure
  - phase: 04-01
    provides: passthrough handler pattern
provides:
  - rev-parse --short HEAD handler with output truncation
  - sl_repo fixtures for Sapling-based testing
affects: [05-add-commit-push, all future sl-based tests]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - capture_output handler for special processing
    - output truncation for git compatibility

key-files:
  created:
    - cmd_rev_parse.py
    - tests/test_cmd_rev_parse.py
  modified:
    - gitsl.py
    - tests/conftest.py

key-decisions:
  - "Use subprocess.run with capture_output=True for rev-parse (not run_sl)"
  - "Truncate to 7 chars for git rev-parse --short compatibility"
  - "Accept args in any order (--short HEAD or HEAD --short)"

patterns-established:
  - "capture_output handler: For commands needing output processing before display"
  - "sl_repo fixtures: For testing against actual Sapling repositories"

# Metrics
duration: 3min
completed: 2026-01-18
---

# Phase 04 Plan 02: Rev-parse Handler Summary

**git rev-parse --short HEAD handler translating to sl whereami with 7-char truncation**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-18T03:47:34Z
- **Completed:** 2026-01-18T03:50:13Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Implemented rev-parse --short HEAD with output truncation
- Created sl_repo fixtures for Sapling repository testing
- Added 5 E2E tests covering output format and exit codes
- All 53 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Create rev-parse handler with output truncation** - `ac79820` (feat)
2. **Task 2: Add E2E tests for rev-parse command** - `7903482` (test)

## Files Created/Modified
- `cmd_rev_parse.py` - Handler for rev-parse command with capture_output and truncation
- `gitsl.py` - Added import and dispatch for rev-parse
- `tests/conftest.py` - Added sl_repo and sl_repo_with_commit fixtures
- `tests/test_cmd_rev_parse.py` - E2E tests for rev-parse command

## Decisions Made
- **capture_output pattern:** Unlike passthrough handlers, rev-parse uses subprocess.run with capture_output=True to process output before display
- **7-char truncation:** Git's rev-parse --short returns 7 characters by default; sl whereami returns 40, so we truncate
- **Argument order agnostic:** Check for presence of both "--short" and "HEAD" in args regardless of order
- **Explicit unsupported message:** Return helpful error for rev-parse variants we don't implement yet

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - execution was smooth.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Rev-parse handler complete
- sl_repo fixtures available for all future sl-based tests
- Ready for additional command handlers

---
*Phase: 04-direct-command-mappings*
*Completed: 2026-01-18*
