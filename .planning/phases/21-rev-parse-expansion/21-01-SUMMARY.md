---
phase: 21-rev-parse-expansion
plan: 01
subsystem: commands
tags: [rev-parse, git, sapling, repository-metadata, cli]

# Dependency graph
requires:
  - phase: 01-core-foundation
    provides: command routing infrastructure and ParsedCommand abstraction
provides:
  - Rev-parse command with 6 new flag handlers (REVP-01 through REVP-06)
  - Repository metadata queries (root, VCS dir, work tree status)
  - Current bookmark/branch name resolution
  - Commit reference validation
affects: [future-rev-parse-extensions, ide-integrations, ci-scripts]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Handler function pattern for rev-parse flags (_handle_*)
    - HEAD to . translation for Sapling compatibility

key-files:
  created: []
  modified:
    - cmd_rev_parse.py
    - tests/test_rev_parse.py

key-decisions:
  - "Translate HEAD to . for Sapling revset compatibility in --verify handler"
  - "Return .sl or .hg directory for --git-dir based on which exists"
  - "Always return exit code 0 for --is-inside-work-tree (git behavior)"

patterns-established:
  - "_handle_* function naming for flag-specific handlers in cmd_rev_parse.py"
  - "HEAD → . translation for Sapling compatibility"

# Metrics
duration: 35min
completed: 2026-01-21
---

# Phase 21 Plan 01: Rev-Parse Expansion Summary

**Expanded git rev-parse with 6 new flag handlers for repository metadata queries (--show-toplevel, --git-dir, --is-inside-work-tree, --abbrev-ref, --verify, --symbolic)**

## Performance

- **Duration:** 35 min
- **Started:** 2026-01-21T01:25:51Z
- **Completed:** 2026-01-21T02:00:37Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Implemented 6 new rev-parse flag handlers enabling tools like VSCode, shell prompts, and CI scripts to query repository metadata
- Added comprehensive E2E test coverage with 14 new tests (19 total for rev-parse)
- All 211 tests pass with no regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement rev-parse flag handlers** - `b47c617` (feat)
2. **Task 1 fix: HEAD translation** - `045515d` (fix)
3. **Task 2: Add E2E tests** - `0e8f3df` (test)

## Files Created/Modified

- `cmd_rev_parse.py` - Added 6 handler functions and dispatcher logic for new rev-parse flags
- `tests/test_rev_parse.py` - Added 6 new test classes covering REVP-01 through REVP-06

## Decisions Made

1. **Translate HEAD to . for Sapling compatibility** - Sapling uses `.` instead of `HEAD` for current commit in revsets. The `--verify HEAD` command must translate to `sl log -r . -T {node}`.

2. **Check for .sl before .hg for --git-dir** - Newer Sapling uses .sl directory, older installations use .hg. Check .sl first, fall back to .hg if not found.

3. **Always return exit 0 for --is-inside-work-tree** - Git returns exit code 0 even outside a repository (outputs "false"). Matched this behavior for compatibility.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] HEAD not valid Sapling revset**
- **Found during:** Task 2 (E2E test execution)
- **Issue:** `git rev-parse --verify HEAD` failed because Sapling doesn't recognize HEAD as a revset
- **Fix:** Added HEAD to . translation in _handle_verify function
- **Files modified:** cmd_rev_parse.py
- **Verification:** All verify tests pass (3/3)
- **Committed in:** 045515d

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential fix for Sapling compatibility. No scope creep.

## Issues Encountered

None beyond the HEAD translation fix documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Rev-parse expansion complete with all 6 flags working
- Ready for Phase 22 (next v1.3 phase)
- All REVP-01 through REVP-07 requirements satisfied

---
*Phase: 21-rev-parse-expansion*
*Completed: 2026-01-21*
