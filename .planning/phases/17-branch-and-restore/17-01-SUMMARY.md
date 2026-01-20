---
phase: 17-branch-and-restore
plan: 01
subsystem: command-handlers
tags: [branch, restore, bookmark, revert, safety-translation]

dependency-graph:
  requires:
    - "16-flag-translation: established cmd_*.py pattern with flag translation"
    - "03-infrastructure: common.py with ParsedCommand and run_sl"
  provides:
    - "cmd_branch.py: git branch -> sl bookmark with -D safety"
    - "cmd_restore.py: git restore -> sl revert"
    - "dispatch routing for branch and restore commands"
  affects:
    - "17-02: E2E tests will validate these handlers"

tech-stack:
  added: []
  patterns:
    - "flag-safety-translation: -D to -d for sl bookmark to prevent commit stripping"
    - "direct-passthrough: restore -> revert with argument forwarding"

key-files:
  created:
    - "cmd_branch.py"
    - "cmd_restore.py"
  modified:
    - "gitsl.py"

decisions:
  - id: "SAFETY-D-FLAG"
    choice: "Always translate -D to -d for sl bookmark"
    rationale: "git branch -D only removes label; sl bookmark -D strips commits (destructive)"

metrics:
  duration: "~5 min"
  completed: "2026-01-20"
---

# Phase 17 Plan 01: Branch and Restore Handlers Summary

**One-liner:** Branch and restore command handlers with critical -D to -d safety translation for sl bookmark

## What Was Built

Created two command handlers following the established cmd_*.py pattern:

1. **cmd_branch.py** - Translates `git branch` to `sl bookmark`
   - List bookmarks: `git branch` -> `sl bookmark`
   - Create bookmark: `git branch <name>` -> `sl bookmark <name>`
   - Delete bookmark: `git branch -d <name>` -> `sl bookmark -d <name>`
   - **Safety translation:** `git branch -D <name>` -> `sl bookmark -d <name>` (NOT -D)

2. **cmd_restore.py** - Translates `git restore` to `sl revert`
   - Restore file: `git restore <file>` -> `sl revert <file>`
   - Restore all: `git restore .` -> `sl revert .`

3. **gitsl.py dispatch** - Added routing for both commands

## Critical Safety Feature

The most important aspect of this plan is the `-D` to `-d` translation for branch deletion:

- **Git behavior:** `git branch -D` force-deletes the branch label, but commits remain accessible
- **Sapling behavior:** `sl bookmark -D` deletes the bookmark AND strips/hides the associated commits
- **gitsl translation:** Both `-d` and `-D` map to `sl bookmark -d` to preserve commits

This prevents users from accidentally losing work when using familiar git commands.

## Key Files

| File | Purpose |
|------|---------|
| cmd_branch.py | Handler for git branch with -D safety |
| cmd_restore.py | Handler for git restore passthrough |
| gitsl.py | Updated dispatch routing |

## Verification Completed

- Python syntax validation for all files
- Debug mode tests confirm commands are recognized
- All debug output shows commands routed (not "unsupported")

## Commits

| Hash | Description |
|------|-------------|
| 20331fb | feat(17-01): create branch and restore command handlers |
| 9567239 | feat(17-01): add dispatch routing for branch and restore |

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

Ready for 17-02 (E2E tests):
- Handlers implement all requirements (BRANCH-01 through BRANCH-04, RESTORE-01, RESTORE-02)
- Safety translation verified in code
- Patterns established for test fixtures (sl_repo_with_commit required for bookmark tests)
