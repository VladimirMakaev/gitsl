# Requirements: GitSL v1.3 Flag Compatibility

**Defined:** 2026-01-20
**Core Value:** Git commands execute correctly against Sapling repos without the calling tool knowing the difference

## v1.3 Requirements

Exhaustive flag coverage for all 25 supported git commands. Requirements organized by command category.

### Safety Fixes

Critical behavioral corrections for flags with semantic differences.

- [x] **SAFE-01**: `commit -a` removes the flag rather than translating to sl -A (prevents adding untracked files)
- [x] **SAFE-02**: `checkout -f/--force` translates to `sl goto -C` for forcing switch with uncommitted changes
- [x] **SAFE-03**: `checkout -m/--merge` translates to `sl goto -m` to merge local changes during switch
- [x] **SAFE-04**: Verify `branch -D` → `-d` translation is complete (already implemented, needs test coverage)

### Log Flags

Git log flag support and translation.

- [x] **LOG-01**: `--graph` translates to `sl log -G`
- [x] **LOG-02**: `--stat` passes through to `sl log --stat`
- [x] **LOG-03**: `--patch/-p` passes through to `sl log -p`
- [x] **LOG-04**: `--author=<pattern>` translates to `sl log -u <pattern>`
- [x] **LOG-05**: `--grep=<pattern>` translates to `sl log -k <pattern>`
- [x] **LOG-06**: `--no-merges` translates to `sl log --no-merges`
- [x] **LOG-07**: `--all` translates to `sl log --all`
- [x] **LOG-08**: `--follow` translates to `sl log -f`
- [x] **LOG-09**: `--since/--after` translates to `sl log -d` with date format handling
- [x] **LOG-10**: `--until/--before` translates to `sl log -d` with date format handling
- [x] **LOG-11**: `--name-only` produces filename-only output
- [x] **LOG-12**: `--name-status` produces status+filename output
- [x] **LOG-13**: `--decorate` shows branch/bookmark names on commits
- [x] **LOG-14**: `--pretty/--format` maps to `sl log -T` template
- [x] **LOG-15**: `--first-parent` follows only first parent of merges
- [x] **LOG-16**: `--reverse` shows commits in reverse chronological order
- [x] **LOG-17**: `-S<string>` searches for string changes in diffs (pickaxe)
- [x] **LOG-18**: `-G<regex>` searches for regex changes in diffs
- [x] **LOG-19**: Document `-n/--max-count` already implemented (translate to `-l`)
- [x] **LOG-20**: Document `--oneline` already implemented

### Diff Flags

Git diff flag support.

- [ ] **DIFF-01**: `--stat` passes through to `sl diff --stat`
- [ ] **DIFF-02**: `-w/--ignore-all-space` passes through to `sl diff -w`
- [ ] **DIFF-03**: `-b/--ignore-space-change` passes through to `sl diff -b`
- [ ] **DIFF-04**: `-U<n>/--unified=<n>` passes through to `sl diff -U`
- [ ] **DIFF-05**: `--name-only` produces filename-only output
- [ ] **DIFF-06**: `--name-status` produces status+filename output
- [ ] **DIFF-07**: `--staged/--cached` warns that Sapling has no staging area
- [ ] **DIFF-08**: `--raw` produces raw format output
- [ ] **DIFF-09**: `-M/--find-renames` enables rename detection
- [ ] **DIFF-10**: `-C/--find-copies` enables copy detection
- [ ] **DIFF-11**: `--word-diff` shows word-level differences
- [ ] **DIFF-12**: `--color-moved` highlights moved lines

### Status Flags

Git status flag support.

- [ ] **STAT-01**: `--ignored` translates to `sl status -i`
- [ ] **STAT-02**: `-b/--branch` adds branch info to output
- [ ] **STAT-03**: `-v/--verbose` passes through for verbose output
- [ ] **STAT-04**: Verify `--porcelain` and `--short` emulation covers all status codes
- [ ] **STAT-05**: `-u/--untracked-files[=<mode>]` controls untracked file display

### Commit Flags

Git commit flag support.

