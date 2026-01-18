# Requirements: GitSL

**Defined:** 2026-01-17
**Core Value:** Git commands used by get-shit-done execute correctly against Sapling repos

## v1 Requirements

### Architecture

- [x] **ARCH-01**: Entry point (gitsl.py) contains only argument dispatch, no command logic
- [x] **ARCH-02**: Shared utilities (common.py) contain parsing, subprocess, debug mode functions
- [x] **ARCH-03**: Each command has its own file (cmd_status.py, cmd_commit.py, etc.)
- [x] **ARCH-04**: Command files export a handler function that receives parsed args

### Core Execution

- [ ] **EXEC-01**: Script parses argv and extracts git command + arguments
- [x] **EXEC-02**: Script executes equivalent Sapling command via subprocess
- [x] **EXEC-03**: Script propagates Sapling's exit code to caller
- [x] **EXEC-04**: Script passes through stdout from Sapling to caller
- [x] **EXEC-05**: Script passes through stderr from Sapling to caller
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

- [x] **CMD-01**: `git status` translates to `sl status`
- [x] **CMD-02**: `git add <files>` translates to `sl add <files>`
- [x] **CMD-03**: `git commit -m "msg"` translates to `sl commit -m "msg"`
- [x] **CMD-04**: `git log` translates to `sl log`
- [x] **CMD-05**: `git diff` translates to `sl diff`
- [x] **CMD-06**: `git init` translates to `sl init`
- [x] **CMD-07**: `git rev-parse --short HEAD` translates to `sl whereami`
- [x] **CMD-08**: `git add -A` translates to `sl addremove`

### Flag Emulation

- [x] **FLAG-01**: `git status --porcelain` emulates exact git porcelain format
- [x] **FLAG-02**: `git status --short` emulates git short format
- [ ] **FLAG-03**: `git add -u` finds modified tracked files and adds them
- [x] **FLAG-04**: `git log --oneline` emulates git oneline format via sl template
- [x] **FLAG-05**: `git log -N` translates to `sl log -l N`

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
| TEST-01 | Phase 2 | Complete |
| TEST-02 | Phase 2 | Complete |
| TEST-03 | Phase 2 | Complete |
| TEST-04 | Phase 2 | Complete |
| TEST-05 | Phase 2 | Complete |
| TEST-06 | Phase 2 | Complete |
| TEST-07 | Phase 2 | Complete |
| ARCH-01 | Phase 3 | Complete |
| ARCH-02 | Phase 3 | Complete |
| ARCH-03 | Phase 3 | Complete |
| ARCH-04 | Phase 3 | Complete |
| EXEC-02 | Phase 3 | Complete |
| EXEC-03 | Phase 3 | Complete |
| EXEC-04 | Phase 3 | Complete |
| EXEC-05 | Phase 3 | Complete |
| CMD-01 | Phase 4 | Complete |
| CMD-04 | Phase 4 | Complete |
| CMD-05 | Phase 4 | Complete |
| CMD-06 | Phase 4 | Complete |
| CMD-07 | Phase 4 | Complete |
| CMD-02 | Phase 5 | Complete |
| CMD-03 | Phase 5 | Complete |
| CMD-08 | Phase 5 | Complete |
| FLAG-01 | Phase 6 | Complete |
| FLAG-02 | Phase 6 | Complete |
| FLAG-04 | Phase 7 | Complete |
| FLAG-05 | Phase 7 | Complete |
| FLAG-03 | Phase 8 | Pending |
| UNSUP-01 | Phase 9 | Pending |
| UNSUP-02 | Phase 9 | Pending |

**Coverage:**
- v1 requirements: 32 total (21 original + 7 testing + 4 architecture)
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2026-01-17*
*Last updated: 2026-01-18 - Phase 7 requirements marked complete (FLAG-04, FLAG-05)*
