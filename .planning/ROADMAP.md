# Roadmap: GitSL

## Milestones

- **v1.0 MVP** - Phases 01-09 (shipped 2026-01-18)
- **v1.1 Polish & Documentation** - Phases 10-14 (shipped 2026-01-19)
- **v1.2 More Commands Support** - Phases 15-19 (shipped 2026-01-20)
- **v1.3 Flag Compatibility** - Phases 20-29 (in progress)

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
**Plans**: 2 plans (complete)

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

<details>
<summary>v1.2 More Commands Support (Phases 15-19) - SHIPPED 2026-01-20</summary>

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

**Plans**: 2 plans

Plans:
- [x] 17-01-PLAN.md - Create branch and restore command handlers with dispatch routing
- [x] 17-02-PLAN.md - E2E tests for all 6 requirements

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

**Plans**: 2 plans

Plans:
- [x] 18-01-PLAN.md - Create stash command handler with subcommand dispatch
- [x] 18-02-PLAN.md - E2E tests for all 7 stash requirements

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

**Plans**: 2 plans

Plans:
- [x] 19-01-PLAN.md - Create checkout command handler with disambiguation logic
- [x] 19-02-PLAN.md - E2E tests for all 6 checkout requirements

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

<details open>
<summary>v1.3 Flag Compatibility (Phases 20-29) - IN PROGRESS</summary>

### Phase 20: Critical Safety Fixes

**Goal**: Users are protected from destructive or unexpected behavior when using flags with semantic differences between git and sl

**Dependencies**: None (safety-critical, must be first)

**Plans**: 1 plan

Plans:
- [x] 20-01-PLAN.md - Implement safety fixes for commit -a, checkout -f/-m, verify branch -D

**Requirements**:
- SAFE-01: `commit -a` removes the flag rather than translating to sl -A
- SAFE-02: `checkout -f/--force` translates to `sl goto -C`
- SAFE-03: `checkout -m/--merge` translates to `sl goto -m`
- SAFE-04: Verify `branch -D` to `-d` translation is complete

**Success Criteria**:
1. User running `git commit -a` commits only tracked modified files, not untracked files
2. User running `git checkout -f <branch>` can switch branches while discarding uncommitted changes
3. User running `git checkout -m <branch>` merges local changes during branch switch
4. User running `git branch -D <name>` deletes only the bookmark label, never strips commits

---

### Phase 21: Rev-Parse Expansion

**Goal**: Users can query repository metadata using git rev-parse flags that tools commonly depend on

**Dependencies**: Phase 20 (safety fixes complete)

**Requirements**:
- REVP-01: `--show-toplevel` translates to `sl root`
- REVP-02: `--git-dir` returns `.sl` directory path
- REVP-03: `--is-inside-work-tree` returns true/false
- REVP-04: `--abbrev-ref HEAD` returns current bookmark name
- REVP-05: `--verify` validates object reference
- REVP-06: `--symbolic` outputs in symbolic form
- REVP-07: Document `--short HEAD` already implemented

**Success Criteria**:
1. User running `git rev-parse --show-toplevel` gets the repository root path
2. User running `git rev-parse --git-dir` gets the `.sl` directory path
3. User running `git rev-parse --is-inside-work-tree` gets `true` when inside repo
4. User running `git rev-parse --abbrev-ref HEAD` gets the current bookmark name
5. Tools that check repository state via rev-parse work correctly with gitsl

---

### Phase 22: Log Flags

**Goal**: Users can filter, format, and customize git log output using the full range of commonly-used git log flags

**Dependencies**: Phase 21 (rev-parse provides commit resolution)

**Requirements**:
- LOG-01: `--graph` translates to `sl log -G`
- LOG-02: `--stat` passes through to `sl log --stat`
- LOG-03: `--patch/-p` passes through to `sl log -p`
- LOG-04: `--author=<pattern>` translates to `sl log -u <pattern>`
- LOG-05: `--grep=<pattern>` translates to `sl log -k <pattern>`
- LOG-06: `--no-merges` translates to `sl log --no-merges`
- LOG-07: `--all` translates to `sl log --all`
- LOG-08: `--follow` translates to `sl log -f`
- LOG-09: `--since/--after` translates to `sl log -d` with date format
- LOG-10: `--until/--before` translates to `sl log -d` with date format
- LOG-11: `--name-only` produces filename-only output
- LOG-12: `--name-status` produces status+filename output
- LOG-13: `--decorate` shows branch/bookmark names on commits
- LOG-14: `--pretty/--format` maps to `sl log -T` template
- LOG-15: `--first-parent` follows only first parent of merges
- LOG-16: `--reverse` shows commits in reverse chronological order
- LOG-17: `-S<string>` searches for string changes in diffs (pickaxe)
- LOG-18: `-G<regex>` searches for regex changes in diffs
- LOG-19: Document `-n/--max-count` already implemented
- LOG-20: Document `--oneline` already implemented

