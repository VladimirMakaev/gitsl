# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.3 Flag Compatibility — Phase 23 (Diff and Show Flags)

## Current Position

Milestone: v1.3 Flag Compatibility
Phase: 23 - Diff and Show Flags
Plan: 01 of 2 (in phase)
Status: Plan 01 complete, ready for Plan 02 (tests)
Last activity: 2026-01-21 — Completed 23-01-PLAN.md

Progress: [###.......] 3/10 phases

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)
- v1.3 Flag Compatibility - 10 phases (in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 35 (13 v1.0 + 7 v1.1 + 10 v1.2 + 5 v1.3)
- Total phases completed: 22
- Total requirements validated: 156 (21 v1.0 + 26 v1.1 + 40 v1.2 + 69 v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 1 |
| v1.2 Commands | 5 | 10 | 2 |
| v1.3 Flags | 3 | 5 | — |

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

### Pending Todos

None — ready for Phase 23-02.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-21
Stopped at: Completed 23-01-PLAN.md
Resume with: Execute 23-02-PLAN.md for Diff and Show Flags tests
