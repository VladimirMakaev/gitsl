# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.3 Flag Compatibility — Phase 23 Complete

## Current Position

Milestone: v1.3 Flag Compatibility
Phase: 23 - Diff and Show Flags (complete)
Plan: 02 of 2 (in phase) - complete
Status: Phase 23 complete, ready for Phase 24
Last activity: 2026-01-21 — Completed 23-02-PLAN.md

Progress: [###.......] 3/10 phases

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)
- v1.3 Flag Compatibility - 10 phases (in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 36 (13 v1.0 + 7 v1.1 + 10 v1.2 + 6 v1.3)
- Total phases completed: 22
- Total requirements validated: 176 (21 v1.0 + 26 v1.1 + 40 v1.2 + 89 v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 1 |
| v1.2 Commands | 5 | 10 | 2 |
| v1.3 Flags | 3 | 6 | — |

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

### Pending Todos

None — ready for Phase 24.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-21
Stopped at: Completed 23-02-PLAN.md
Resume with: Execute Phase 24 for next v1.3 Flag Compatibility work