**Success Criteria**:
1. User running `git log --graph` sees ASCII commit graph
2. User running `git log --author=<name>` sees only commits by that author
3. User running `git log --since="1 week ago"` sees only recent commits
4. User running `git log --stat` sees diffstat with each commit
5. User running `git log --name-only` sees only filenames changed per commit

---

### Phase 23: Diff and Show Flags

**Goal**: Users can customize diff and show output using standard git flags for context, formatting, and filtering

**Dependencies**: Phase 22 (log patterns inform diff/show)

**Requirements**:
- DIFF-01: `--stat` passes through to `sl diff --stat`
- DIFF-02: `-w/--ignore-all-space` passes through to `sl diff -w`
- DIFF-03: `-b/--ignore-space-change` passes through to `sl diff -b`
- DIFF-04: `-U<n>/--unified=<n>` passes through to `sl diff -U`
- DIFF-05: `--name-only` produces filename-only output
- DIFF-06: `--name-status` produces status+filename output
- DIFF-07: `--staged/--cached` warns that Sapling has no staging area
- DIFF-08: `--raw` produces raw format output
- DIFF-09: `-M/--find-renames` enables rename detection
- DIFF-10: `-C/--find-copies` enables copy detection
- DIFF-11: `--word-diff` shows word-level differences
- DIFF-12: `--color-moved` highlights moved lines
- SHOW-01: `--stat` passes through to `sl show --stat`
- SHOW-02: `-U<n>` passes through for context lines
- SHOW-03: `-w` passes through to ignore whitespace
- SHOW-04: `--name-only` produces filename-only output
- SHOW-05: `--name-status` produces status+filename output
- SHOW-06: `--pretty/--format` maps to template formatting
- SHOW-07: `-s/--no-patch` suppresses diff output
- SHOW-08: `--oneline` produces short format output

**Success Criteria**:
1. User running `git diff --stat` sees diffstat summary
2. User running `git diff -w` ignores whitespace differences
3. User running `git diff --staged` receives a helpful warning about no staging area
4. User running `git show --stat <commit>` sees diffstat for that commit
5. User running `git show -s <commit>` sees commit info without the diff

---

### Phase 24: Status and Add Flags

**Goal**: Users can customize status and add behavior with standard git flags for filtering and verbosity

**Dependencies**: Phase 23 (diff patterns apply to status output)

**Requirements**:
- STAT-01: `--ignored` translates to `sl status -i`
- STAT-02: `-b/--branch` adds branch info to output
- STAT-03: `-v/--verbose` passes through for verbose output
- STAT-04: Verify `--porcelain` and `--short` emulation covers all status codes
- STAT-05: `-u/--untracked-files[=<mode>]` controls untracked file display
- ADD-01: Verify `-A/--all` to `addremove` translation
- ADD-02: Verify `-u/--update` emulation for modified tracked files
- ADD-03: `--dry-run/-n` shows what would be added
- ADD-04: `-f/--force` adds ignored files
- ADD-05: `-v/--verbose` shows files as they are added

**Success Criteria**:
1. User running `git status --ignored` sees ignored files in output
2. User running `git status -b` sees current branch name in status output
3. User running `git add -n <file>` sees what would be added without adding
4. User running `git add -f <ignored-file>` can force-add ignored files
5. User running `git status -u no` suppresses untracked file listing

---

### Phase 25: Commit and Branch Flags

**Goal**: Users can use advanced commit and branch management flags for amending, authoring, and branch organization

**Dependencies**: Phase 24 (add flags inform commit workflow)

**Requirements**:
- COMM-01: `--amend` translates to `sl amend` command
- COMM-02: `--no-edit` combined with amend uses existing message
- COMM-03: `-F <file>/--file=<file>` translates to `sl commit -l <file>`
- COMM-04: `--author=<author>` translates to `sl commit -u <author>`
- COMM-05: `--date=<date>` translates to `sl commit -d <date>`
- COMM-06: `-v/--verbose` shows diff in commit message editor
- COMM-07: `-s/--signoff` adds Signed-off-by trailer
- COMM-08: `-n/--no-verify` bypasses pre-commit hooks
- BRAN-01: `-m <old> <new>` translates to `sl bookmark -m <old> <new>`
- BRAN-02: `-a/--all` shows all bookmarks including remote
- BRAN-03: `-r/--remotes` shows remote bookmarks only
- BRAN-04: `-v/--verbose` shows commit info with each branch
- BRAN-05: `-l/--list` lists branches matching pattern
- BRAN-06: `--show-current` shows current branch name
- BRAN-07: `-t/--track` sets up upstream tracking
- BRAN-08: `-f/--force` forces branch operations
- BRAN-09: `-c/--copy` copies a branch

