---
phase: 01-script-skeleton
plan: 01
subsystem: cli
tags: [python, argv, parsing, debug, shlex]

# Dependency graph
requires: []
provides:
  - gitsl.py script entry point with argument parsing
  - ParsedCommand dataclass for command/args extraction
  - GITSL_DEBUG environment variable support
  - Version and help flag handling
affects: [02-e2e-test-infra, 03-status-command, all-subsequent-phases]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-phase command extraction (extract command, preserve remaining args)"
    - "Environment variable for debug mode (GITSL_DEBUG)"
    - "main() returns int exit code with sys.exit(main()) guard"
    - "shlex.join() for safe command display"

key-files:
  created:
    - gitsl.py
  modified: []

key-decisions:
  - "Manual argv parsing instead of argparse for git-style command handling"
  - "Debug mode via environment variable (not CLI flag) to avoid consuming args"
  - "Accept multiple debug values: 1, true, yes, on (case-insensitive)"

patterns-established:
  - "ParsedCommand dataclass: command (Optional[str]), args (List[str]), raw_argv (List[str])"
  - "Debug output goes to stderr, not stdout"
  - "Exit 1 for no-args/usage, exit 0 for successful operations"

# Metrics
duration: 2min
completed: 2026-01-17
---

# Phase 1 Plan 1: Script Skeleton Summary

**Git-to-Sapling CLI shim entry point with ParsedCommand dataclass, argv parsing, and GITSL_DEBUG environment variable support**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-17T23:56:33Z
- **Completed:** 2026-01-17T23:58:59Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Created gitsl.py (125 lines) with complete argument parsing infrastructure
- Implemented ParsedCommand dataclass with command/args/raw_argv fields
- Added GITSL_DEBUG environment variable for showing what would execute
- Handled edge cases: empty args (exit 1), --version (exit 0), --help (exit 0)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create gitsl.py script skeleton with argument parsing** - `b0c2817` (feat)
2. **Task 2: Add type hints and verify Python 3.8+ compatibility** - no commit (verification-only, type hints already in Task 1)

## Files Created/Modified
- `gitsl.py` - Main CLI shim entry point with:
  - ParsedCommand dataclass
  - parse_argv() function
  - is_debug_mode() function
  - print_debug_info() function
  - main() entry point

## Decisions Made
- Used dataclass (not NamedTuple) for ParsedCommand as recommended in research
- Debug output goes to stderr to avoid polluting stdout
- Used shlex.join() for safe command display with proper quoting

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Script skeleton complete and ready for E2E test infrastructure (Phase 2)
- ParsedCommand structure ready for command translation (Phase 3+)
- Exports available: main, parse_argv, ParsedCommand, is_debug_mode

---
*Phase: 01-script-skeleton*
*Completed: 2026-01-17*
