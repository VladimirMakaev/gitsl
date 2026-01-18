---
phase: 08-add-u-emulation
plan: 01
subsystem: command-translation
tags: [git-add, update-flag, staging, sapling]

dependency-graph:
  requires:
    - 05-file-operation-commands (cmd_add.py base implementation)
  provides:
    - FLAG-03: git add -u/--update emulation
    - Deleted file marking via sl remove --mark
  affects:
    - 09-unsupported-command-handling (pattern for flag-specific logic)

tech-stack:
  added: []
  patterns:
    - capture-output-pattern: subprocess.run with capture_output=True for sl status
    - conditional-flag-handling: check for -u/--update before -A/--all dispatch

key-files:
  created: []
  modified:
    - cmd_add.py
    - tests/test_cmd_add.py

decisions:
  - id: D-0801
    decision: "Modified tracked files require no action in Sapling (auto-staged)"
    rationale: "Sapling auto-includes modified tracked files in commits unlike Git"

metrics:
  duration: 5 min
  completed: 2026-01-18
---

# Phase 8 Plan 1: Add -u Emulation Summary

Implemented git add -u flag to stage only tracked files, handling the key difference between Git and Sapling staging models.

## One-liner

git add -u marks deleted files for removal via sl remove --mark; modified tracked files need no action (Sapling auto-stages)

## Changes

### Task 1: Implement -u/--update flag handling
**Files:** cmd_add.py
**Commit:** 304232d

Added two helper functions and updated main handler:
- `get_deleted_files(pathspec)`: Queries `sl status -d -n` to find deleted tracked files
- `handle_update(parsed)`: Extracts pathspec, finds deleted files, runs `sl remove --mark`
- Updated `handle()` to check for -u/--update BEFORE -A/--all check

Key insight: In Sapling, modified tracked files are automatically staged (unlike Git). Only deleted files need explicit action via `sl remove --mark`.

### Task 2: Add E2E tests
**Files:** tests/test_cmd_add.py
**Commit:** 43f0915

Added 5 comprehensive E2E tests:
1. `test_add_u_ignores_untracked`: Verifies untracked files remain as `?` after -u
2. `test_add_u_marks_deleted_for_removal`: Verifies deleted file marked as `R`
3. `test_add_u_with_pathspec`: Verifies pathspec filtering works (only subdir affected)
4. `test_add_u_no_deleted_files`: Verifies no-op case succeeds with exit 0
5. `test_add_update_long_flag`: Verifies --update works same as -u

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- **Import check:** `python -c "import cmd_add; print('OK')"` - PASSED
- **Existing tests:** All 5 original cmd_add tests pass
- **New tests:** All 5 new add_u tests pass
- **Full suite:** 84 tests pass in 61s
- **Manual verification:** Created test repo, deleted tracked file, ran gitsl add -u, verified `R` status for deleted and `?` status for untracked

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| D-0801 | No action for modified tracked files | Sapling auto-stages modified tracked files in commits |

## Technical Details

### Sapling vs Git Staging Model

| File State | Git `add -u` Action | Sapling `add -u` Action |
|------------|---------------------|-------------------------|
| Modified tracked | Stage (git add) | No action (auto-staged) |
| Deleted tracked | Mark for removal | Run `sl remove --mark` |
| Untracked | Ignore | Ignore |

### sl Command Usage

```python
# Find deleted tracked files
sl status -d -n [pathspec...]  # -d=deleted, -n=no-status-prefix

# Mark deleted files for removal
sl remove --mark <files...>
```

## Next Phase Readiness

Phase 8 complete. Ready for Phase 9 (Unsupported Command Handling).

No blockers identified.