**Success Criteria**:
1. User running `git commit --amend` can modify the last commit
2. User running `git commit --amend --no-edit` amends without changing message
3. User running `git branch -m old new` renames a branch
4. User running `git branch -a` sees all branches including remote
5. User running `git branch --show-current` sees just the current branch name

---

### Phase 26: Stash and Checkout/Switch/Restore Flags

**Goal**: Users can use the full range of stash, checkout, switch, and restore flags for flexible working tree management

**Dependencies**: Phase 25 (branch flags inform checkout/switch)

**Requirements**:
- STSH-01: `-u/--include-untracked` translates to `sl shelve -u`
- STSH-02: `-m/--message` translates to `sl shelve -m`
- STSH-03: `stash show --stat` displays shelve diff statistics
- STSH-04: `stash@{n}` reference syntax maps to shelve names
- STSH-05: `-p/--patch` interactive mode passes through to `sl shelve -i`
- STSH-06: `-k/--keep-index` warns about no staging area
- STSH-07: `-a/--all` stashes all files including ignored
- STSH-08: `-q/--quiet` suppresses output
- STSH-09: `stash push <pathspec>` supports selective file stashing
- STSH-10: `stash branch <name>` creates branch from stash
- CHKT-01: `switch -c/--create` translates to `sl bookmark` + `sl goto`
- CHKT-02: `switch -C/--force-create` force creates bookmark if exists
- CHKT-03: `restore --source=<tree>/-s <tree>` translates to `sl revert -r <rev>`
- CHKT-04: `restore --staged/-S` warns about no staging area
- CHKT-05: `checkout --detach` passes through (sl has no attached concept)
- CHKT-06: `checkout -t/--track` sets up upstream tracking for new branch
- CHKT-07: `switch -d/--detach` switches to commit without branch
- CHKT-08: `switch -f/--force/--discard-changes` discards local changes
- CHKT-09: `switch -m/--merge` merges local changes during switch
- CHKT-10: `restore -q/--quiet` suppresses output
- CHKT-11: `restore -W/--worktree` explicitly restores working tree

**Success Criteria**:
1. User running `git stash -u` includes untracked files in stash
2. User running `git stash -m "message"` can label their stash
3. User running `git switch -c newbranch` creates and switches to new branch
4. User running `git restore -s HEAD~1 file` restores file from specific commit
5. User running `git stash show --stat` sees diffstat of stashed changes

---

### Phase 27: Grep and Blame Flags

**Goal**: Users can search code and view file history with the full range of grep and blame flags

**Dependencies**: Phase 26 (stash patterns complete, now content search)

**Requirements**:
- GREP-01: `-n` passes through to `sl grep -n` (line numbers)
- GREP-02: `-i` passes through to `sl grep -i` (case insensitive)
- GREP-03: `-l` passes through to `sl grep -l` (files only)
- GREP-04: `-c` passes through to `sl grep -c` (count)
- GREP-05: `-w` passes through to `sl grep -w` (word match)
- GREP-06: `-v` passes through for inverted match
- GREP-07: `-A <num>` shows trailing context lines
- GREP-08: `-B <num>` shows leading context lines
- GREP-09: `-C <num>` shows both context lines
- GREP-10: `-h` suppresses filename output
- GREP-11: `-H` forces filename output
- GREP-12: `-o/--only-matching` shows only matched parts
- GREP-13: `-q/--quiet` suppresses output, exit status only
- GREP-14: `-F/--fixed-strings` treats pattern as literal string
- BLAM-01: `-w` passes through to `sl annotate -w`
- BLAM-02: `-b` passes through to `sl annotate -b`
- BLAM-03: `-L <start>,<end>` line range support
- BLAM-04: `-e/--show-email` shows author email
- BLAM-05: `-p/--porcelain` produces machine-readable output
- BLAM-06: `-l` shows long revision hash
- BLAM-07: `-n/--show-number` shows original line numbers

**Success Criteria**:
1. User running `git grep -n pattern` sees line numbers with matches
2. User running `git grep -i pattern` performs case-insensitive search
3. User running `git grep -C 3 pattern` sees 3 lines of context around matches
4. User running `git blame -L 10,20 file` sees blame for only lines 10-20
5. User running `git blame -w file` ignores whitespace when determining blame

