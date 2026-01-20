# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-19)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.2 More Commands Support - COMPLETE

## Current Position

Phase: 19 of 19 (v1.2) - Complete
Plan: 02 of 02 (E2E tests for checkout)
Status: Phase complete - v1.2 complete
Last activity: 2026-01-20 - Completed 19-02-PLAN.md

Progress: [##########] 100% (v1.2 - 5 of 5 phases)

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)

## v1.2 Phase Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 15 | Direct pass-through commands | 13 | Complete |
| 16 | Flag translation commands | 8 | Complete |
| 17 | Branch and restore | 6 | Complete |
| 18 | Stash operations | 7 | Complete |
| 19 | Checkout command | 6 | Complete |

**Total v1.2 requirements:** 40
**Validated:** 40 of 40

## Performance Metrics

**Velocity:**
- Total plans completed: 30 (13 v1.0 + 7 v1.1 + 10 v1.2)
- Total phases completed: 19
- Total requirements validated: 21 v1.0 + 26 v1.1 + 40 v1.2

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 2 |
| v1.2 Commands | 5 | 10 | 2 |

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table.
All marked as "Good" during milestone completions.

**Phase 16 decisions:**
- Enforce git's safety model for clean (-f or -n required, exit 128 otherwise)
- Use --files --dirs for clean -d to properly remove directories (not just filter -d)
- Default to --local scope for config writes when no scope specified
- Combined short flags (e.g., -fd) must be parsed correctly

**Phase 17 decisions:**
- CRITICAL: Translate -D to -d for sl bookmark to prevent commit stripping (git -D only removes label, sl -D strips commits)
- Accept sl bookmark's update-on-duplicate behavior (silently updates existing bookmarks)
- Accept sl revert's exit 0 with stderr warning for nonexistent files

**Phase 18 decisions:**
- Subcommand dispatch pattern for handling push/pop/apply/list/drop
- Output capture with subprocess.run for _get_most_recent_shelve()
- Git-compatible error message for drop with no stashes

**Phase 19 decisions:**
- Use sl log -r exit code to validate revision instead of parsing output
- Error on ambiguity (both file and revision match) rather than silent priority

### Pending Todos

None - v1.2 complete.

### Blockers/Concerns

None.

### Research Notes (from v1.2 research)

Key pitfalls to address:
1. ~~**Checkout disambiguation** - Phase 19 must handle branch/file/commit ambiguity~~ DONE in 19-01/19-02
2. ~~**Clean data safety** - Phase 16 must enforce `-f` requirement before passing to sl purge~~ DONE in 16-01
3. ~~**Stash conflict handling** - Phase 18 must detect conflict state on pop~~ DONE in 18-01/18-02
4. ~~**Bookmark model mismatch** - Phase 17 should document git branch vs sl bookmark differences~~ DONE in 17-01/17-02

## Session Continuity

Last session: 2026-01-20 02:10 UTC
Stopped at: Completed 19-02-PLAN.md (v1.2 complete)
Resume with: Next milestone planning
