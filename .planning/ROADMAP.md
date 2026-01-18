# Roadmap: GitSL

## Overview

GitSL transforms git commands into Sapling equivalents, enabling tools like get-shit-done to work transparently with Sapling repos. The roadmap builds from core execution infrastructure (parsing, subprocess handling) through command translation layers (direct mappings, then flag transformations) to output format emulation for tooling compatibility. **E2E testing is foundational** - we build the test harness early and use golden-master comparison (git vs gitsl output) to validate every phase.

## Testing Philosophy

**Golden-Master E2E Testing:** Since Sapling works with git repositories, every command can be validated by:
1. Create temp git repository with specific state
2. Run `git <command>` and capture output/exit code
3. Run `gitsl <command>` and capture output/exit code
4. Compare results (exact for porcelain, semantic for human-readable)

This gives us confidence that gitsl behaves identically to git for all supported commands.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Script Skeleton** - Argument parsing and debug mode
- [x] **Phase 2: E2E Test Infrastructure** - Golden-master testing framework
- [x] **Phase 3: Execution Pipeline** - Subprocess handling with proper I/O and exit codes
- [x] **Phase 4: Direct Command Mappings** - Simple 1:1 git-to-sl translations
- [x] **Phase 5: File Operation Commands** - Add, commit, and addremove commands
- [x] **Phase 6: Status Output Emulation** - Porcelain and short format matching
- [x] **Phase 7: Log Output Emulation** - Oneline format and -N flag translation
- [x] **Phase 8: Add -u Emulation** - Finding and staging modified tracked files
- [ ] **Phase 9: Unsupported Command Handling** - Graceful failure with informative messages

## Phase Details

### Phase 1: Script Skeleton
**Goal**: Script can parse git commands from argv and show what would execute
**Depends on**: Nothing (first phase)
**Requirements**: EXEC-01, EXEC-06
**Success Criteria** (what must be TRUE):
  1. User can invoke script with git-style arguments and script correctly identifies command and arguments
  2. User can run with debug flag and see translated command without execution
  3. Script handles empty/missing arguments gracefully
**E2E Tests**: None yet (test infra built in Phase 2)
**Plans**: 1 plan

Plans:
- [x] 01-01-PLAN.md - Create gitsl.py with argument parsing and debug mode

### Phase 2: E2E Test Infrastructure
**Goal**: Test harness can compare git and gitsl behavior on temp repositories
**Depends on**: Phase 1 (needs script to test)
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, TEST-07
**Success Criteria** (what must be TRUE):
  1. Test can create temp git repo with `tempfile.mkdtemp()` and clean up after
  2. Test can run `git <cmd>` and capture stdout, stderr, exit code
  3. Test can run `gitsl <cmd>` and capture stdout, stderr, exit code
  4. Test can assert exit codes match between git and gitsl
  5. Test can assert exact output match (for porcelain formats)
  6. Test can assert semantic output match (ignoring whitespace, timestamps for human formats)
  7. Test fixtures can create repos with: initial commit, modified files, untracked files, branches
**E2E Tests**: Self-validating - the infrastructure IS the tests
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md - Core test infrastructure (helpers, fixtures, conftest)
- [x] 02-02-PLAN.md - Harness self-validation tests

### Phase 3: Execution Pipeline
**Goal**: Script can execute Sapling commands and faithfully relay results to caller
**Depends on**: Phase 2 (test infra ready)
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04, EXEC-02, EXEC-03, EXEC-04, EXEC-05
**Success Criteria** (what must be TRUE):
  1. gitsl.py contains only entry point logic, dispatches to command handlers
  2. common.py contains shared utilities (parsing, subprocess, debug mode)
  3. Command handlers are in separate files (cmd_*.py pattern)
  4. Script executes sl commands via subprocess without deadlock
  5. Exit code from sl propagates exactly to caller (verified by echo $?)
  6. stdout from sl appears on caller's stdout in real-time
  7. stderr from sl appears on caller's stderr in real-time
  8. Ctrl+C cleanly terminates both script and sl subprocess
**E2E Tests**:
  - Test exit code propagation: run command that fails, verify exit code matches
  - Test stdout passthrough: run `sl status`, verify output appears
  - Test stderr passthrough: run invalid command, verify error appears
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md - Refactor gitsl.py into multi-file architecture
- [x] 03-02-PLAN.md - Implement subprocess execution with E2E tests

### Phase 4: Direct Command Mappings
**Goal**: Simple git commands translate directly to sl equivalents
**Depends on**: Phase 3
**Requirements**: CMD-01, CMD-04, CMD-05, CMD-06, CMD-07
**Success Criteria** (what must be TRUE):
  1. `git status` runs `sl status` and shows output
  2. `git log` runs `sl log` and shows output
  3. `git diff` runs `sl diff` and shows output
  4. `git init` runs `sl init` and creates repo
  5. `git rev-parse --short HEAD` returns current commit hash via `sl whereami`