---

### Phase 28: Clone, Rm, Mv, Clean, Config Flags

**Goal**: Users can use the full range of flags for repository cloning and file/config management

**Dependencies**: Phase 27 (grep/blame complete, now utility commands)

**Requirements**:
- CLON-01: `-b <branch>/--branch` translates to `sl clone -u <bookmark>`
- CLON-02: `--depth` translates to `sl clone --shallow`
- CLON-03: `--single-branch` behavior with shallow clone
- CLON-04: `-o/--origin <name>` sets custom remote name
- CLON-05: `-n/--no-checkout` skips checkout after clone
- CLON-06: `--recursive/--recurse-submodules` clones with submodules
- CLON-07: `--no-tags` skips tag cloning
- CLON-08: `-q/--quiet` suppresses output
- CLON-09: `-v/--verbose` increases output verbosity
- RM-01: `-f/--force` passes through for forced removal
- RM-02: `--cached` warns about no staging area
- RM-03: `-n/--dry-run` previews removal without executing
- RM-04: `-q/--quiet` suppresses output
- RM-05: Verify `-r/--recursive` filtering (sl remove is recursive by default)
- MV-01: `-f/--force` passes through for forced move
- MV-02: `-k` skip errors and continue
- MV-03: `-v/--verbose` shows files as they are moved
- MV-04: `-n/--dry-run` previews move without executing
- CLEN-01: `-x` translates to `sl purge --all` (remove ignored too)
- CLEN-02: `-X` removes only ignored files
- CLEN-03: `-e <pattern>` translates to `sl purge -X` exclude pattern
- CLEN-04: Verify `-f`, `-d`, `-n` already implemented correctly
- CONF-01: `--get` for reading specific key
- CONF-02: `--unset` for removing a key
- CONF-03: `--list/-l` shows all configuration
- CONF-04: Verify `--global` to `--user` translation
- CONF-05: `--local` scopes to repository config
- CONF-06: `--system` scopes to system-wide config
- CONF-07: `--show-origin` displays where value comes from
- CONF-08: `--all` gets all values for multi-valued keys

**Success Criteria**:
1. User running `git clone -b main <url>` clones and checks out the main branch
2. User running `git clone --depth 1 <url>` creates a shallow clone
3. User running `git rm --dry-run <file>` previews what would be removed
4. User running `git clean -x` removes both untracked and ignored files
5. User running `git config --list` sees all configuration values

---

### Phase 29: Documentation

**Goal**: Users have complete documentation of all flag compatibility, including clear explanations for unsupported flags and helpful error messages

**Dependencies**: Phase 28 (all implementation complete, document final state)

**Requirements**:
- DOC-01: Create comprehensive flag compatibility matrix in README
- DOC-02: Document all staging-related flags as unsupported with explanation
- DOC-03: Document interactive mode limitations (`-i`, `-p` for patch selection)
- DOC-04: Add helpful error messages for unsupported flags
- DOC-05: Document already-implemented flags that were missing from docs

**Success Criteria**:
1. User can find a complete flag compatibility matrix in README.md
2. User encountering unsupported staging flags gets a clear explanation
3. User encountering interactive mode flags gets a clear explanation
4. All supported flags are documented with their Sapling equivalents
5. README accurately reflects the full v1.3 flag compatibility status

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
| 17. Branch and Restore | v1.2 | 2/2 | Complete | 2026-01-20 |
| 18. Stash Operations | v1.2 | 2/2 | Complete | 2026-01-20 |
| 19. Checkout Command | v1.2 | 2/2 | Complete | 2026-01-20 |
| 20. Critical Safety Fixes | v1.3 | 1/1 | Complete | 2026-01-20 |
| 21. Rev-Parse Expansion | v1.3 | 0/? | Pending | — |
| 22. Log Flags | v1.3 | 0/? | Pending | — |
| 23. Diff and Show Flags | v1.3 | 0/? | Pending | — |
| 24. Status and Add Flags | v1.3 | 0/? | Pending | — |
| 25. Commit and Branch Flags | v1.3 | 0/? | Pending | — |
| 26. Stash and Checkout/Switch/Restore Flags | v1.3 | 0/? | Pending | — |
| 27. Grep and Blame Flags | v1.3 | 0/? | Pending | — |
| 28. Clone, Rm, Mv, Clean, Config Flags | v1.3 | 0/? | Pending | — |
| 29. Documentation | v1.3 | 0/? | Pending | — |