- [ ] **COMM-01**: `--amend` translates to `sl amend` command
- [ ] **COMM-02**: `--no-edit` combined with amend uses existing message
- [ ] **COMM-03**: `-F <file>/--file=<file>` translates to `sl commit -l <file>`
- [ ] **COMM-04**: `--author=<author>` translates to `sl commit -u <author>`
- [ ] **COMM-05**: `--date=<date>` translates to `sl commit -d <date>`
- [ ] **COMM-06**: `-v/--verbose` shows diff in commit message editor
- [ ] **COMM-07**: `-s/--signoff` adds Signed-off-by trailer
- [ ] **COMM-08**: `-n/--no-verify` bypasses pre-commit hooks

### Stash Flags

Git stash flag support.

- [ ] **STSH-01**: `-u/--include-untracked` translates to `sl shelve -u`
- [ ] **STSH-02**: `-m/--message` translates to `sl shelve -m`
- [ ] **STSH-03**: `stash show --stat` displays shelve diff statistics
- [ ] **STSH-04**: `stash@{n}` reference syntax maps to shelve names
- [ ] **STSH-05**: `-p/--patch` interactive mode passes through to `sl shelve -i`
- [ ] **STSH-06**: `-k/--keep-index` warns about no staging area
- [ ] **STSH-07**: `-a/--all` stashes all files including ignored
- [ ] **STSH-08**: `-q/--quiet` suppresses output
- [ ] **STSH-09**: `stash push <pathspec>` supports selective file stashing
- [ ] **STSH-10**: `stash branch <name>` creates branch from stash

### Branch Flags

Git branch flag support.

- [ ] **BRAN-01**: `-m <old> <new>` translates to `sl bookmark -m <old> <new>`
- [ ] **BRAN-02**: `-a/--all` shows all bookmarks including remote
- [ ] **BRAN-03**: `-r/--remotes` shows remote bookmarks only
- [ ] **BRAN-04**: `-v/--verbose` shows commit info with each branch
- [ ] **BRAN-05**: `-l/--list` lists branches matching pattern
- [ ] **BRAN-06**: `--show-current` shows current branch name
- [ ] **BRAN-07**: `-t/--track` sets up upstream tracking
- [ ] **BRAN-08**: `-f/--force` forces branch operations
- [ ] **BRAN-09**: `-c/--copy` copies a branch

### Checkout/Switch/Restore Flags

Git checkout, switch, and restore flag support.

