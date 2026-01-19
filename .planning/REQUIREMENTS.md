# Requirements: GitSL v1.1

**Defined:** 2026-01-18
**Core Value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference.

## v1.1 Requirements

Requirements for v1.1 Polish & Documentation release. Each maps to roadmap phases.

### Cleanup

- [ ] **CLEAN-01**: Remove external tool references from codebase
- [ ] **CLEAN-02**: Remove external tool references from comments/docs

### Testing

- [x] **TEST-01**: `./test` script runs all tests
- [x] **TEST-02**: `./test <command>` runs tests for specific command only
- [x] **TEST-03**: Test script works on MacOS, Linux, Windows
- [x] **TEST-04**: Audit existing tests for completeness gaps
- [x] **TEST-05**: Add tests for edge cases (empty repos, special characters, large files)
- [x] **TEST-06**: Add tests for error conditions (missing sl, invalid args)
- [x] **TEST-07**: Add tests for flag combinations not currently covered

### Packaging

- [x] **PACK-01**: pyproject.toml defines package metadata and entry points
- [ ] **PACK-02**: `pip install gitsl` installs package from PyPI
- [x] **PACK-03**: `gitsl` command available in PATH after install
- [x] **PACK-04**: Package version matches git tag

### CI/CD

- [ ] **CI-01**: GitHub Actions workflow runs tests on push/PR
- [ ] **CI-02**: Test matrix covers MacOS, Linux, Windows
- [ ] **CI-03**: CI installs Sapling on each platform
- [ ] **CI-04**: Release workflow publishes to PyPI on version tag
- [ ] **CI-05**: Trusted publishing configured (no API tokens in secrets)

### Documentation

- [ ] **DOC-01**: README.md with installation instructions
- [ ] **DOC-02**: README.md with quick start / usage examples
- [ ] **DOC-03**: README.md with command support matrix (supported vs unsupported)
- [ ] **DOC-04**: Per-command flag documentation with support status
- [ ] **DOC-05**: Unsupported commands/flags include reason why
- [ ] **DOC-06**: CI status badge in README
- [ ] **DOC-07**: PyPI version badge in README
- [ ] **DOC-08**: Python version badge in README

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Extended Command Support

- **CMD-01**: Implement additional git commands based on v1.1 research
- **CMD-02**: Add new flag support for existing commands

### Advanced Features

- **ADV-01**: Configuration file support
- **ADV-02**: Plugin system for custom command handlers

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| New command implementations | v1.1 is documentation/polish only; new commands are v2 |
| Matching git diff output exactly | Pass-through is sufficient |
| OAuth/authentication handling | Sapling handles this |
| Remote operations (push/pull/fetch) | Sapling model differs fundamentally |
| Interactive commands (rebase -i, add -p) | Require terminal control |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLEAN-01 | Phase 10 | Complete |
| CLEAN-02 | Phase 10 | Complete |
| TEST-01 | Phase 11 | Complete |
| TEST-02 | Phase 11 | Complete |
| TEST-03 | Phase 11 | Complete |
| TEST-04 | Phase 11 | Complete |
| TEST-05 | Phase 11 | Complete |
| TEST-06 | Phase 11 | Complete |
| TEST-07 | Phase 11 | Complete |
| PACK-01 | Phase 12 | Complete |
| PACK-02 | Phase 12 | Pending (Phase 13) |
| PACK-03 | Phase 12 | Complete |
| PACK-04 | Phase 12 | Complete |
| CI-01 | Phase 13 | Pending |
| CI-02 | Phase 13 | Pending |
| CI-03 | Phase 13 | Pending |
| CI-04 | Phase 13 | Pending |
| CI-05 | Phase 13 | Pending |
| DOC-01 | Phase 14 | Pending |
| DOC-02 | Phase 14 | Pending |
| DOC-03 | Phase 14 | Pending |
| DOC-04 | Phase 14 | Pending |
| DOC-05 | Phase 14 | Pending |
| DOC-06 | Phase 14 | Pending |
| DOC-07 | Phase 14 | Pending |
| DOC-08 | Phase 14 | Pending |

**Coverage:**
- v1.1 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements defined: 2026-01-18*
*Last updated: 2026-01-19 after roadmap creation*
