---
phase: 12
plan: 01
subsystem: packaging
tags: [pip, setuptools, pyproject.toml, setuptools-scm, entry-points]

dependency_graph:
  requires: [10-cleanup, 11-testing]
  provides: [pip-installable-package, gitsl-cli-command, dynamic-version]
  affects: [13-ci-cd]

tech_stack:
  added: [setuptools>=80, setuptools-scm>=8, build]
  patterns: [flat-layout-py-modules, console-scripts-entry-point, spdx-license]

key_files:
  created:
    - pyproject.toml
    - LICENSE
    - README.md
  modified:
    - common.py
    - .gitignore

decisions:
  - id: PACK-LICENSE
    choice: SPDX string license format
    reason: Deprecated table format {text="MIT"} causes setuptools warnings

metrics:
  duration: 4min
  completed: 2026-01-19
---

# Phase 12 Plan 01: Package Configuration Summary

**One-liner:** pyproject.toml with setuptools flat layout, setuptools-scm version from git tags, console_scripts entry point

## What Was Built

Created Python package configuration enabling `pip install -e .` and preparing for PyPI publishing:

1. **pyproject.toml** - Complete package configuration:
   - Build backend: setuptools>=80 with setuptools-scm>=8
   - Dynamic version from git tags (v1.0 produces 1.0, head produces 1.1.dev28+gdba77e5)
   - Explicit py-modules list for flat layout (all cmd_*.py files)
   - Console script entry point: `gitsl = "gitsl:main"`
   - SPDX license format: `license = "MIT"`

2. **common.py** - Dynamic version:
   - Replaced hardcoded VERSION with importlib.metadata.version()
   - Fallback to "0.0.0" for uninstalled development

3. **LICENSE** - MIT license file (required for package metadata)

4. **README.md** - Minimal placeholder (required for pyproject.toml readme field)

5. **.gitignore** - Added build artifact patterns (build/, dist/, *.egg-info/)

## Verification Results

| Check | Result |
|-------|--------|
| pip install -e . | Success - installed gitsl-1.1.dev28+gdba77e529 |
| gitsl command available | Yes - /Users/.../venv/bin/gitsl |
| gitsl --version | Shows "gitsl version 1.1.dev28+gdba77e529" |
| All modules importable | Yes - gitsl, common, all cmd_* modules |
| Wheel contains modules | Yes - all 9 .py files, no tests |
| Tests pass | 124 passed |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed deprecated license format**
- **Found during:** Task 3 (wheel build)
- **Issue:** setuptools warnings about deprecated `license = {text = "MIT"}` table format
- **Fix:** Changed to SPDX string format `license = "MIT"`, removed License classifier
- **Files modified:** pyproject.toml
- **Commit:** 360ce5a

**2. [Rule 3 - Blocking] System pip too old for editable install**
- **Found during:** Task 3 (pip install -e .)
- **Issue:** System pip 21.2.4 doesn't support pyproject.toml editable installs
- **Fix:** Created .venv with Python 3.12 and pip 25.3
- **Files modified:** None (venv gitignored)
- **Commit:** N/A (environment setup)

**3. [Rule 2 - Missing Critical] Build artifacts not gitignored**
- **Found during:** Task 3
- **Issue:** build/, dist/, *.egg-info/ would be committed
- **Fix:** Added to .gitignore
- **Files modified:** .gitignore
- **Commit:** 360ce5a

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 007e033 | chore | create package configuration files |
| dba77e5 | feat | dynamic version from importlib.metadata |
| 360ce5a | fix | use SPDX license format, add build artifacts to gitignore |

## Success Criteria

- [x] PACK-01: pyproject.toml exists with metadata and entry points
- [x] PACK-03: `gitsl` command available in PATH after `pip install -e .`
- [x] PACK-04: Version from git tag via setuptools-scm

## Next Phase Readiness

Phase 13 (CI/CD) can proceed:
- Package builds cleanly with `python -m build`
- Wheel contains all required modules
- Version automatically derived from git tags
- Ready for GitHub Actions workflow and PyPI publishing