- [ ] **CHKT-01**: `switch -c/--create` translates to `sl bookmark` + `sl goto`
- [ ] **CHKT-02**: `switch -C/--force-create` force creates bookmark if exists
- [ ] **CHKT-03**: `restore --source=<tree>/-s <tree>` translates to `sl revert -r <rev>`
- [ ] **CHKT-04**: `restore --staged/-S` warns about no staging area
- [ ] **CHKT-05**: `checkout --detach` passes through (sl doesn't have attached concept)
- [ ] **CHKT-06**: `checkout -t/--track` sets up upstream tracking for new branch
- [ ] **CHKT-07**: `switch -d/--detach` switches to commit without branch
- [ ] **CHKT-08**: `switch -f/--force/--discard-changes` discards local changes
- [ ] **CHKT-09**: `switch -m/--merge` merges local changes during switch
- [ ] **CHKT-10**: `restore -q/--quiet` suppresses output
- [ ] **CHKT-11**: `restore -W/--worktree` explicitly restores working tree

### Show Flags

Git show flag support.

- [ ] **SHOW-01**: `--stat` passes through to `sl show --stat`
- [ ] **SHOW-02**: `-U<n>` passes through for context lines
- [ ] **SHOW-03**: `-w` passes through to ignore whitespace
- [ ] **SHOW-04**: `--name-only` produces filename-only output
- [ ] **SHOW-05**: `--name-status` produces status+filename output
- [ ] **SHOW-06**: `--pretty/--format` maps to template formatting
- [ ] **SHOW-07**: `-s/--no-patch` suppresses diff output
- [ ] **SHOW-08**: `--oneline` produces short format output

### Blame Flags

Git blame flag support.

- [ ] **BLAM-01**: `-w` passes through to `sl annotate -w` (ignore whitespace)
- [ ] **BLAM-02**: `-b` passes through to `sl annotate -b` (ignore space changes)
- [ ] **BLAM-03**: `-L <start>,<end>` line range support
- [ ] **BLAM-04**: `-e/--show-email` shows author email
- [ ] **BLAM-05**: `-p/--porcelain` produces machine-readable output
- [ ] **BLAM-06**: `-l` shows long revision hash
- [ ] **BLAM-07**: `-n/--show-number` shows original line numbers

### Grep Flags

Git grep flag support.

- [ ] **GREP-01**: `-n` passes through to `sl grep -n` (line numbers)
- [ ] **GREP-02**: `-i` passes through to `sl grep -i` (case insensitive)
- [ ] **GREP-03**: `-l` passes through to `sl grep -l` (files only)
- [ ] **GREP-04**: `-c` passes through to `sl grep -c` (count)
- [ ] **GREP-05**: `-w` passes through to `sl grep -w` (word match)
- [ ] **GREP-06**: `-v` passes through for inverted match
- [ ] **GREP-07**: `-A <num>` shows trailing context lines
- [ ] **GREP-08**: `-B <num>` shows leading context lines
- [ ] **GREP-09**: `-C <num>` shows both context lines
- [ ] **GREP-10**: `-h` suppresses filename output
- [ ] **GREP-11**: `-H` forces filename output
- [ ] **GREP-12**: `-o/--only-matching` shows only matched parts
- [ ] **GREP-13**: `-q/--quiet` suppresses output, exit status only
- [ ] **GREP-14**: `-F/--fixed-strings` treats pattern as literal string

### Clean Flags

Git clean flag support.

- [ ] **CLEN-01**: `-x` translates to `sl purge --all` (remove ignored too)
- [ ] **CLEN-02**: `-X` removes only ignored files
- [ ] **CLEN-03**: `-e <pattern>` translates to `sl purge -X` exclude pattern
- [ ] **CLEN-04**: Verify `-f`, `-d`, `-n` already implemented correctly

### Config Flags

Git config flag support.

- [ ] **CONF-01**: `--get` for reading specific key
- [ ] **CONF-02**: `--unset` for removing a key
- [ ] **CONF-03**: `--list/-l` shows all configuration
- [ ] **CONF-04**: Verify `--global` → `--user` translation
- [ ] **CONF-05**: `--local` scopes to repository config
- [ ] **CONF-06**: `--system` scopes to system-wide config
- [ ] **CONF-07**: `--show-origin` displays where value comes from
- [ ] **CONF-08**: `--all` gets all values for multi-valued keys

### Rev-Parse Flags

Git rev-parse flag support.

- [x] **REVP-01**: `--show-toplevel` translates to `sl root`
- [x] **REVP-02**: `--git-dir` returns `.sl` directory path
- [x] **REVP-03**: `--is-inside-work-tree` returns true/false
- [x] **REVP-04**: `--abbrev-ref HEAD` returns current bookmark name
- [x] **REVP-05**: `--verify` validates object reference
- [x] **REVP-06**: `--symbolic` outputs in symbolic form
- [x] **REVP-07**: Document `--short HEAD` already implemented

### Add Flags

Git add flag support.

- [ ] **ADD-01**: Verify `-A/--all` → `addremove` translation
- [ ] **ADD-02**: Verify `-u/--update` emulation for modified tracked files
- [ ] **ADD-03**: `--dry-run/-n` shows what would be added
- [ ] **ADD-04**: `-f/--force` adds ignored files
- [ ] **ADD-05**: `-v/--verbose` shows files as they are added

### Clone Flags

Git clone flag support.

- [ ] **CLON-01**: `-b <branch>/--branch` translates to `sl clone -u <bookmark>`
- [ ] **CLON-02**: `--depth` translates to `sl clone --shallow`
- [ ] **CLON-03**: `--single-branch` behavior with shallow clone
- [ ] **CLON-04**: `-o/--origin <name>` sets custom remote name
- [ ] **CLON-05**: `-n/--no-checkout` skips checkout after clone
- [ ] **CLON-06**: `--recursive/--recurse-submodules` clones with submodules
- [ ] **CLON-07**: `--no-tags` skips tag cloning
- [ ] **CLON-08**: `-q/--quiet` suppresses output
- [ ] **CLON-09**: `-v/--verbose` increases output verbosity

### Rm Flags

Git rm flag support.

- [ ] **RM-01**: `-f/--force` passes through for forced removal
- [ ] **RM-02**: `--cached` warns about no staging area
- [ ] **RM-03**: `-n/--dry-run` previews removal without executing
- [ ] **RM-04**: `-q/--quiet` suppresses output
- [ ] **RM-05**: Verify `-r/--recursive` filtering (sl remove is recursive by default)

### Mv Flags

Git mv flag support.

- [ ] **MV-01**: `-f/--force` passes through for forced move
- [ ] **MV-02**: `-k` skip errors and continue
- [ ] **MV-03**: `-v/--verbose` shows files as they are moved
- [ ] **MV-04**: `-n/--dry-run` previews move without executing

### Documentation

Flag compatibility documentation updates.

- [ ] **DOC-01**: Create comprehensive flag compatibility matrix in README
- [ ] **DOC-02**: Document all staging-related flags as unsupported with explanation
- [ ] **DOC-03**: Document interactive mode limitations (`-i`, `-p` for patch selection)
- [ ] **DOC-04**: Add helpful error messages for unsupported flags
- [ ] **DOC-05**: Document already-implemented flags that were missing from docs

## Future Requirements (v2+)

Deferred to future releases.

### Advanced Formatting
- **FMT-01**: `log --pretty=format:` custom format templates (complex)
- **FMT-02**: `status --porcelain=v2` format support
- **FMT-03**: `blame --porcelain` machine-readable output (complex)

### Interactive Modes
- **INTR-01**: Full parity for `-p/--patch` interactive selection
- **INTR-02**: `add -i` interactive staging

### Edge Cases
- **EDGE-01**: `stash export/import` commands
- **EDGE-02**: `branch --contains/--merged/--no-merged` filtering
- **EDGE-03**: `checkout --orphan` for new root commits
- **EDGE-04**: `stash --index` on pop/apply (staging required)

## Out of Scope

| Feature | Reason |
|---------|--------|
| `--staged`/`--cached` flags | Sapling has no staging area — cannot emulate |
| `--index` on stash pop/apply | Staging area required |
| `commit --fixup/--squash` | Different workflow in Sapling (use sl fold) |
| Interactive rebase | Completely different model |
| `diff --diff-filter` | No sl equivalent |
| `log --walk-reflogs` | Sapling reflog differs |
| `stash --keep-index` | Staging area required (warn only) |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SAFE-01 | 20 | Complete |
| SAFE-02 | 20 | Complete |
| SAFE-03 | 20 | Complete |
| SAFE-04 | 20 | Complete |
| REVP-01 | 21 | Complete |
| REVP-02 | 21 | Complete |
| REVP-03 | 21 | Complete |
| REVP-04 | 21 | Complete |
| REVP-05 | 21 | Complete |
| REVP-06 | 21 | Complete |
| REVP-07 | 21 | Complete |
| LOG-01 | 22 | Complete |
| LOG-02 | 22 | Complete |
| LOG-03 | 22 | Complete |
| LOG-04 | 22 | Complete |
| LOG-05 | 22 | Complete |
| LOG-06 | 22 | Complete |
| LOG-07 | 22 | Complete |
| LOG-08 | 22 | Complete |
| LOG-09 | 22 | Complete |
| LOG-10 | 22 | Complete |
| LOG-11 | 22 | Complete |
| LOG-12 | 22 | Complete |
| LOG-13 | 22 | Complete |
| LOG-14 | 22 | Complete |
| LOG-15 | 22 | Complete |
| LOG-16 | 22 | Complete |
| LOG-17 | 22 | Complete |
| LOG-18 | 22 | Complete |
| LOG-19 | 22 | Complete |
| LOG-20 | 22 | Complete |
| DIFF-01 | 23 | Pending |
| DIFF-02 | 23 | Pending |
| DIFF-03 | 23 | Pending |
| DIFF-04 | 23 | Pending |
| DIFF-05 | 23 | Pending |
| DIFF-06 | 23 | Pending |
| DIFF-07 | 23 | Pending |
| DIFF-08 | 23 | Pending |
| DIFF-09 | 23 | Pending |
| DIFF-10 | 23 | Pending |
| DIFF-11 | 23 | Pending |
| DIFF-12 | 23 | Pending |
| SHOW-01 | 23 | Pending |
| SHOW-02 | 23 | Pending |
| SHOW-03 | 23 | Pending |
| SHOW-04 | 23 | Pending |
| SHOW-05 | 23 | Pending |
| SHOW-06 | 23 | Pending |
| SHOW-07 | 23 | Pending |
| SHOW-08 | 23 | Pending |
| STAT-01 | 24 | Pending |
| STAT-02 | 24 | Pending |
| STAT-03 | 24 | Pending |
| STAT-04 | 24 | Pending |
| STAT-05 | 24 | Pending |
| ADD-01 | 24 | Pending |
| ADD-02 | 24 | Pending |
| ADD-03 | 24 | Pending |
| ADD-04 | 24 | Pending |
| ADD-05 | 24 | Pending |
| COMM-01 | 25 | Pending |
| COMM-02 | 25 | Pending |
| COMM-03 | 25 | Pending |
| COMM-04 | 25 | Pending |
| COMM-05 | 25 | Pending |
| COMM-06 | 25 | Pending |
| COMM-07 | 25 | Pending |
| COMM-08 | 25 | Pending |
| BRAN-01 | 25 | Pending |
| BRAN-02 | 25 | Pending |
| BRAN-03 | 25 | Pending |
| BRAN-04 | 25 | Pending |
| BRAN-05 | 25 | Pending |
| BRAN-06 | 25 | Pending |
| BRAN-07 | 25 | Pending |
| BRAN-08 | 25 | Pending |
| BRAN-09 | 25 | Pending |
| STSH-01 | 26 | Pending |
| STSH-02 | 26 | Pending |
| STSH-03 | 26 | Pending |
| STSH-04 | 26 | Pending |
| STSH-05 | 26 | Pending |
| STSH-06 | 26 | Pending |
| STSH-07 | 26 | Pending |
| STSH-08 | 26 | Pending |
| STSH-09 | 26 | Pending |
| STSH-10 | 26 | Pending |
| CHKT-01 | 26 | Pending |
| CHKT-02 | 26 | Pending |
| CHKT-03 | 26 | Pending |
| CHKT-04 | 26 | Pending |
| CHKT-05 | 26 | Pending |
| CHKT-06 | 26 | Pending |
| CHKT-07 | 26 | Pending |
| CHKT-08 | 26 | Pending |
| CHKT-09 | 26 | Pending |
| CHKT-10 | 26 | Pending |
| CHKT-11 | 26 | Pending |
| GREP-01 | 27 | Pending |
| GREP-02 | 27 | Pending |
| GREP-03 | 27 | Pending |
| GREP-04 | 27 | Pending |
| GREP-05 | 27 | Pending |
| GREP-06 | 27 | Pending |
| GREP-07 | 27 | Pending |
| GREP-08 | 27 | Pending |
| GREP-09 | 27 | Pending |
| GREP-10 | 27 | Pending |
| GREP-11 | 27 | Pending |
| GREP-12 | 27 | Pending |
| GREP-13 | 27 | Pending |
| GREP-14 | 27 | Pending |
| BLAM-01 | 27 | Pending |
| BLAM-02 | 27 | Pending |
| BLAM-03 | 27 | Pending |
| BLAM-04 | 27 | Pending |
| BLAM-05 | 27 | Pending |
| BLAM-06 | 27 | Pending |
| BLAM-07 | 27 | Pending |
| CLON-01 | 28 | Pending |
| CLON-02 | 28 | Pending |
| CLON-03 | 28 | Pending |
| CLON-04 | 28 | Pending |
| CLON-05 | 28 | Pending |
| CLON-06 | 28 | Pending |
| CLON-07 | 28 | Pending |
| CLON-08 | 28 | Pending |
| CLON-09 | 28 | Pending |
| RM-01 | 28 | Pending |
| RM-02 | 28 | Pending |
| RM-03 | 28 | Pending |
| RM-04 | 28 | Pending |
| RM-05 | 28 | Pending |
| MV-01 | 28 | Pending |
| MV-02 | 28 | Pending |
| MV-03 | 28 | Pending |
| MV-04 | 28 | Pending |
| CLEN-01 | 28 | Pending |
| CLEN-02 | 28 | Pending |
| CLEN-03 | 28 | Pending |
| CLEN-04 | 28 | Pending |
| CONF-01 | 28 | Pending |
| CONF-02 | 28 | Pending |
| CONF-03 | 28 | Pending |
| CONF-04 | 28 | Pending |
| CONF-05 | 28 | Pending |
| CONF-06 | 28 | Pending |
| CONF-07 | 28 | Pending |
| CONF-08 | 28 | Pending |
| DOC-01 | 29 | Pending |
| DOC-02 | 29 | Pending |
| DOC-03 | 29 | Pending |
| DOC-04 | 29 | Pending |
| DOC-05 | 29 | Pending |

**Coverage:**
- v1.3 requirements: 111 total
- Mapped to phases: 111
- Unmapped: 0

---
*Requirements defined: 2026-01-20*
*Last updated: 2026-01-20 after roadmap creation*
