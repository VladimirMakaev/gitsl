---
phase: 11-testing
plan: 02
subsystem: testing
tags: [pytest, edge-cases, error-handling, mock]
dependency-graph:
  requires: [11-01-test-runner]
  provides: [edge-case-tests, error-condition-tests, mock-sl-binary]
  affects: [13-ci-cd]
tech-stack:
  added: []
  patterns: [path-injection-for-mocks, pytest-fixtures]
key-files:
  created:
    - tests/test_edge_cases.py
    - tests/test_error_conditions.py
    - tests/mocks/sl
    - tests/mocks/sl.cmd
  modified:
    - tests/test_log.py
    - tests/test_add.py
    - tests/test_diff.py
decisions: []
metrics:
  duration: 8min
  completed: 2026-01-19
---

# Phase 11 Plan 02: Edge Cases and Error Conditions Summary

Comprehensive edge case and error condition tests with mock sl binary for controlled testing.

## What Was Built

### Edge Case Tests (`tests/test_edge_cases.py`)
13 new tests covering:
- **TestSpecialCharacters**: spaces, unicode (accents), brackets in filenames
- **TestEmptyRepo**: status/log/diff on repos with no commits
- **TestLargeFileScenarios**: 100+ files and 10MB file content
- **TestPathEdgeCases**: subdirectories and nested paths

### Error Condition Tests (`tests/test_error_conditions.py`)
8 new tests covering:
- **TestSlErrors**: exit code propagation, stderr/stdout passthrough
- **TestInvalidArgs**: unknown command, no command, help/version flags
- **TestMissingSl**: missing sl binary scenario

### Mock sl Binary (`tests/mocks/sl`, `tests/mocks/sl.cmd`)
- Python script with configurable exit code, stdout, stderr via env vars
- `MOCK_SL_EXIT`: exit code to return
- `MOCK_SL_STDOUT`: string to print to stdout
- `MOCK_SL_STDERR`: string to print to stderr
- Windows wrapper (`sl.cmd`) for cross-platform support

### Flag Combination Tests (added to existing files)
12 new tests across:
- **test_log.py**: `-5 --oneline` combined, no-flags tests
- **test_add.py**: `add .`, `add subdir/` path tests
- **test_diff.py**: specific file diff, sl repo diff tests

## Verification Results

| Check | Status |
|-------|--------|
| `pytest tests/test_edge_cases.py` | 13 passed |
| `pytest tests/test_error_conditions.py` | 8 passed |
| Mock sl with `MOCK_SL_EXIT=1` returns exit code 1 | PASS |
| All existing tests still pass | 124 passed |
| Large file tests under 30 seconds | 1.10s |
| Test count increased | 91 -> 124 (+33) |

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 38e7cc6 | test | Add edge case tests for special chars, empty repos, large files |
| 9366d99 | test | Add mock sl binary and error condition tests |
| f0ab96c | test | Add flag combination and file path tests |

## Deviations from Plan

None - plan executed exactly as written.

## Requirements Satisfied

- **TEST-04**: Existing tests audited, gaps filled with flag combination tests
- **TEST-05**: Edge cases (empty repos, special characters, large files) covered
- **TEST-06**: Error conditions (missing sl, invalid args) covered
- **TEST-07**: Flag combinations not previously covered now tested

## Next Phase Readiness

Testing phase complete. Phase 12 (Packaging) can proceed.

Ready: 12-packaging
