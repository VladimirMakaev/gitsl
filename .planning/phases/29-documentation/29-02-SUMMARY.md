---
phase: 29-documentation
plan: 02
subsystem: documentation
tags: [readme, flag-tables, stash, checkout, switch, restore, grep, blame, clone, rm, mv, clean, config]

# Dependency graph
requires:
  - phase: 26-stash-and-checkout-switch-restore-flags
    provides: STSH-01 to STSH-10, CHKT-01 to CHKT-11 implementations
  - phase: 27-grep-and-blame-flags
    provides: GREP-01 to GREP-14, BLAM-01 to BLAM-07 implementations
  - phase: 28-clone-rm-mv-clean-config-flags
    provides: CLON-01 to CLON-09, RM-01 to RM-05, MV-01 to MV-04, CLEN-01 to CLEN-04, CONF-01 to CONF-08 implementations
provides:
  - Complete flag documentation for stash, checkout, switch, restore in README
  - Complete flag documentation for grep, blame, clone, show in README
  - Complete flag documentation for rm, mv, clean, config, rev-parse in README
  - All 19 commands marked Full status (no Partial)
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Flag tables with Supported/Translation/Notes columns
    - Critical warnings for non-obvious translations

key-files:
  created: []
  modified:
    - README.md

key-decisions:
  - "Document stash@{n} syntax with shelve name lookup explanation"
  - "Highlight critical translations (grep -v to -V, blame -b to --ignore-space-change) prominently"
  - "Cross-reference checkout/switch/restore for users migrating from old git checkout"
  - "Mark rev-parse as Full status with 7 flags documented"

patterns-established:
  - "Three-column flag table format: Flag | Supported | Translation/Notes"
  - "Warning status for staging-related flags with explanation"
  - "Critical notes section for translations that differ from expectations"

# Metrics
duration: 3min
completed: 2026-01-23
---

# Phase 29 Plan 02: Flag Tables for Stash, Checkout, Grep, Blame, Clone, Rm, Mv, Clean, Config Summary

**Complete flag documentation for 11 commands (stash, checkout, switch, restore, grep, blame, clone, show, rm, mv, clean, config) with critical warnings for non-obvious translations like grep -v to -V and blame -b to --ignore-space-change**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-23T02:20:25Z
- **Completed:** 2026-01-23T02:23:33Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- git stash: 18 flags including stash@{n} lookup, -p/-i interactive mode, branch subcommand
- git checkout/switch/restore: Complete CHKT-01 to CHKT-11 with safety flags (-f/-m) and cross-references
- git grep: 14 flags with CRITICAL warning about -v to -V translation
- git blame: 7 flags with CRITICAL warning about -b translation
- git clone: 9 flags with -b/-u and -n/-U translations
- git rm, mv, clean, config: All flags documented with translations
- git rev-parse: Upgraded to Full status with 7 flags (was Partial)
- All 19 commands now marked Full in Supported Commands table

## Task Commits

Each task was committed atomically:

1. **Task 1: Update stash, checkout, switch, restore flag tables** - `33aa07a` (docs)
2. **Task 2: Add grep, blame, clone flag tables** - `05d5be9` (docs)
3. **Task 3: Update rm, mv, clean, config tables and final polish** - `22388ea` (docs)

## Files Created/Modified
- `README.md` - Complete command reference with all v1.3 flag tables

## Decisions Made
- Documented stash@{n} syntax with explanation of shelve name lookup mechanism
- Placed critical warnings for grep -v and blame -b prominently in both Common Flag Translations and individual sections
- Added cross-references between checkout, switch, restore for users migrating from old git checkout workflow
- Updated rev-parse from Partial to Full status now that 7 flags are documented

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- README documentation is complete for v1.3 Flag Compatibility milestone
- All 217 v1.3 requirements are now reflected in documentation
- Ready for milestone completion verification

---
*Phase: 29-documentation*
*Completed: 2026-01-23*
