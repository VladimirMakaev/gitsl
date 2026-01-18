# Project Research Summary

**Project:** gitsl v1.1 Polish & Documentation
**Domain:** CLI Packaging / PyPI Publishing / CI/CD
**Researched:** 2026-01-18
**Confidence:** HIGH

## Executive Summary

gitsl v1.1 is a polish and documentation release that transforms the existing CLI shim from a working prototype into a properly packaged, documented, and continuously tested product. The research confirms that Python's modern packaging ecosystem (pyproject.toml with setuptools) provides a straightforward path to PyPI publishing, and GitHub Actions offers robust cross-platform CI capabilities. The key challenge is gitsl's flat module layout, which requires explicit module listing rather than relying on setuptools auto-discovery.

The recommended approach prioritizes package structure first, then CI/CD, followed by documentation and finally the release workflow. This order ensures that each phase builds on a stable foundation: you cannot test what you cannot install, you cannot document what you have not verified works, and you cannot release what is not thoroughly tested. The existing codebase is well-structured for this transition, with clear module boundaries and established test patterns.

The primary risks are (1) the PowerShell `sl` alias conflict on Windows that will cause mysterious test failures, (2) PyPI's immutable releases meaning any premature release permanently consumes that version number, and (3) the need to configure trusted publishing on PyPI before the first release attempt. All three are preventable with proper planning and testing on TestPyPI first.

## Key Findings

### Recommended Stack

The v1.1 stack is primarily about tooling and configuration rather than new dependencies. All recommendations use mature, well-documented components.

**Core technologies:**
- **pyproject.toml + setuptools**: Modern packaging standard, no extra dependencies, handles entry points cleanly
- **GitHub Actions**: Native CI/CD, free for open source, excellent matrix support for cross-platform testing
- **Trusted Publishing (OIDC)**: PyPI authentication without managing secrets, recommended by Python Packaging Authority
- **pytest**: Already in use, add `./test` wrapper script for command-specific testing convenience

**Key configuration decisions:**
- Use explicit `py-modules` list in pyproject.toml (flat layout requires this)
- Version should remain in `common.py` with dynamic reading at build time
- Python support: 3.8-3.13 to maximize compatibility

### Expected Features

**Must have (table stakes):**
- README with one-liner description, installation instructions, quick start example
- Command support matrix showing what git commands are supported
- Per-command flag documentation
- `pip install gitsl` entry point works
- `--help` and `--version` work correctly
- LICENSE file (MIT)

**Should have (differentiators):**
- Comprehensive command matrix covering ~34 git commands with status (implemented/planned/out-of-scope)
- Badges showing CI status, Python versions, PyPI version
- Cross-platform CI (Ubuntu, macOS, Windows)
- `./test` and `./test <command>` convenience scripts
- Architecture section explaining how translation works

**Defer (v2+):**
- GIF/video demos in README
- Homebrew tap or other package managers
- Additional git command implementations
- GUI/TUI components
- Extensive configuration options

### Architecture Approach

The research supports two viable package structures: maintaining the current flat layout with explicit module listing, or migrating to src layout. **Recommendation: keep flat layout for v1.1** to minimize disruption and testing burden. The flat layout works fine with explicit `py-modules` configuration.

**Major components:**
1. **pyproject.toml** - Package metadata, entry points, build configuration
2. **GitHub workflows** - `ci.yml` for testing, `publish.yml` for PyPI release
3. **Test infrastructure** - Existing pytest + new `./test` wrapper script
4. **Documentation** - README.md structured per best practices

**Entry point configuration:**
```toml
[project.scripts]
gitsl = "gitsl:main"
```

This creates the `gitsl` command that calls `main()` from `gitsl.py`.

### Critical Pitfalls

1. **PowerShell `sl` alias conflict (Windows)** - PowerShell has built-in `sl` alias for `Set-Location`. Must remove alias in CI workflow: `Remove-Alias -Name sl -Force -ErrorAction SilentlyContinue`

2. **PyPI immutable releases** - Cannot overwrite or delete released versions. Test on TestPyPI first. Use `.dev` versions for testing.

3. **Missing trusted publisher config** - Must configure on PyPI.org AND test.pypi.org BEFORE first release attempt. Workflow, repo, and environment names must match exactly.

4. **Flat layout module discovery** - Setuptools auto-discovery fails for flat layout. Must explicitly list all modules in `py-modules`.

5. **pypa/gh-action-pypi-publish is Linux-only** - Docker-based action only runs on Linux. Build can happen on any OS, but publish job MUST use ubuntu-latest.

6. **Windows PATH for Sapling** - Sapling installer may not persist PATH changes. Explicitly add to `$GITHUB_PATH` in workflow.

