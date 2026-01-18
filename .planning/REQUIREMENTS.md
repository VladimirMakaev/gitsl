# Requirements: GitSL

**Defined:** 2026-01-17
**Core Value:** Git commands used by get-shit-done execute correctly against Sapling repos

## v1 Requirements

### Core Execution

- [ ] **EXEC-01**: Script parses argv and extracts git command + arguments
- [ ] **EXEC-02**: Script executes equivalent Sapling command via subprocess
- [ ] **EXEC-03**: Script propagates Sapling's exit code to caller
- [ ] **EXEC-04**: Script passes through stdout from Sapling to caller
- [ ] **EXEC-05**: Script passes through stderr from Sapling to caller
- [ ] **EXEC-06**: Debug mode shows command that would run without executing

### E2E Test Infrastructure

- [ ] **TEST-01**: Test framework creates temp git repositories using tempfile
- [ ] **TEST-02**: Test harness runs real git command and captures stdout, stderr, exit code
- [ ] **TEST-03**: Test harness runs gitsl shim command and captures stdout, stderr, exit code
- [ ] **TEST-04**: Exit code comparison asserts git and gitsl return same codes
- [ ] **TEST-05**: Output comparison supports exact match mode (for porcelain formats)
- [ ] **TEST-06**: Output comparison supports semantic match mode (for human-readable formats)
- [ ] **TEST-07**: Test fixtures can set up repos with commits, branches, modified files

### Command Translation

- [ ] **CMD-01**: `git status` translates to `sl status`
- [ ] **CMD-02**: `git add <files>` translates to `sl add <files>`
- [ ] **CMD-03**: `git commit -m "msg"` translates to `sl commit -m "msg"`
- [ ] **CMD-04**: `git log` translates to `sl log`
- [ ] **CMD-05**: `git diff` translates to `sl diff`
- [ ] **CMD-06**: `git init` translates to `sl init`
- [ ] **CMD-07**: `git rev-parse --short HEAD` translates to `sl whereami`
- [ ] **CMD-08**: `git add -A` translates to `sl addremove`

### Flag Emulation

- [ ] **FLAG-01**: `git status --porcelain` emulates exact git porcelain format
- [ ] **FLAG-02**: `git status --short` emulates git short format
- [ ] **FLAG-03**: `git add -u` finds modified tracked files and adds them
- [ ] **FLAG-04**: `git log --oneline` emulates git oneline format via sl template
- [ ] **FLAG-05**: `git log -N` translates to `sl log -l N`

### Unsupported Commands

- [ ] **UNSUP-01**: Unsupported commands print original command to stderr
- [ ] **UNSUP-02**: Unsupported commands exit with code 0

## v2 Requirements

### Extended Commands

- **EXTCMD-01**: `git push` support with branch mapping
- **EXTCMD-02**: `git pull` support
- **EXTCMD-03**: `git checkout` / `git switch` support
- **EXTCMD-04**: `git branch` support
- **EXTCMD-05**: `git stash` -> `sl shelve` translation

### Extended Features

- **EXTFEAT-01**: Environment variable passthrough (GIT_DIR, etc.)
- **EXTFEAT-02**: Git config command handling
- **EXTFEAT-03**: Complex reference syntax translation (HEAD~2, etc.)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full git compatibility | Scope creep - only GSD commands needed |
| Windows batch file support | Unix-only for now |
| Interactive commands (rebase -i, add -p) | Complex, not used by GSD |
| Git aliases support | Over-engineering |
| Caching/optimization | Premature optimization |
| Output transformation for diff | User confirmed passthrough sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXEC-01 | Phase 1 | Complete |
| EXEC-06 | Phase 1 | Complete |
| TEST-01 | Phase 2 | Pending |
| TEST-02 | Phase 2 | Pending |
| TEST-03 | Phase 2 | Pending |
| TEST-04 | Phase 2 | Pending |
| TEST-05 | Phase 2 | Pending |
| TEST-06 | Phase 2 | Pending |
| TEST-07 | Phase 2 | Pending |
| EXEC-02 | Phase 3 | Pending |
| EXEC-03 | Phase 3 | Pending |
| EXEC-04 | Phase 3 | Pending |
| EXEC-05 | Phase 3 | Pending |
| CMD-01 | Phase 4 | Pending |
| CMD-04 | Phase 4 | Pending |
| CMD-05 | Phase 4 | Pending |
| CMD-06 | Phase 4 | Pending |
| CMD-07 | Phase 4 | Pending |
| CMD-02 | Phase 5 | Pending |
| CMD-03 | Phase 5 | Pending |
| CMD-08 | Phase 5 | Pending |
| FLAG-01 | Phase 6 | Pending |
| FLAG-02 | Phase 6 | Pending |
| FLAG-04 | Phase 7 | Pending |
| FLAG-05 | Phase 7 | Pending |
| FLAG-03 | Phase 8 | Pending |
| UNSUP-01 | Phase 9 | Pending |
| UNSUP-02 | Phase 9 | Pending |

**Coverage:**
- v1 requirements: 28 total (21 original + 7 testing)
- Mapped to phases: 28
- Unmapped: 0

---
*Requirements defined: 2026-01-17*
*Last updated: 2026-01-17 - Added E2E test infrastructure requirements, renumbered phases*
