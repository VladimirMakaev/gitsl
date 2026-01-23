---
phase: 29-documentation
plan: 01
subsystem: docs
tags: [readme, documentation, flag-compatibility, user-facing]

# Dependency graph
requires:
  - phase: 20-28
    provides: All flag implementations documented in 29-RESEARCH.md
provides:
  - Updated README.md with Staging Area Limitations section
  - Common Flag Translations quick reference
  - Comprehensive flag tables for log, diff, show
  - Updated status, add, commit, branch, rev-parse sections
affects: [user-documentation, onboarding]

# Tech tracking
tech-stack:
  added: []
  patterns: [consistent-flag-tables, staged-flags-documentation]

key-files:
  created: []
  modified:
    - README.md

key-decisions:
  - "Document staging area limitations prominently for git users migrating to Sapling"
  - "Use consistent table format: Flag | Supported | Translation/Notes"
  - "Change rev-parse status from Partial to Full in Supported Commands table"

patterns-established:
  - "Flag documentation format: three-column tables with translation notes"
  - "Warning pattern: explain behavior differences rather than just saying 'unsupported'"

# Metrics
duration: 8min
completed: 2026-01-23
---

# Phase 29 Plan 01: README Flag Documentation Summary

**Added Staging Area Limitations section, Common Flag Translations reference, and comprehensive flag tables for log (21 flags), diff (13 flags), show (9 flags), status, add, commit, branch, and rev-parse (7 flags)**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-23T09:00:00Z
- **Completed:** 2026-01-23T09:08:00Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- Added Staging Area Limitations section explaining Sapling has no staging area
- Added Common Flag Translations quick reference table with critical translations highlighted
- Updated git log section from 2 flags to 21 flags with accurate translation info
- Added NEW git diff section with 13 flags
- Updated git show section from generic to specific 9 flags
- Expanded status, add, commit, branch sections with new flags
- Updated rev-parse from "Partial" (1 flag) to "Full" (7 flags)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Staging Area Limitations and Common Translations sections** - `cee3a93` (docs)
2. **Task 2+3: Update log, diff, show, status, add, commit, branch, rev-parse flag tables** - `f6be914` (docs)

## Files Created/Modified
- `README.md` - Updated with comprehensive flag compatibility documentation

## Decisions Made
- Changed rev-parse status from "Partial" to "Full" in Supported Commands table since all 7 flags are now implemented
- Used consistent three-column table format across all command sections
- Documented staging area limitations prominently for users migrating from git

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- "File has been modified since read" errors during Edit operations - resolved by using Write tool for full file update

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- README now accurately reflects v1.3 Flag Compatibility implementation
- Plan 29-02 handles remaining commands (stash, checkout, grep, blame, etc.)

---
*Phase: 29-documentation*
*Completed: 2026-01-23*