7. **Matrix fail-fast default** - GitHub Actions cancels all matrix jobs when one fails. Set `fail-fast: false` to see which platforms actually work.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Package Configuration
**Rationale:** Foundation for all other phases. Cannot test installation without pyproject.toml.
**Delivers:** Working `pip install -e .` and `pip install gitsl` (local)
**Addresses:** pyproject.toml, entry points, version management
**Avoids:** Pitfalls #4 (flat layout), #15-20 (package structure issues)

Key tasks:
- Create pyproject.toml with explicit py-modules list
- Verify `pip install -e .` works
- Verify `gitsl` command works after install
- Verify `--version` shows correct version

### Phase 2: CI Pipeline
**Rationale:** Must have automated testing before documentation (ensures accuracy) and before release (prevents broken releases).
**Delivers:** Green CI badge, cross-platform test matrix
**Uses:** GitHub Actions, pytest
**Avoids:** Pitfalls #6 (sl alias), #7 (paths), #8 (line endings), #10 (fail-fast), #11-14 (Sapling install)

Key tasks:
- Create `.github/workflows/ci.yml`
- Install Sapling on Ubuntu, macOS, Windows
- Handle PowerShell `sl` alias on Windows
- Test matrix: Python 3.8-3.13 x 3 OSes (with exclusions)
- Set `fail-fast: false`

### Phase 3: Test Runner Improvements
**Rationale:** Developer experience improvement. Should happen alongside CI to ensure `./test` works the same locally and in CI.
**Delivers:** `./test` and `./test <command>` convenience scripts
**Addresses:** Test runner UX from FEATURES.md

Key tasks:
- Create `./test` shell script
- Support `./test status`, `./test log`, etc.
- Ensure pytest.ini alignment with CI

### Phase 4: Documentation
**Rationale:** Documentation comes after CI is green so we can add accurate status badges and know exactly what works.
**Delivers:** Complete README.md, LICENSE file
**Addresses:** All table stakes from FEATURES.md

Key tasks:
- Write README.md with required sections
- Add command support matrix (34 commands)
- Add flag documentation for implemented commands
- Add CI status badge
- Ensure LICENSE file exists

### Phase 5: Release Workflow
**Rationale:** Final phase after everything else is stable and documented.
**Delivers:** PyPI package, release automation
**Avoids:** Pitfalls #1 (immutable), #2 (trusted publisher), #3 (TestPyPI), #4 (Linux-only), #5 (artifacts)

Key tasks:
- Configure trusted publisher on test.pypi.org
- Test release to TestPyPI
- Configure trusted publisher on pypi.org
- Create `.github/workflows/publish.yml`
- Test full release flow

### Phase Ordering Rationale

- **Package before CI**: Cannot run `pip install -e .` in CI without pyproject.toml
- **CI before Documentation**: Need accurate CI status before adding badges
- **Test runner alongside CI**: Both use pytest, should stay synchronized
- **Documentation before Release**: README.md required for PyPI page
- **Release last**: All quality checks must pass first

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (CI):** Sapling installation steps may change with new releases. Pin specific version and test.
- **Phase 5 (Release):** Trusted publishing configuration is repository-specific. Verify exact steps when ready.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Package):** pyproject.toml is well-documented, patterns are established
- **Phase 3 (Test Runner):** Simple shell script, no research needed
- **Phase 4 (Documentation):** README patterns are established, just execution

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official Python Packaging Guide, setuptools docs |
| Features | MEDIUM-HIGH | Based on CLI best practices, may need user feedback |
| Architecture | HIGH | Standard patterns, no novel approaches |
| Pitfalls | HIGH | Verified against official docs, specific to this project |

**Overall confidence:** HIGH

### Gaps to Address

- **Sapling Windows installation**: Documentation is sparse. May need to experiment in CI to find reliable approach.
- **Package name availability**: Have not verified "gitsl" is available on PyPI. Check before first release.
- **macOS Sapling Homebrew stability**: `brew install sapling` works but version pinning options unclear.

## Sources

### Primary (HIGH confidence)
- [Python Packaging User Guide - Modernize setup.py](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/)
- [Setuptools pyproject.toml Configuration](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)

### Secondary (MEDIUM confidence)
- [GitHub README guide](https://www.markepear.dev/blog/github-readme-guide) - README structure patterns
- [gh CLI manual](https://cli.github.com/manual/gh) - Command documentation format
- [Sapling Installation Guide](https://sapling-scm.com/docs/introduction/getting-started/)
- [Pytest with Eric - GitHub Actions Integration](https://pytest-with-eric.com/integrations/pytest-github-actions/)

### Tertiary (LOW confidence)
- Sapling Windows installation specifics - May need validation during CI implementation

---
*Research completed: 2026-01-18*
*Ready for roadmap: yes*
