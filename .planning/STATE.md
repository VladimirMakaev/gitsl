# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-17)

**Core value:** Git commands used by get-shit-done execute correctly against Sapling repos
**Current focus:** Phase 9 - Unsupported Command Handling

## Current Position

Phase: 9 of 9 (Unsupported Command Handling)
Plan: 0 of ? in current phase
Status: Ready to plan
Last activity: 2026-01-18 - Phase 8 complete and verified

Progress: [████████..] 88%

## Performance Metrics

**Velocity:**
- Total plans completed: 11
- Average duration: 2.9 min
- Total execution time: 33 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-script-skeleton | 1 | 2 min | 2 min |
| 02-e2e-test-infrastructure | 2 | 6 min | 3 min |
| 03-execution-pipeline | 2 | 4 min | 2 min |
| 04-direct-command-mappings | 2 | 6 min | 3 min |
| 05-file-operation-commands | 1 | 3 min | 3 min |
| 06-status-output-emulation | 1 | 4 min | 4 min |
| 07-log-output-emulation | 1 | 3 min | 3 min |
| 08-add-u-emulation | 1 | 5 min | 5 min |

**Recent Trend:**
- Last 5 plans: 3 min, 3 min, 4 min, 3 min, 5 min
- Trend: stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- E2E testing is foundational - Phase 2 dedicated to test infrastructure
- Golden-master approach: compare git vs gitsl output on temp repos
- Exact match for porcelain formats, semantic match for human-readable
- Manual argv parsing instead of argparse for git-style command handling
- Debug mode via environment variable (GITSL_DEBUG) to avoid consuming args
- **Multi-file architecture**: gitsl.py entry point only, common.py shared logic, one file per command (cmd_*.py)
- **pytest.ini with pythonpath:** Configured `pythonpath = tests` for module discovery
- **.gitignore:** Added standard Python gitignore entries
- **Path.resolve() for symlink handling:** Use Path.resolve() when comparing paths on macOS
- **Handler interface:** handle(ParsedCommand) -> int for all command handlers in cmd_*.py
- **subprocess.run() defaults:** No PIPE, no capture_output - real-time I/O passthrough
- **sys.executable in tests:** Use sys.executable for portable Python invocation
- **capture_output pattern:** For commands needing output processing (e.g., rev-parse), use subprocess.run with capture_output=True
- **sl_repo fixtures:** Added for Sapling-based testing in conftest.py
- **Flag translation pattern:** git add -A/--all translates to sl addremove (not sl add with flags)
- **Status code mapping:** sl M -> git ' M' (space+M), sl A -> git 'A ' (A+space), sl R -> git 'D ' (D+space)
- **Porcelain output pattern:** SL_TO_GIT_STATUS dict + transform_to_porcelain function
- **sl-template-output pattern:** Use sl -T flag with template string for custom output formats
- **multi-variant-flag-parsing:** Handle multiple flag formats (-N, -n N, -nN, --flag=N) with unified translation
- **Sapling auto-stages modified files:** Modified tracked files require no action in Sapling (unlike Git which requires explicit add)

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-01-18
Stopped at: Phase 8 complete and verified, ready for Phase 9 planning
Resume file: None
