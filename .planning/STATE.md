# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.3 Flag Compatibility — Phase 26 (Stash and Checkout/Switch/Restore Flags)

## Current Position

Milestone: v1.3 Flag Compatibility
Phase: 26 - Stash and Checkout/Switch/Restore Flags
Plan: Not started
Status: Ready for planning
Last activity: 2026-01-21 — Phase 25 verified and complete

Progress: [######....] 6/10 phases

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)
- v1.3 Flag Compatibility - 10 phases (in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 40 (13 v1.0 + 7 v1.1 + 10 v1.2 + 10 v1.3)
- Total phases completed: 25
- Total requirements validated: 211 (21 v1.0 + 26 v1.1 + 40 v1.2 + 124 v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 1 |
| v1.2 Commands | 5 | 10 | 2 |
| v1.3 Flags | 6 | 10 | — |

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

**Phase 24-02 Decisions:**
- Test -v/--verbose by verifying files get added, not by checking output (sl add has no verbose output)
- Use sl_repo_with_ignored and sl_repo_with_bookmark fixtures for specialized test scenarios

**Phase 25-01 Decisions:**
- sl amend defaults to no-edit, so add -e flag for git's default editor behavior
- signoff implemented via custom trailer appending, not sl config
- branch -c uses two-step: get commit hash, create new bookmark
- verbose branch uses template instead of sl -v flag

**Phase 25-02 Decisions:**
- Skip -e flag when message provided via -m or -F with --amend (bug fix)
- Test verbose by checking for colon in output (template format)
- Test track flag by verifying command acceptance, not tracking behavior

### Pending Todos

None — Phase 25 complete, ready for Phase 26.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-21
Stopped at: Phase 25 verified and complete
Resume with: `/gsd:plan-phase 26` to plan Stash and Checkout/Switch/Restore Flags phase
