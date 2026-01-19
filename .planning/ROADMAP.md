# Roadmap: GitSL

## Milestones

- ✅ **v1.0 MVP** - Phases 01-09 (shipped 2026-01-18)
- 🚧 **v1.1 Polish & Documentation** - Phases 10-14 (in progress)

## Phases

<details>
<summary>v1.0 MVP (Phases 01-09) - SHIPPED 2026-01-18</summary>

### Phase 01: Script Skeleton
**Goal**: Minimal gitsl.py that receives argv and can be invoked
**Plans**: 2 plans (complete)

### Phase 02: E2E Test Infrastructure
**Goal**: pytest-based test framework that can invoke gitsl and verify output
**Plans**: 2 plans (complete)

### Phase 03: Execution Pipeline
**Goal**: gitsl dispatches to sl commands and returns output/exit codes
**Plans**: 2 plans (complete)

### Phase 04: Direct Command Mappings
**Goal**: git init, commit, diff pass through to equivalent sl commands
**Plans**: 2 plans (complete)

### Phase 05: File Operation Commands
**Goal**: git add commands translate correctly to sl equivalents
**Plans**: 1 plan (complete)

### Phase 06: Status Output Emulation
**Goal**: git status with --short and --porcelain flags emit git-compatible output
**Plans**: 1 plan (complete)

### Phase 07: Log Output Emulation
**Goal**: git log with -N and --oneline flags emit git-compatible output
**Plans**: 1 plan (complete)

### Phase 08: Add -u Emulation
**Goal**: git add -u stages modified tracked files correctly
**Plans**: 1 plan (complete)

### Phase 09: Unsupported Command Handling
**Goal**: Unsupported commands print to stderr and exit 0
**Plans**: 1 plan (complete)

</details>

### 🚧 v1.1 Polish & Documentation (In Progress)

**Milestone Goal:** Make gitsl production-ready with comprehensive documentation, easier testing, CI/CD, and PyPI publishing.

#### Phase 10: Cleanup
**Goal**: Remove all external tool references from code and comments
**Depends on**: Phase 09 (v1.0 complete)
**Requirements**: CLEAN-01, CLEAN-02
**Success Criteria** (what must be TRUE):
  1. No references to external tools remain in Python source files
  2. No references to external tools remain in comments or docstrings
  3. Codebase is clean and self-contained
**Plans**: 1 plan

Plans:
- [x] 10-01-PLAN.md — Remove external tool references from planning documentation

#### Phase 11: Testing
**Goal**: Comprehensive test infrastructure with improved runner and coverage
**Depends on**: Phase 10
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, TEST-07
**Success Criteria** (what must be TRUE):
  1. Running `./test` executes all tests and reports results
  2. Running `./test status` runs only status command tests
  3. Test script runs successfully on MacOS, Linux, and Windows
  4. Test coverage includes edge cases (empty repos, special characters)
  5. Test coverage includes error conditions (missing sl, invalid args)
**Plans**: 2 plans

Plans:
- [x] 11-01-PLAN.md — Create cross-platform test runner with command filtering
- [x] 11-02-PLAN.md — Add edge case and error condition tests

#### Phase 12: Packaging
**Goal**: gitsl installable via pip with proper entry points
**Depends on**: Phase 11
**Requirements**: PACK-01, PACK-02, PACK-03, PACK-04
**Success Criteria** (what must be TRUE):
  1. `pip install -e .` succeeds and `gitsl` command is available
  2. `gitsl --version` displays correct version number
  3. Package version matches git tag when building from tagged commit
  4. All Python modules are included in the package
**Plans**: TBD

Plans:
- [ ] 12-01: TBD

#### Phase 13: CI/CD
**Goal**: Automated testing on all platforms with release automation
**Depends on**: Phase 12
**Requirements**: CI-01, CI-02, CI-03, CI-04, CI-05
**Success Criteria** (what must be TRUE):
  1. Push to main/PR triggers test workflow automatically
  2. Tests run on MacOS, Linux, and Windows in CI matrix
  3. Sapling is installed and functional in CI environment
  4. Tagged release triggers PyPI publish workflow
  5. PyPI publishing uses trusted publishing (no API tokens)
**Plans**: TBD

Plans:
- [ ] 13-01: TBD

#### Phase 14: Documentation
**Goal**: Production-quality README with installation, usage, and command matrix
**Depends on**: Phase 13
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DOC-06, DOC-07, DOC-08
**Success Criteria** (what must be TRUE):
  1. README.md contains installation instructions (`pip install gitsl`)
  2. README.md contains quick start example showing basic usage
  3. README.md contains command support matrix (implemented vs unsupported)
  4. Each supported command has flag documentation with support status
  5. README.md displays CI status, PyPI version, and Python version badges
**Plans**: TBD

Plans:
- [ ] 14-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 10 → 11 → 12 → 13 → 14

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 01. Script Skeleton | v1.0 | 2/2 | Complete | 2026-01-18 |
| 02. E2E Test Infrastructure | v1.0 | 2/2 | Complete | 2026-01-18 |
| 03. Execution Pipeline | v1.0 | 2/2 | Complete | 2026-01-18 |
| 04. Direct Command Mappings | v1.0 | 2/2 | Complete | 2026-01-18 |
| 05. File Operation Commands | v1.0 | 1/1 | Complete | 2026-01-18 |
| 06. Status Output Emulation | v1.0 | 1/1 | Complete | 2026-01-18 |
| 07. Log Output Emulation | v1.0 | 1/1 | Complete | 2026-01-18 |
| 08. Add -u Emulation | v1.0 | 1/1 | Complete | 2026-01-18 |
| 09. Unsupported Command Handling | v1.0 | 1/1 | Complete | 2026-01-18 |
| 10. Cleanup | v1.1 | 1/1 | Complete | 2026-01-19 |
| 11. Testing | v1.1 | 2/2 | Complete | 2026-01-19 |
| 12. Packaging | v1.1 | 0/? | Not started | - |
| 13. CI/CD | v1.1 | 0/? | Not started | - |
| 14. Documentation | v1.1 | 0/? | Not started | - |
