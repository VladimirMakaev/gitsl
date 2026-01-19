# Phase 11: Testing - Context

**Gathered:** 2026-01-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Comprehensive test infrastructure with improved runner and coverage. Create a cross-platform test runner script with command filtering, self-bootstrapping venv, and CI-compatible output. Add edge case and error condition tests.

</domain>

<decisions>
## Implementation Decisions

### Filtering behavior
- Test files named `test_<command>.py` (e.g., `test_status.py`, `test_add.py`)
- Pytest markers for command filtering (e.g., `@pytest.mark.status`)
- Invocation: `./test` runs all, `./test status` runs tests marked with `status`
- Non-matching category runs zero tests (no error)
- Unmarked tests always run regardless of filter
- All tests are e2e (no separate unit/integration categories)
- Rename existing `test_cmd_*.py` files to match `test_*.py` convention

### Coverage gaps
- Edge cases: special characters in filenames (spaces, unicode), empty repos, no commits
- File state permutations: 1/2/3+ files × added/deleted/staged/untracked combinations
- Error conditions: missing sl binary, invalid arguments, sl errors
- Mock sl binary: Python script callable as shell command for controlled testing
- Mock injection: PATH override (prepend mock sl directory)

### Cross-platform approach
- Test runner: Python script with shebang (`./test`)
- Windows wrapper: `test.cmd` that calls Python
- Binary lookup: `shutil.which()` in Python, not shell-dependent
- Self-bootstrapping:
  - Check for sl binary upfront, fail with clear message if missing
  - Auto-create `.venv` in project root if not present
  - Install pytest and dependencies into venv
  - Detect existing setup to avoid redundant work
  - Smart re-run: don't reinstall if already set up

### CI integration
- Default output: standard pytest (readable, colored when TTY)
- Report flag: `--report <filename>` exports CI-compatible format (JUnit XML)
- Color handling: auto-detect TTY (colors on terminal, plain in pipe/CI)
- Exit codes: standard (0 = pass, non-zero = fail) for CI compatibility

### Claude's Discretion
- Organization of test_harness.py and test_execution.py (utilities vs consolidate)
- Exact JUnit XML generation approach
- Venv detection logic details
- Mock sl script implementation details

</decisions>

<specifics>
## Specific Ideas

- "Good Dev Experience" — running `./test` twice should be fast (detect existing setup)
- Mock sl should support configurable exit code and stdout/stderr output
- Self-contained: only sl binary needs to be pre-installed, everything else bootstraps

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-testing*
*Context gathered: 2026-01-19*
