# Flag Compatibility Gaps

**Researched:** 2026-01-20
**Confidence:** MEDIUM (based on official documentation for both git and Sapling)

## Summary

GitSL translates 25 git commands to Sapling equivalents. Flag compatibility falls into distinct categories with varying risk levels:

| Category | Count | Risk | Action Required |
|----------|-------|------|-----------------|
| Semantic Differences | 8 | HIGH | Must emulate or block |
| Flag Translation | 12 | LOW | Simple name mapping |
| Git-Only (No Equivalent) | 25+ | MEDIUM | Emulate, warn, or document |
| Pass-Through Compatible | 50+ | NONE | Direct pass-through |
| Output Format Differences | 6 | MEDIUM | Transform output or document |

**Critical finding:** Several flags have identical names but different behavior between git and sl. These are the highest-risk gaps that could cause unexpected behavior if passed through naively.

---

## Semantic Differences (High Risk)

Flags that exist in both git and sl but behave differently. These require explicit handling.

| Command | Flag | Git Behavior | sl Behavior | Risk | Mitigation |
|---------|------|--------------|-------------|------|------------|
| `branch` | `-D` | Force delete branch label only | Delete label AND strip commits (destructive!) | **CRITICAL** | Already handled: translate -D to -d |
| `log` | `-n N` | Limit to N commits | Does not exist (use `-l N`) | HIGH | Already handled: translate to -l |
| `status` | `--porcelain` | Machine-readable 2-char XY format | Does not exist | HIGH | Already handled: parse and transform output |
| `status` | `--short`/`-s` | Same as porcelain | Does not exist | HIGH | Already handled: transform output |
| `add` | `-A`/`--all` | Stage all (new, modified, deleted) | Does not exist | MEDIUM | Already handled: translate to `addremove` |
| `add` | `-u`/`--update` | Stage modified/deleted tracked files only | Does not exist | MEDIUM | Already handled: find deleted and mark for removal |
| `checkout` | (no flag) | Multi-purpose: switch/restore | Does not exist | HIGH | Already handled: disambiguate to goto/revert |
| `commit` | `-a`/`--all` | Auto-stage modified/deleted before commit | `-A` in sl means addremove (includes untracked) | **HIGH** | Needs handling: sl has no staging, different semantics |

### Critical: git commit -a vs sl commit -A

**Git behavior:** `git commit -a` stages modified and deleted tracked files, then commits. Does NOT add untracked files.

**sl behavior:** `sl commit -A` runs addremove (adds untracked AND removes missing) before commit. This ADDS UNTRACKED FILES which git -a would NOT do.

**Risk:** If user runs `git commit -a` expecting only tracked changes to be committed, but we pass -A to sl, untracked files will be added unexpectedly.

**Mitigation options:**
1. Block with error message explaining difference
2. Emulate by checking for untracked files first
3. Translate to `sl commit` without flag (sl commits all pending changes anyway)

**Recommended:** Option 3 - Since Sapling has no staging area, all tracked modified files are already "staged" for commit. Simply remove the -a flag and let sl commit work as intended.

---

## Flag Translation (Low Risk)

Flags with different names but equivalent semantics. Simple translation required.

| Command | Git Flag | sl Flag | Notes |
|---------|----------|---------|-------|
| `log` | `-n N`, `-N` | `-l N` | Already handled |
| `log` | `--max-count=N` | `-l N` | Already handled |
| `clean` | `-f`/`--force` | (implicit) | sl purge requires no force flag |
| `clean` | `-n`/`--dry-run` | `--print` | Already handled |
| `clean` | `-d` | `--files --dirs` | Already handled |
| `config` | `--list`/`-l` | (no args) | Already handled |
| `stash drop` | (no args = recent) | Requires name | Already handled: lookup most recent |
| `stash apply` | (default) | `--keep` | Already handled |
| `checkout -b` | Create branch and switch | `bookmark` + `goto` | Already handled |
| `rm` | `-r`/`--recursive` | (implicit) | sl remove is recursive by default |
| `switch -c` | Create branch | `bookmark` | Already handled |
| `diff` | `--cached` | (see note) | sl has no staging; use `--rev` for comparison |

---

## Git-Only Flags (Needs Emulation or Documentation)

Flags that git supports but sl has no equivalent for. Organized by command.

### status

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `--porcelain=v2` | Version 2 format | Parse sl output, format v2 | LOW (v1 sufficient for most tools) |
| `-b`/`--branch` | Show branch info | Add branch info to output | MEDIUM |
| `--untracked-files=no` | Hide untracked | Filter output | LOW |
| `--ignored` | Show ignored files | sl status -i | HIGH (direct translation) |
| `-z` | NUL-terminated | Transform output | LOW |
| `--ahead-behind` | Show ahead/behind counts | Not applicable (different model) | N/A |