**E2E Tests**:
  - For each command: create temp repo, run git, run gitsl, compare outputs
  - Test `git status` on clean repo, modified repo, untracked files
  - Test `git log` with commits
  - Test `git diff` with modifications
  - Test `git init` creates working repo
  - Test `git rev-parse --short HEAD` returns valid hash
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md - Passthrough commands (log, diff, init) with E2E tests
- [x] 04-02-PLAN.md - rev-parse --short HEAD handler with output truncation

### Phase 5: File Operation Commands
**Goal**: File staging and commit commands work correctly
**Depends on**: Phase 4
**Requirements**: CMD-02, CMD-03, CMD-08
**Success Criteria** (what must be TRUE):
  1. `git add <files>` stages specified files via `sl add`
  2. `git commit -m "message"` creates commit with message via `sl commit`
  3. `git add -A` stages all changes including new/deleted files via `sl addremove`
**E2E Tests**:
  - Test `git add file.txt`: verify file staged
  - Test `git commit -m "msg"`: verify commit created, message correct
  - Test `git add -A`: verify new, modified, and deleted files all staged
  - Test workflow: add -> commit -> status shows clean
**Plans**: 1 plan

Plans:
- [x] 05-01-PLAN.md - Add and commit handlers with flag translation for -A/--all

### Phase 6: Status Output Emulation
**Goal**: Status output matches git's format exactly for tooling compatibility
**Depends on**: Phase 4
**Requirements**: FLAG-01, FLAG-02
**Success Criteria** (what must be TRUE):
  1. `git status --porcelain` outputs 2-character status codes matching git exactly
  2. `git status --short` outputs abbreviated status matching git format
  3. Tools parsing git status output (like get-shit-done) work without modification
**E2E Tests** (EXACT MATCH required):
  - Test `--porcelain` with: new file, modified file, deleted file, renamed file
  - Test `--short` with same scenarios
  - Compare output byte-for-byte with git output
  - Test mixed states (some staged, some not)
**Plans**: 1 plan

Plans:
- [x] 06-01-PLAN.md - Porcelain and short output transformation with E2E tests

### Phase 7: Log Output Emulation
**Goal**: Log output supports git's format options
**Depends on**: Phase 4
**Requirements**: FLAG-04, FLAG-05
**Success Criteria** (what must be TRUE):
  1. `git log --oneline` outputs `<hash> <subject>` format via sl template
  2. `git log -N` limits output to N commits via `sl log -l N`
  3. `git log --oneline -5` combines both flags correctly
**E2E Tests**:
  - Test `--oneline` format matches git (semantic: hash length may differ)
  - Test `-N` limits correctly: create 10 commits, verify `-3` shows 3
  - Test combined flags work together
**Plans**: 1 plan

Plans:
- [x] 07-01-PLAN.md - Flag translation for --oneline and -N with E2E tests

### Phase 8: Add -u Emulation
**Goal**: Stage only modified tracked files (exclude new files)
**Depends on**: Phase 5
**Requirements**: FLAG-03
**Success Criteria** (what must be TRUE):
  1. `git add -u` finds modified tracked files via `sl status -m` and stages them
  2. Untracked files are NOT staged when using -u
  3. Deleted files are marked for removal when using -u
**E2E Tests**:
  - Test with modified tracked file + untracked file: only tracked staged
  - Test with deleted tracked file: marked for removal
  - Compare `git status --porcelain` before/after between git and gitsl
**Plans**: 1 plan

Plans:
- [x] 08-01-PLAN.md - Implement -u/--update flag with deleted file handling

### Phase 9: Unsupported Command Handling
**Goal**: Gracefully handle commands we cannot translate
**Depends on**: Phase 3
**Requirements**: UNSUP-01, UNSUP-02
**Success Criteria** (what must be TRUE):
  1. Unsupported commands print original git command to stderr
  2. Unsupported commands exit with code 0 (prevent calling tool from failing)
  3. Message clearly indicates command is not supported by shim
**E2E Tests**:
  - Test `git push` (unsupported): verify exit 0, stderr contains message
  - Test `git rebase` (unsupported): same
  - Verify stdout is empty for unsupported commands
**Plans**: TBD

Plans:
- [ ] 09-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Script Skeleton | 1/1 | Complete | 2026-01-18 |
| 2. E2E Test Infrastructure | 2/2 | Complete | 2026-01-18 |
| 3. Execution Pipeline | 2/2 | Complete | 2026-01-18 |
| 4. Direct Command Mappings | 2/2 | Complete | 2026-01-18 |
| 5. File Operation Commands | 1/1 | Complete | 2026-01-18 |
| 6. Status Output Emulation | 1/1 | Complete | 2026-01-18 |
| 7. Log Output Emulation | 1/1 | Complete | 2026-01-18 |
| 8. Add -u Emulation | 1/1 | Complete | 2026-01-18 |
| 9. Unsupported Command Handling | 0/? | Not started | - |

---
*Roadmap created: 2026-01-17*
*Last updated: 2026-01-18 - Phase 8 complete (add -u emulation)*
