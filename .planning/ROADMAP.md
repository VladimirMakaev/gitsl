# Roadmap: GitSL

## Milestones

- **v1.0 MVP** - Phases 01-09 (shipped 2026-01-18)
- **v1.1 Polish & Documentation** - Phases 10-14 (shipped 2026-01-19)
- **v1.2 More Commands Support** - Phases 15-19 (in progress)

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

<details>
<summary>v1.1 Polish & Documentation (Phases 10-14) - SHIPPED 2026-01-19</summary>

### Phase 10: Cleanup
**Goal**: Remove all external tool references from code and comments
**Plans**: 1 plan (complete)

### Phase 11: Testing
**Goal**: Comprehensive test infrastructure with improved runner and coverage
**Plans**: 2 plans (complete)

### Phase 12: Packaging
**Goal**: gitsl installable via pip with proper entry points
**Plans**: 1 plan (complete)

### Phase 13: CI/CD
**Goal**: Automated testing on all platforms with release automation
**Plans**: 2 plans (complete)

### Phase 14: Documentation
**Goal**: Production-quality README with installation, usage, and command matrix
**Plans**: 1 plan (complete)

</details>

<details open>
<summary>v1.2 More Commands Support (Phases 15-19) - IN PROGRESS</summary>

### Phase 15: Direct Pass-through Commands

**Goal**: Users can view commits, blame files, and perform file operations with simple git commands

**Dependencies**: None (builds on existing cmd_*.py pattern)

**Plans**: 2 plans

Plans:
- [x] 15-01-PLAN.md - Create 6 command handlers and dispatch routing
- [x] 15-02-PLAN.md - E2E tests for all 6 commands

**Requirements**:
- SHOW-01, SHOW-02 (git show)
- BLAME-01, BLAME-02 (git blame)
- RM-01, RM-02, RM-03 (git rm)
- MV-01, MV-02 (git mv)
- CLONE-01, CLONE-02 (git clone)
- GREP-01, GREP-02 (git grep)

**Success Criteria**:
1. User can run `git show` to view the most recent commit
2. User can run `git blame <file>` to see per-line annotations
3. User can run `git rm <file>` to remove tracked files
4. User can run `git mv <src> <dst>` to rename/move files
5. User can run `git clone <url>` to clone a repository

---

### Phase 16: Flag Translation Commands

**Goal**: Users can run config, clean, and switch commands with proper flag translation to Sapling equivalents

**Dependencies**: Phase 15 (establishes handler pattern rhythm)

**Plans**: 2 plans

Plans:
- [x] 16-01-PLAN.md - Create 3 command handlers (clean, config, switch) with flag translation
- [x] 16-02-PLAN.md - E2E tests for all 8 requirements

**Requirements**:
- CLEAN-01, CLEAN-02, CLEAN-03 (git clean)
- CONFIG-01, CONFIG-02, CONFIG-03 (git config)
- SWITCH-01, SWITCH-02 (git switch)

**Success Criteria**:
1. User can run `git clean -f` to remove untracked files
2. User can run `git clean -n` to preview files that would be removed (dry run)
3. User can run `git config <key>` to read configuration values
4. User can run `git config <key> <value>` to set configuration values
5. User can run `git switch <branch>` to change branches

---

### Phase 17: Branch and Restore

**Goal**: Users can manage branches (bookmarks) and restore files to previous states

**Dependencies**: Phase 16 (switch establishes goto pattern)

**Requirements**:
- BRANCH-01, BRANCH-02, BRANCH-03, BRANCH-04 (git branch)
- RESTORE-01, RESTORE-02 (git restore)

**Success Criteria**:
1. User can run `git branch` to list all bookmarks
2. User can run `git branch <name>` to create a new bookmark
3. User can run `git branch -d <name>` to delete a bookmark
4. User can run `git restore <file>` to discard uncommitted changes to a file
5. User can run `git restore .` to discard all uncommitted changes

---

### Phase 18: Stash Operations

**Goal**: Users can save, restore, list, and manage temporary changes using git stash workflow

**Dependencies**: Phase 17 (restore pattern informs stash apply)

**Requirements**:
- STASH-01, STASH-02, STASH-03 (stash save)
- STASH-04 (stash pop)
- STASH-05 (stash apply)
- STASH-06 (stash list)
- STASH-07 (stash drop)

**Success Criteria**:
1. User can run `git stash` to save uncommitted changes
2. User can run `git stash pop` to apply and remove the most recent stash
3. User can run `git stash apply` to apply stash without removing it
4. User can run `git stash list` to see all saved stashes
5. User can run `git stash drop` to delete the most recent stash

---

### Phase 19: Checkout Command

**Goal**: Users can use the overloaded git checkout command with correct disambiguation between switching branches, restoring files, and creating branches

**Dependencies**: Phase 17 (branch pattern), Phase 16 (switch pattern), Phase 17 (restore pattern)

**Requirements**:
- CHECKOUT-01 (checkout commit)
- CHECKOUT-02 (checkout branch)
- CHECKOUT-03, CHECKOUT-04 (checkout file)
- CHECKOUT-05 (checkout -b)
- CHECKOUT-06 (disambiguation logic)

**Success Criteria**:
1. User can run `git checkout <branch>` to switch to an existing branch
2. User can run `git checkout -b <name>` to create and switch to a new branch
3. User can run `git checkout -- <file>` to restore a file to its committed state
4. User can run `git checkout <commit>` to check out a specific commit
5. Ambiguous arguments (file with same name as branch) are correctly disambiguated

</details>

## Progress

**Execution Order:**
Phases execute in numeric order.

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
| 12. Packaging | v1.1 | 1/1 | Complete | 2026-01-19 |
| 13. CI/CD | v1.1 | 2/2 | Complete | 2026-01-19 |
| 14. Documentation | v1.1 | 1/1 | Complete | 2026-01-19 |
| 15. Direct Pass-through | v1.2 | 2/2 | Complete | 2026-01-19 |
| 16. Flag Translation | v1.2 | 2/2 | Complete | 2026-01-19 |
| 17. Branch and Restore | v1.2 | 0/? | Pending | - |
| 18. Stash Operations | v1.2 | 0/? | Pending | - |
| 19. Checkout Command | v1.2 | 0/? | Pending | - |