### log

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `--pretty=<format>` | Custom format | Map to sl -T template | MEDIUM |
| `--format=<format>` | Same as --pretty | Map to sl -T template | MEDIUM |
| `--graph` | Show ASCII graph | sl log -G (direct) | HIGH |
| `--decorate` | Show refs | sl log with template | MEDIUM |
| `--abbrev-commit` | Short hash | sl uses short by default | NONE |
| `--author=<pattern>` | Filter by author | sl log -u | HIGH (direct) |
| `--since`/`--after` | Date filter | sl log -d | HIGH (needs format translation) |
| `--until`/`--before` | Date filter | sl log -d | HIGH (needs format translation) |
| `--grep=<pattern>` | Filter by message | sl log -k | HIGH (direct) |
| `--all` | All branches | sl log --all | HIGH (direct) |
| `--no-merges` | Hide merges | sl log -M | HIGH (direct) |
| `-p`/`--patch` | Show diffs | sl log -p | HIGH (direct) |
| `--stat` | Show diffstat | sl log --stat | HIGH (direct) |
| `--name-only` | Show filenames only | Transform output | MEDIUM |
| `--name-status` | Show status + names | Transform output | MEDIUM |
| `--follow` | Follow renames | sl log -f | HIGH (direct) |

### diff

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `--staged`/`--cached` | Staged changes | N/A - sl has no staging | N/A (document) |
| `--stat` | Show diffstat | sl diff --stat | HIGH (direct) |
| `-U<n>`/`--unified=<n>` | Context lines | sl diff -U | HIGH (direct) |
| `-w`/`--ignore-all-space` | Ignore whitespace | sl diff -w | HIGH (direct) |
| `-b`/`--ignore-space-change` | Ignore space changes | sl diff -b | HIGH (direct) |
| `--name-only` | Filenames only | Transform output or use sl status | MEDIUM |
| `--name-status` | Status + filenames | Transform output | MEDIUM |
| `--color` | Colored output | sl uses color by default | LOW |
| `-M`/`--find-renames` | Detect renames | sl has rename tracking built-in | LOW |
| `--diff-filter` | Filter by status | No equivalent | LOW |

