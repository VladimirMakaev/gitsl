---
phase: 28-clone-rm-mv-clean-config-flags
plan: 01
subsystem: cli
tags: [git, sapling, clone, rm, mv, clean, config, flags, translation]

# Dependency graph
requires:
  - phase: 27-grep-blame-flags
    provides: Flag extraction pattern established
provides:
  - Clone flag extraction and translation (-b -> -u, -n -> -U)
  - Rm flag extraction with warnings for unsupported flags
  - Mv flag extraction with -k warning
  - Clean flag extension for -x, -X, -e patterns
  - Config flag extraction and translation (--global -> --user, --unset -> --delete)
affects: [28-02-tests, phase-29]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Flag extraction loop with sl_args and remaining_args separation
    - Warning messages for unsupported flags

key-files:
  created: []
  modified:
    - cmd_clone.py
    - cmd_rm.py
    - cmd_mv.py
    - cmd_clean.py
    - cmd_config.py

key-decisions:
  - "Translate git clone -b to sl clone -u (update to bookmark)"
  - "Translate git clone -n to sl clone -U (no update)"
  - "Translate git config --global to sl config --user"
  - "Translate git config --unset to sl config --delete"
  - "Translate git config --show-origin to sl config --debug"
  - "Translate git clean -x to sl purge --ignored"
  - "Translate git clean -e to sl purge -X (exclude pattern)"
  - "Print warnings for unsupported flags rather than failing"

patterns-established:
  - "Warning pattern: Print to stderr with 'Warning:' prefix for unsupported flags"
  - "Flag extraction: Loop through args with index, handle both short and long forms"

# Metrics
duration: 2min
completed: 2026-01-22
---

# Phase 28 Plan 01: Clone, Rm, Mv, Clean, Config Flag Support Summary

**Full flag support for 5 utility commands with 30 flag translations and warnings covering CLON-01 through CONF-08**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-22T13:22:09Z
- **Completed:** 2026-01-22T13:24:29Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Extended cmd_clone.py with 9 flag handlers (CLON-01 through CLON-09)
- Extended cmd_rm.py and cmd_mv.py with 9 flag handlers combined (RM-01 through MV-04)
- Extended cmd_clean.py and cmd_config.py with 12 flag handlers combined (CLEN-01 through CONF-08)
- All critical translations in place: -b -> -u, -n -> -U, --global -> --user, --unset -> --delete, -x -> --ignored

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend cmd_clone.py with Flag Support** - `2b0998f` (feat)
2. **Task 2: Extend cmd_rm.py and cmd_mv.py with Flag Support** - `166416c` (feat)
3. **Task 3: Extend cmd_clean.py and cmd_config.py with Flag Support** - `7da860b` (feat)

## Files Modified
- `cmd_clone.py` - Clone flag extraction: -b -> -u, -n -> -U, warnings for --depth, --single-branch, etc.
- `cmd_rm.py` - Rm flag extraction: -f, -q pass-through, --cached and -n warnings
- `cmd_mv.py` - Mv flag extraction: -f, -n, -v pass-through, -k warning
- `cmd_clean.py` - Clean flag extension: -x -> --ignored, -e -> -X exclude, -X warning
- `cmd_config.py` - Config flag extraction: --global -> --user, --unset -> --delete, --show-origin -> --debug

## Decisions Made
- Translate git clone -b to sl clone -u (update to specific bookmark)
- Translate git clone -n to sl clone -U (no update/checkout)
- Translate git config --global to sl config --user (equivalent scope)
- Translate git config --unset to sl config --delete (equivalent operation)
- Translate git config --show-origin to sl config --debug (shows source file)
- Translate git clean -x to sl purge --ignored (include ignored files)
- Translate git clean -e pattern to sl purge -X pattern (exclude pattern)
- Print warnings for unsupported flags rather than failing (user-friendly)

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 5 command handlers extended with comprehensive flag support
- Ready for 28-02 plan to add E2E tests for these flags
- 30 flag behaviors to verify across clone, rm, mv, clean, and config commands

---
*Phase: 28-clone-rm-mv-clean-config-flags*
*Completed: 2026-01-22*
