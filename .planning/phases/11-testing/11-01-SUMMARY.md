---
phase: 11-testing
plan: 01
subsystem: testing
tags: [pytest, test-runner, cross-platform]
dependency-graph:
  requires: [02-e2e-test-infrastructure]
  provides: [test-runner-script, command-filtering, marker-system]
  affects: [11-02-coverage, 13-ci-cd]
tech-stack:
  added: []
  patterns: [pytest-markers, venv-bootstrapping]
key-files:
  created:
    - test
    - test.cmd
  modified:
    - pytest.ini
    - tests/test_add.py
    - tests/test_commit.py
    - tests/test_diff.py
    - tests/test_init.py
    - tests/test_log.py
    - tests/test_rev_parse.py
    - tests/test_status.py
    - tests/test_execution.py
    - tests/test_harness.py
    - tests/test_unsupported.py
decisions: []
metrics:
  duration: 5min
  completed: 2026-01-19
---

# Phase 11 Plan 01: Test Runner and Markers Summary

Cross-platform test runner with self-bootstrapping venv, pytest auto-install, and command-based filtering via markers.

## What Was Built

### Test Runner Script (`test`)
- Python script with shebang, works on Unix and macOS
- Auto-creates `.venv` if missing using `venv.create()`
- Auto-installs pytest if not found in venv
- Warns if Sapling (sl) not installed (some tests require it)
- Supports command filtering: `./test status`, `./test add`, etc.
- Supports JUnit XML output: `./test --report results.xml`
- Passes through additional pytest arguments

### Windows Wrapper (`test.cmd`)
- Batch file that invokes `python test %*`
- Enables `test <command>` syntax on Windows

### Pytest Markers (pytest.ini)
Registered markers for all command types:
- `add`, `commit`, `diff`, `init`, `log`, `rev_parse`, `status`
- `unsupported`, `execution`, `harness`, `always`

### Renamed Test Files
- `test_cmd_*.py` -> `test_*.py` (cleaner naming)
- `test_status_porcelain.py` -> `test_status.py`
- All files now have command markers applied

## Verification Results

| Check | Status |
|-------|--------|
| `./test` creates venv if missing | PASS |
| `./test` runs all 91 tests | PASS (60.52s) |
| `./test status` runs only status tests | PASS (11 selected) |
| `./test add` runs only add tests | PASS (10 selected) |
| `./test --report` creates JUnit XML | PASS |
| No unknown marker warnings | PASS |

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 6d4b468 | feat | Create cross-platform test runner with self-bootstrapping |
| b0bc36f | feat | Register pytest markers for command filtering |
| 1dbba79 | refactor | Rename test files and apply command markers |

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

Plan 11-02 (Coverage) can proceed. Test runner provides foundation for coverage reporting.

Ready: 11-02-PLAN.md