### commit

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-m <msg>` | Message | sl commit -m | HIGH (direct) |
| `-a`/`--all` | Auto-stage | See semantic differences section | HIGH |
| `--amend` | Amend last commit | sl amend | HIGH (different command) |
| `--no-edit` | Skip editor | sl amend (uses existing message) | MEDIUM |
| `--allow-empty` | Empty commit | sl commit --config ui.allowemptycommit=true | LOW |
| `-F <file>` | Message from file | sl commit -l | HIGH (direct) |
| `--author` | Override author | sl commit -u | MEDIUM |
| `--date` | Override date | sl commit -d | MEDIUM |
| `-v`/`--verbose` | Show diff in editor | sl commit (shows by default) | LOW |
| `--dry-run` | Show what would commit | No direct equivalent | LOW |
| `-n`/`--no-verify` | Skip hooks | sl commit --config hooks.pre-commit= | LOW |
| `--fixup`/`--squash` | For autosquash | No equivalent (use sl fold) | LOW |

### checkout

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-b <name>` | Create branch | sl bookmark + goto | Already handled |
| `-B <name>` | Force create | sl bookmark (updates existing) | Already handled |
| `-f`/`--force` | Force switch | sl goto -C | HIGH |
| `--detach` | Detached HEAD | sl goto (sl doesn't have "attached" concept) | N/A |
| `--orphan` | New root commit | Not commonly needed | LOW |
| `--ours`/`--theirs` | Conflict resolution | sl revert --no-backup | MEDIUM |
| `-m`/`--merge` | Merge local changes | sl goto -m | MEDIUM |

### stash

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-u`/`--include-untracked` | Include untracked | sl shelve -u | HIGH (direct) |
| `-a`/`--all` | Include ignored | sl shelve (need to verify) | LOW |
| `-k`/`--keep-index` | Keep staged | N/A - sl has no staging | N/A |
| `-S`/`--staged` | Stash staged only | N/A - sl has no staging | N/A |
| `--index` (pop/apply) | Restore index | N/A - sl has no staging | N/A |
| `-p`/`--patch` | Interactive | sl shelve -i | MEDIUM |
| `stash@{n}` | Reference by index | Translate to shelve name | MEDIUM |

### branch

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-d <name>` | Delete | sl bookmark -d | Already handled |
| `-D <name>` | Force delete | sl bookmark -d (NOT -D!) | Already handled |
| `-a`/`--all` | List all | sl bookmark -a | MEDIUM |
| `-r`/`--remotes` | List remotes | sl bookmark --remote | MEDIUM |
| `-m <old> <new>` | Rename | sl bookmark -m | HIGH (direct) |
| `-c <old> <new>` | Copy | No direct equivalent | LOW |
| `-v`/`--verbose` | Show commit info | Transform output | LOW |
| `--list` | List matching | sl bookmark | LOW |
| `--contains` | Filter by commit | No direct equivalent | LOW |
| `--merged`/`--no-merged` | Filter by merge status | No direct equivalent | LOW |

### restore

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `--staged`/`-S` | Unstage | N/A - sl has no staging | N/A (warn user) |
| `--worktree`/`-W` | Restore working tree | sl revert (default) | LOW |
| `--source=<tree>` | From specific commit | sl revert -r | HIGH |
| `--ours`/`--theirs` | Conflict resolution | sl revert with specific handling | MEDIUM |
| `-p`/`--patch` | Interactive | sl revert --interactive | MEDIUM |

### clean

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-x` | Remove ignored too | sl purge --all | MEDIUM |
| `-X` | Remove ONLY ignored | Filter output | LOW |
| `-e <pattern>` | Exclude pattern | sl purge -X | MEDIUM |

### grep

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-n` | Line numbers | sl grep -n | HIGH (direct) |
| `-i` | Case insensitive | sl grep -i | HIGH (direct) |
| `-l` | Files only | sl grep -l | HIGH (direct) |
| `-c` | Count | sl grep -c | HIGH (direct) |
| `-v` | Invert match | sl grep --invert-match | MEDIUM |
| `-w` | Word match | sl grep -w | MEDIUM |
| `-E` | Extended regex | sl grep uses Rust regex | LOW |
| `-P` | Perl regex | Not supported | LOW |
| `--cached` | Search staged | N/A - sl has no staging | N/A |

### show

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `--stat` | Show diffstat | sl show --stat | HIGH (direct) |
| `--name-only` | Filenames only | Transform output | MEDIUM |
| `--name-status` | Status + filenames | Transform output | MEDIUM |
| `-U<n>` | Context lines | sl show -U | HIGH (direct) |
| `--format` | Output format | sl show -T | MEDIUM |

### blame (annotate)

| Flag | Description | Emulation Strategy | Priority |
|------|-------------|-------------------|----------|
| `-w` | Ignore whitespace | sl annotate -w | HIGH (direct) |
| `-b` | Ignore space changes | sl annotate -b | HIGH (direct) |
| `-L <start>,<end>` | Line range | Not directly supported | MEDIUM |
| `--porcelain` | Machine format | Transform output | LOW |
| `--show-email`/`-e` | Show email | sl annotate -u -v | LOW |

---

## Output Format Differences

Commands where output differs between git and sl, potentially breaking tool parsing.

| Command | Difference | Impact | Strategy |
|---------|------------|--------|----------|
| `status` | Single char vs XY format | HIGH - tools parse this | Already emulated for --porcelain |
| `log --oneline` | Hash length (git: 7, sl: 12) | MEDIUM - some tools may expect 7 | Document; semantic match acceptable |
| `blame` | Line format differs | LOW - rarely parsed | Pass-through acceptable |
| `diff` | Output generally compatible | LOW | Pass-through |
| `branch` | Bookmark vs branch terminology | LOW | Pass-through |
| `stash list` | Different format | MEDIUM | Consider formatting |

### Status Format Details

| Status | git Porcelain | sl Native | gitsl Emulation |
|--------|--------------|-----------|-----------------|
| Modified | ` M` (space + M) | `M` | Emulated |
| Added | `A ` (A + space) | `A` | Emulated |
| Deleted (staged) | `D ` | `R` (removed) | Emulated |
| Missing (untracked delete) | ` D` | `!` | Emulated |
| Untracked | `??` | `?` | Emulated |
| Ignored | `!!` | `I` | Needs implementation |

---

## Pitfalls

### 1. Staging Area Assumption

**What goes wrong:** Git commands that reference staging (--staged, --cached, -a) have no direct equivalent in Sapling.

**Why it happens:** Sapling eliminates the staging area entirely. All tracked modified files are implicitly "staged."

**Detection:** Look for flags: `--staged`, `--cached`, `-a`, `--index`, `-S` (restore)

**Prevention:**
- For `--cached`/`--staged` in diff: warn that sl has no staging, show all changes
- For `-a` in commit: remove flag (sl commits all changes anyway)
- For `--staged` in restore: warn that sl has no staging, suggest alternative
- For `--index` in stash: ignore or warn

### 2. Branch -D Destruction

**What goes wrong:** sl bookmark -D strips commits, git branch -D only removes label.

**Why it happens:** Different semantics inherited from Mercurial.

**Detection:** Already handled in code

**Prevention:** Always translate -D to -d

### 3. Stash Reference Format

**What goes wrong:** Git uses `stash@{0}`, `stash@{1}`, etc. sl uses named shelves.

**Why it happens:** Different stash models.

**Detection:** Arguments matching `stash@{\d+}` pattern

**Prevention:** Map to most recent shelve names (need to implement lookup)

### 4. Commit -a Adding Untracked Files

**What goes wrong:** If we naively pass -a as -A to sl, untracked files get added.

**Why it happens:** Different semantics: git -a = stage modified tracked, sl -A = addremove

**Detection:** Check for -a flag in commit

**Prevention:** Remove -a flag (sl commits all tracked changes without it)

### 5. Date Format Differences

**What goes wrong:** git log --since/--until uses different date format than sl log -d

**Why it happens:** Different date parsing implementations

**Detection:** Presence of --since, --until, --after, --before flags

**Prevention:** Transform date format or document limitation

### 6. Interactive Flags

**What goes wrong:** Interactive flags (-i, -p for patch selection) may behave differently.

**Why it happens:** Different TUI implementations

**Detection:** Presence of -i, -p, --interactive, --patch (for selection)

**Prevention:** Pass through and let sl handle, or warn about potential differences

---

## Prioritization

### Phase 1: Critical Safety (Must Complete First)
1. `commit -a` handling (prevent unexpected file adds)
2. Verify branch -D translation coverage
3. Document staging-related limitations

### Phase 2: High-Impact Emulation
1. `log --graph` pass-through (sl log -G)
2. `log --author`, `--since`, `--until` translation
3. `log --stat`, `--patch` pass-through
4. `checkout -f` / `goto -C` translation
5. `stash -u` / `shelve -u` pass-through
6. `status --ignored` pass-through

### Phase 3: Medium-Impact Improvements
1. `restore --source` translation
2. `branch -a`, `-r`, `-m` translations
3. `log --pretty` / `--format` template mapping
4. Stash reference format translation (`stash@{n}`)
5. `grep` additional flags

### Phase 4: Low-Impact / Documentation Only
1. Document staging-related flags as unsupported
2. `--porcelain=v2` format
3. Interactive mode differences
4. Edge case flags with no equivalent

---

## Recommendations for v1.3 Milestone

### Must Have
- [ ] Fix `commit -a` to not use sl -A (remove flag instead)
- [ ] Add `checkout -f` / `--force` translation to `goto -C`
- [ ] Add `status --ignored` translation to sl status -i
- [ ] Verify all pass-through flags actually work in sl

### Should Have
- [ ] Add `log --graph` translation (-G)
- [ ] Add `log --author` translation (-u)
- [ ] Add `stash -u` translation (--include-untracked)
- [ ] Add `branch -m` translation (rename)
- [ ] Add `restore --source` translation (-r)

### Nice to Have
- [ ] Stash reference format translation
- [ ] Log date filtering translation
- [ ] Log format/pretty template mapping

### Document as Unsupported
- [ ] All `--staged`/`--cached` flags (explain no staging area)
- [ ] `--index` flag on stash pop/apply
- [ ] `commit --fixup`/`--squash` (different workflow)
- [ ] Interactive rebase (not translatable)

---

## Sources

- [Sapling Differences from Git](https://sapling-scm.com/docs/introduction/differences-git)
- [Sapling Basic Commands](https://sapling-scm.com/docs/overview/basic-commands/)
- [Sapling status command](https://sapling-scm.com/docs/commands/status/)
- [Sapling annotate command](https://sapling-scm.com/docs/commands/annotate/)
- [Sapling log command](https://sapling-scm.com/docs/commands/log/)
- [Sapling diff command](https://sapling-scm.com/docs/commands/diff/)
- [Sapling commit command](https://sapling-scm.com/docs/commands/commit/)
- [Sapling shelve command](https://sapling-scm.com/docs/commands/shelve/)
- [Sapling goto command](https://sapling-scm.com/docs/commands/goto/)
- [Sapling bookmark command](https://sapling-scm.com/docs/commands/bookmark/)
- [git log documentation](https://git-scm.com/docs/git-log)
- [git status documentation](https://git-scm.com/docs/git-status)
- [git diff documentation](https://git-scm.com/docs/git-diff)
- [git commit documentation](https://git-scm.com/docs/git-commit)
- [git stash documentation](https://git-scm.com/docs/git-stash)
- [git restore documentation](https://git-scm.com/docs/git-restore)
