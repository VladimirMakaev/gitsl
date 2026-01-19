---
phase: 08-add-u-emulation
verified: 2026-01-18T22:00:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 8: Add -u Emulation Verification Report

**Phase Goal:** Stage only modified tracked files (exclude new files)
**Verified:** 2026-01-18T22:00:00Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | git add -u stages modified tracked files (no action in Sapling - auto-staged) | VERIFIED | `handle_update()` at line 31-52 in cmd_add.py; test `test_add_u_no_deleted_files` confirms modified files remain in expected M state |
| 2 | git add -u marks deleted tracked files for removal via sl remove --mark | VERIFIED | Line 49: `subprocess.run(["sl", "remove", "--mark"] + deleted_files)`; test `test_add_u_marks_deleted_for_removal` confirms R status after command |
| 3 | git add -u does NOT stage untracked files | VERIFIED | Test `test_add_u_ignores_untracked` explicitly verifies `? untracked.txt` remains after `git add -u` |
| 4 | git add -u path/ respects pathspec (only affects files under path/) | VERIFIED | Line 42-45: pathspec filtering; test `test_add_u_with_pathspec` confirms only subdir affected |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `cmd_add.py` | -u/--update flag handling with `handle_update` | VERIFIED | 77 lines, contains `handle_update()` at line 31, `get_deleted_files()` at line 9. No stub patterns found. |
| `tests/test_cmd_add.py` | E2E tests with `test_add_u` | VERIFIED | 184 lines, contains 5 test functions: `test_add_u_ignores_untracked`, `test_add_u_marks_deleted_for_removal`, `test_add_u_with_pathspec`, `test_add_u_no_deleted_files`, `test_add_update_long_flag` |

### Artifact Verification Details

#### cmd_add.py

**Level 1 - Existence:** EXISTS (77 lines)

**Level 2 - Substantive:**
- Line count: 77 lines (exceeds 15-line minimum for handler)
- No TODO/FIXME/placeholder patterns found
- Real implementation: `get_deleted_files()` queries `sl status -d -n`, `handle_update()` calls `sl remove --mark`
- Proper exports: `handle()` function exported and used

**Level 3 - Wired:**
- Imported at gitsl.py:18: `import cmd_add`
- Used at gitsl.py:75: `return cmd_add.handle(parsed)`
- Status: WIRED

#### tests/test_cmd_add.py

**Level 1 - Existence:** EXISTS (184 lines)

**Level 2 - Substantive:**
- Line count: 184 lines (exceeds 10-line minimum for test file)
- 5 comprehensive test functions in `TestAddUpdate` class
- Each test has setup, action, and assertion phases
- No placeholder tests

**Level 3 - Wired:**
- Tests run via pytest (confirmed: 10 passed in 9.40s)
- Tests use proper fixtures (`sl_repo_with_commit`)
- Status: WIRED

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| cmd_add.py | sl status -d -n | subprocess.run with capture_output | WIRED | Line 19: `cmd = ["sl", "status", "-d", "-n"]`, Line 23: `subprocess.run(cmd, capture_output=True, text=True)` |
| cmd_add.py | sl remove --mark | subprocess.run for marking deleted files | WIRED | Line 49: `subprocess.run(["sl", "remove", "--mark"] + deleted_files)` |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| FLAG-03: git add -u finds modified tracked files and adds them | SATISFIED | None |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| cmd_add.py | 26 | `return []` | Info | Intentional - returns empty list when no deleted files found |
| tests/test_cmd_add.py | 21 | `skipif` | Info | Standard pattern for skipping when Sapling not installed |

No blocking anti-patterns found.

### Human Verification Required

None - all truths verified programmatically and through test execution.

### Test Execution Results

```
/usr/bin/python3 -m pytest tests/test_cmd_add.py -v
============================= test session starts ==============================
collected 10 items

tests/test_cmd_add.py::TestAddBasic::test_add_new_file_succeeds PASSED
tests/test_cmd_add.py::TestAddBasic::test_add_multiple_files PASSED
tests/test_cmd_add.py::TestAddAll::test_add_all_short_flag PASSED
tests/test_cmd_add.py::TestAddAll::test_add_all_long_flag PASSED
tests/test_cmd_add.py::TestAddAll::test_add_all_with_deleted_file PASSED
tests/test_cmd_add.py::TestAddUpdate::test_add_u_ignores_untracked PASSED
tests/test_cmd_add.py::TestAddUpdate::test_add_u_marks_deleted_for_removal PASSED
tests/test_cmd_add.py::TestAddUpdate::test_add_u_with_pathspec PASSED
tests/test_cmd_add.py::TestAddUpdate::test_add_u_no_deleted_files PASSED
tests/test_cmd_add.py::TestAddUpdate::test_add_update_long_flag PASSED

============================== 10 passed in 9.40s ==============================
```

### Summary

Phase 8 goal fully achieved. The `git add -u` command:

1. **Ignores untracked files** - Verified by test showing `?` status preserved
2. **Handles modified tracked files** - No action needed (Sapling auto-stages), verified by test
3. **Marks deleted files for removal** - Calls `sl remove --mark`, verified by test showing `R` status
4. **Respects pathspec** - Filters deleted files by path, verified by test showing only subdir affected

All 4 must-have truths verified. All artifacts exist, are substantive, and are properly wired. All 10 tests pass.

---

*Verified: 2026-01-18T22:00:00Z*
*Verifier: Claude*
