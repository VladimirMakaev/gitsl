---
phase: 23-diff-and-show-flags
plan: 01
subsystem: cli
tags: [diff, show, flags, templates, sl, sapling]

# Dependency graph
requires:
  - phase: 22-log-flags
    provides: Flag translation patterns and template system
provides:
  - Diff flag translation with 12 flags (DIFF-01 through DIFF-12)
  - Show flag translation with 8 flags (SHOW-01 through SHOW-08)
  - Warnings for unsupported git features (--staged, -M, -C, --word-diff, --color-moved)
affects: [23-diff-and-show-flags, testing-phases]

# Tech tracking
tech-stack:
  added: []
  patterns: [flag-translation-with-warnings, sl-status-for-name-only, template-based-output]

key-files:
  created: []
  modified: [cmd_diff.py, cmd_show.py]

key-decisions:
  - "Use sl status -mard for diff --name-only/--name-status in working directory"
  - "Print warnings for staging area flags (--staged/--cached) since Sapling has no staging"
  - "Reuse PRETTY_PRESETS and GIT_TO_SL_PLACEHOLDERS pattern from cmd_log.py"

patterns-established:
  - "Warning pattern: print to stderr, skip flag, continue execution"
  - "Template priority: custom_template > name_status > name_only > no_patch > oneline"

# Metrics
duration: 3min
completed: 2026-01-21
---

# Phase 23 Plan 01: Diff and Show Flags Summary

**Diff and show flag translation with warnings for unsupported git features and templates for output formatting**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-21T15:17:30Z
- **Completed:** 2026-01-21T15:19:59Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Extended cmd_diff.py with 12 flag translations (DIFF-01 through DIFF-12)
- Extended cmd_show.py with 8 flag translations (SHOW-01 through SHOW-08)
- Implemented warnings for unsupported git features (--staged, --raw, -M, -C, --word-diff, --color-moved)
- Added template-based output formatting for show (--oneline, --name-only, --name-status, -s, --pretty)

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend cmd_diff.py with flag translation** - `871a378` (feat)
2. **Task 2: Extend cmd_show.py with flag translation and templates** - `eba6250` (feat)

## Files Created/Modified
- `cmd_diff.py` - Extended from 13 to 160 lines with 12 flag translations and warnings
- `cmd_show.py` - Extended from 17 to 184 lines with 8 flag translations, templates, and format placeholders

## Decisions Made
- Use `sl status -mard` for `git diff --name-only/--name-status` when comparing working directory (no commits specified). For commit diffs, pass through with a note about potential format differences.
- Print clear warnings for staging area concepts (--staged/--cached) explaining Sapling has no staging area.
- Copied PRETTY_PRESETS and GIT_TO_SL_PLACEHOLDERS pattern from cmd_log.py for consistency rather than extracting to common module (avoiding premature abstraction).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Diff and show commands fully support common git flags
- Ready for Phase 23-02 tests
- All 20 requirements (DIFF-01 through DIFF-12, SHOW-01 through SHOW-08) implemented

---
*Phase: 23-diff-and-show-flags*
*Completed: 2026-01-21*
