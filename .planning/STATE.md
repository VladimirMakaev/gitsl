# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference
**Current focus:** v1.3 Flag Compatibility — Phase 27 Plan 01 complete, ready for Plan 02

## Current Position

Milestone: v1.3 Flag Compatibility
Phase: 27 - Grep and Blame Flags
Plan: 01 of 02 complete
Status: In progress
Last activity: 2026-01-22 — Completed 27-01-PLAN.md

Progress: [#######...] 7/10 phases

## Milestones

- v1.0 MVP - 9 phases, 13 plans (shipped 2026-01-18)
- v1.1 Polish & Documentation - 5 phases, 7 plans (shipped 2026-01-19)
- v1.2 More Commands Support - 5 phases, 10 plans (shipped 2026-01-20)
- v1.3 Flag Compatibility - 10 phases (in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 43 (13 v1.0 + 7 v1.1 + 10 v1.2 + 13 v1.3)
- Total phases completed: 26
- Total requirements validated: 253 (21 v1.0 + 26 v1.1 + 40 v1.2 + 166 v1.3)

**By Milestone:**

| Milestone | Phases | Plans | Days |
|-----------|--------|-------|------|
| v1.0 MVP | 9 | 13 | 1 |
| v1.1 Polish | 5 | 7 | 1 |
| v1.2 Commands | 5 | 10 | 2 |
| v1.3 Flags | 7 | 13 | — |

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

**Phase 26-01 Decisions:**
- Parse stash@{n} syntax and lookup shelve name via sl shelve --list
- Translate -p/--patch to -i for interactive shelving
- Implement stash branch as bookmark creation + unshelve
- Translate --detach to --inactive for goto
- Accept track flag with note about limited emulation

**Phase 26-02 Decisions:**
- Test stash@{n} by creating multiple stashes and verifying index-to-name translation
- Verify warning messages by checking stderr contains relevant keywords
- Test interactive mode (-p) by checking flag acceptance rather than behavior

**Phase 27-01 Decisions:**
- Translate git grep -v to sl grep -V (sl uses uppercase V for invert match)
- Translate git blame -b to sl --ignore-space-change (sl -b means blank SHA1)
- Do not pass through git blame -l (sl -l means line number, not long hash)
- Do not pass through git grep -h (sl -h shows help, not filename suppression)

### Pending Todos

None — Phase 27-01 complete, ready for Phase 27-02 (Grep and Blame Flags Tests).

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-22
Stopped at: Completed 27-01-PLAN.md
Resume with: `/gsd:execute-plan .planning/phases/27-grep-and-blame-flags/27-02-PLAN.md` for tests
