# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.3 Flag Compatibility — Phase 24 (Status and Add Flags)

## Current Position

Milestone: v1.3 Flag Compatibility
Phase: 24 - Status and Add Flags
Plan: 01 of 02 complete
Status: In progress
Last activity: 2026-01-21 — Completed 24-01-PLAN.md

Progress: [####......] 4/10 phases

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)
- v1.3 Flag Compatibility - 10 phases (in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 37 (13 v1.0 + 7 v1.1 + 10 v1.2 + 7 v1.3)
- Total phases completed: 23
- Total requirements validated: 184 (21 v1.0 + 26 v1.1 + 40 v1.2 + 97 v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 1 |
| v1.2 Commands | 5 | 10 | 2 |
| v1.3 Flags | 4 | 7 | — |

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table.
All marked as "Good" during milestone completions.

**Phase 20-01 Decisions:**
- Remove -a/--all from commit entirely rather than translate (semantic difference too dangerous)
- Translate -f/--force to -C for goto paths (matches sl goto -C semantics)
- Pass through -m/--merge to -m for goto paths (same semantics in sl)

**Phase 21-01 Decisions:**
- Translate HEAD to . for Sapling revset compatibility in --verify handler
- Return .sl or .hg directory for --git-dir based on which exists
- Always return exit code 0 for --is-inside-work-tree (git behavior)

**Phase 22-01 Decisions:**
- Print warning for -S/-G pickaxe with grep alternative (no sl equivalent)
- Use revset approximations for --first-parent and --reverse
- Template priority: custom_template > name_status > name_only > decorate > oneline

**Phase 23-01 Decisions:**
- Use sl status -mard for diff --name-only/--name-status in working directory
- Print warnings for staging area flags (--staged/--cached) since Sapling has no staging
- Reuse PRETTY_PRESETS and GIT_TO_SL_PLACEHOLDERS pattern from cmd_log.py

**Phase 23-02 Decisions:**
- Test sl show template behavior as-is (templates format header, diff appended by sl)
- Verify warning presence in stderr rather than exact message text

**Phase 24-01 Decisions:**
- Use sl log template for branch header in status -b output
- Print note for -v/--verbose since Sapling -v has different meaning
- Print warning for -f/--force since Sapling cannot force-add ignored files

### Pending Todos

None — ready for Phase 24-02 tests.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-21
Stopped at: Completed 24-01-PLAN.md
Resume with: `/gsd:execute-phase` to continue with 24-02-PLAN.md (tests)
