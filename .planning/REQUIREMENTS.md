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
- **EXTCMD-05**: `git stash` → `sl shelve` translation

### Extended Features

- **EXTFEAT-01**: Environment variable passthrough (GIT_DIR, etc.)
- **EXTFEAT-02**: Git config command handling
- **EXTFEAT-03**: Complex reference syntax translation (HEAD~2, etc.)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full git compatibility | Scope creep — only GSD commands needed |
| Windows batch file support | Unix-only for now |
| Interactive commands (rebase -i, add -p) | Complex, not used by GSD |
| Git aliases support | Over-engineering |
| Caching/optimization | Premature optimization |
| Output transformation for diff | User confirmed passthrough sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXEC-01 | TBD | Pending |
| EXEC-02 | TBD | Pending |
| EXEC-03 | TBD | Pending |
| EXEC-04 | TBD | Pending |
| EXEC-05 | TBD | Pending |
| EXEC-06 | TBD | Pending |
| CMD-01 | TBD | Pending |
| CMD-02 | TBD | Pending |
| CMD-03 | TBD | Pending |
| CMD-04 | TBD | Pending |
| CMD-05 | TBD | Pending |
| CMD-06 | TBD | Pending |
| CMD-07 | TBD | Pending |
| CMD-08 | TBD | Pending |
| FLAG-01 | TBD | Pending |
| FLAG-02 | TBD | Pending |
| FLAG-03 | TBD | Pending |
| FLAG-04 | TBD | Pending |
| FLAG-05 | TBD | Pending |
| UNSUP-01 | TBD | Pending |
| UNSUP-02 | TBD | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 0
- Unmapped: 21 ⚠️

---
*Requirements defined: 2026-01-17*
*Last updated: 2026-01-17 after initial definition*
