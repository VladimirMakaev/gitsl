# Sapling Command Flags with Git Mapping

**Researched:** 2026-01-20
**Confidence:** HIGH (verified via `sl help <command> --verbose` locally)
**Commands covered:** 18 commands mapped to their git equivalents

## Summary

This document provides comprehensive flag mappings between Sapling (sl) commands and their Git equivalents. For each command pair, it lists:
- All sl flags with their git equivalents (where they exist)
- sl-specific flags with no git equivalent
- git flags with no sl equivalent (requiring emulation or being unsupported)

---

## 1. sl status -> git status

### sl status Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--all` | `-A` | show status of all files | (implicit behavior) |
| `--modified` | `-m` | show only modified files | (no direct flag, use `--porcelain` + filter) |
| `--added` | `-a` | show only added files | (no direct flag) |
| `--removed` | `-r` | show only removed files | (no direct flag) |
| `--deleted` | `-d` | show only deleted (but tracked) files | (no direct flag) |
| `--clean` | `-c` | show only files without changes | (no direct flag) |
| `--unknown` | `-u` | show only unknown (not tracked) files | `-u` / `--untracked-files` |
| `--ignored` | `-i` | show only ignored files | `--ignored` |
| `--no-status` | `-n` | hide status prefix | (no direct flag) |
| `--copies` | `-C` | show source of copied files | (no direct flag) |
| `--print0` | `-0` | NUL-terminate filenames | `-z` |
| `--rev` | | show differences from revision | (no direct equivalent) |
| `--change` | | list changed files of a revision | (no direct equivalent) |
| `--root-relative` | | status relative to repo root | (git default behavior) |
| `--terse` | `-t` | abbreviate output by directory | (no git equivalent) |
| `--include` | `-I` | include files matching patterns | (pathspec, not flag) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec, not flag) |
| `--template` | `-T` | display with template | (no git equivalent) |

### Git status Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--porcelain` | machine-readable output | Transform sl output to git XY format |
| `--short` / `-s` | short format output | Same as --porcelain |
| `--branch` / `-b` | show branch info | Use `sl whereami` or `sl bookmark` separately |
| `--untracked-files[=mode]` | control untracked display | `-u` partial match, modes not supported |
| `--show-stash` | show stash count | Use `sl shelve --list` separately |
| `--ahead-behind` | show ahead/behind counts | Not available in sl |
| `--long` | default long format | sl default differs from git |

---

## 2. sl add -> git add

### sl add Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |
| `--dry-run` | `-n` | don't perform, just print | `--dry-run` / `-n` |

### Git add Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-A` / `--all` | add all files (new + modified + deleted) | Use `sl addremove` |
| `-u` / `--update` | update tracked files only | Use `sl remove --mark` for deleted files |
| `-p` / `--patch` | interactive partial staging | `sl commit -i` (at commit time) |
| `-i` / `--interactive` | interactive mode | `sl commit -i` (at commit time) |
| `-f` / `--force` | add ignored files | Not supported |
| `-e` / `--edit` | edit diff before adding | Not supported |
| `--chmod=` | override executable bit | Not supported |
| `-v` / `--verbose` | verbose output | Global `-v` flag |

**Key Difference:** sl has no staging area. `sl add` marks files for tracking, not staging.

---

## 3. sl commit -> git commit

### sl commit Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--addremove` | `-A` | mark new/missing files before commit | `-a` (partial - only tracked) |
| `--edit` | `-e` | invoke editor on commit message | (git default behavior) |
| `--interactive` | `-i` | use interactive mode | `-p` / `--patch` (similar) |
| `--reuse-message` | `-M` | reuse commit message from REV | `-C` / `--reuse-message` |
| `--no-move-detection` | | disable file move detection | (git doesn't auto-detect) |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |
| `--message` | `-m` | use text as commit message | `-m` / `--message` |
| `--logfile` | `-l` | read message from file | `-F` / `--file` |
| `--date` | `-d` | record specified date | `--date` |
| `--user` | `-u` | record specified user as committer | `--author` |

### Git commit Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-a` / `--all` | commit all tracked modified files | Use `sl commit` (sl auto-includes modified) |
| `--amend` | amend previous commit | Use `sl amend` instead |
| `--no-edit` | use selected commit message without edit | `sl amend --no-edit` for amend |
| `-c` / `-C` | reuse message from commit | `-M` / `--reuse-message` |
| `--allow-empty` | allow empty commit | Not directly supported |
| `--allow-empty-message` | allow empty message | Not supported |
| `-s` / `--signoff` | add Signed-off-by | Not supported |
| `--no-verify` | skip pre-commit hooks | Not directly supported |
| `-v` / `--verbose` | show diff in commit message template | Global `-v` |

**Key Difference:** sl has no staging area, so `-a` behavior is implicit.

---

## 4. sl log -> git log

### sl log Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--follow` | `-f` | follow file history across copies/renames | `--follow` |
| `--date` | `-d` | show revisions matching date spec | `--since` / `--until` (similar) |
| `--copies` | `-C` | show copied files | `-C` |
| `--keyword` | `-k` | case-insensitive search in commit content | `--grep` (case-insensitive with `-i`) |
| `--rev` | `-r` | show specified revision or revset | (revision argument) |
| `--removed` | | include revisions where files were removed | (git default behavior) |
| `--user` | `-u` | revisions committed by user | `--author` |
| `--prune` | `-P` | do not display revision or ancestors | (no direct equivalent) |
| `--patch` | `-p` | show patch | `-p` / `--patch` |
| `--git` | `-g` | use git extended diff format | (git default) |
| `--limit` | `-l` | limit number of changes | `-n` / `--max-count` |
| `--no-merges` | `-M` | do not show merges | `--no-merges` |
| `--stat` | | output diffstat-style summary | `--stat` |
| `--graph` | `-G` | show revision DAG | `--graph` |
| `--template` | `-T` | display with template | `--format` / `--pretty` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |
| `--all` | | show all changesets | `--all` |
| `--branch` | `-b` | show changesets in branch (DEPRECATED) | `--branches` |
| `--line-range` | `-L` | follow line range history | `-L` |

### Git log Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--oneline` | one-line format | Use `-T "{node|short} {desc|firstline}\n"` |
| `--decorate` | show branch/tag names | Use `--template` with bookmark info |
| `--abbrev-commit` | short commit hashes | Use `--template` with `{node|short}` |
| `--first-parent` | follow only first parent | Not directly available |
| `--ancestry-path` | show commits in ancestry path | Use revset expressions |
| `--date-order` / `--topo-order` | ordering options | sl has own ordering |
| `--reverse` | reverse output order | Not directly available |

---

## 5. sl diff -> git diff

### sl diff Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--rev` | `-r` | revision(s) to compare | (revision arguments) |
| `--change` | `-c` | show changes made by revision | (use `commit^..commit`) |
| `--text` | `-a` | treat all files as text | `-a` / `--text` |
| `--git` | `-g` | use git extended diff format | (git default) |
| `--binary` | | generate binary diffs | `--binary` |
| `--nodates` | | omit dates from diff headers | (no direct equivalent) |
| `--noprefix` | | remove a/ b/ prefixes | `--no-prefix` |
| `--show-function` | `-p` | show function for each change | `-p` / `--show-function` |
| `--reverse` | | produce diff that undoes changes | `-R` |
| `--ignore-all-space` | `-w` | ignore whitespace | `-w` |
| `--ignore-space-change` | `-b` | ignore whitespace amount changes | `-b` |
| `--ignore-blank-lines` | `-B` | ignore blank line changes | `--ignore-blank-lines` |
| `--ignore-space-at-eol` | `-Z` | ignore trailing whitespace | `--ignore-space-at-eol` |
| `--unified` | `-U` | lines of context | `-U<n>` / `--unified=<n>` |
| `--stat` | | show diffstat summary | `--stat` |
| `--root` | | diffs relative to subdirectory | (no direct equivalent) |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### Git diff Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--staged` / `--cached` | diff staged changes | **Not applicable** - sl has no staging area |
| `--name-only` | show only file names | Use `sl status --rev REV` |
| `--name-status` | show file names with status | Use `sl status --rev REV` |
| `--numstat` | machine-readable stat | Not available |
| `--shortstat` | only summary line | Not available |
| `--word-diff` | word-level diff | Not available |
| `--color-words` | word diff with colors | Not available |
| `--check` | warn if changes introduce errors | Not available |

---

## 6. sl init -> git init

### sl init Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--git` | | use git as backend (EXPERIMENTAL) | (inherent to git) |

### Git init Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--bare` | create bare repository | Not directly supported |
| `--template=` | use template directory | Not supported |
| `-b` / `--initial-branch` | specify initial branch name | Not supported |
| `--shared` | set group permissions | Not supported |
| `--separate-git-dir` | separate .git directory | Not supported |

---

## 7. sl show -> git show

### sl show Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--nodates` | | omit dates from diff headers | (no direct equivalent) |
| `--noprefix` | | remove a/ b/ prefixes | `--no-prefix` |
| `--stat` | | output diffstat summary | `--stat` |
| `--git` | `-g` | use git extended diff format | (git default) |
| `--unified` | `-U` | lines of context | `-U<n>` |
| `--ignore-all-space` | `-w` | ignore whitespace | `-w` |
| `--ignore-space-change` | `-b` | ignore whitespace changes | `-b` |
| `--ignore-blank-lines` | `-B` | ignore blank line changes | `--ignore-blank-lines` |
| `--ignore-space-at-eol` | `-Z` | ignore trailing whitespace | `--ignore-space-at-eol` |
| `--template` | `-T` | display with template | `--format` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### Git show Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--name-only` | show only file names | Use template or status |
| `--name-status` | show file names with status | Use template or status |
| `-s` | suppress diff output | Use template with no diff |
| `--format=` / `--pretty=` | output format | Use `--template` |
| `--abbrev-commit` | short commit hash | Use template |
| `--oneline` | one line per commit | Use template |

---

## 8. sl annotate -> git blame

### sl annotate Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--rev` | `-r` | annotate specified revision | `<rev>` argument |
| `--no-follow` | | don't follow copies/renames | (git default) |
| `--text` | `-a` | treat all files as text | (git default) |
| `--user` | `-u` | list the author | `-e` / `--show-email` (partial) |
| `--file` | `-f` | list the filename | (git default) |
| `--date` | `-d` | list the date | (git default) |
| `--number` | `-n` | list revision number | (no direct equivalent) |
| `--changeset` | `-c` | list the changeset (default) | (git default shows hash) |
| `--line-number` | `-l` | show line number at first appearance | `-n` |
| `--ignore-all-space` | `-w` | ignore whitespace | `-w` |
| `--ignore-space-change` | `-b` | ignore whitespace changes | `--ignore-space-change` |
| `--ignore-blank-lines` | `-B` | ignore blank line changes | `--ignore-blank-lines` |
| `--ignore-space-at-eol` | `-Z` | ignore trailing whitespace | (no direct equivalent) |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### Git blame Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-L <start>,<end>` | blame only line range | Not directly available |
| `-M` | detect moved lines within file | Not available |
| `-C` | detect copied lines | sl `--no-follow` inverse |
| `--porcelain` | machine-readable output | Use template |
| `-s` | suppress author name and time | Use template |
| `--show-name` | show filename | `-f` |

---

## 9. sl remove -> git rm

### sl remove Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--mark` | | mark deletion for missing files | (no direct equivalent) |
| `--after` | `-A` | alias to --mark (DEPRECATED) | (no direct equivalent) |
| `--force` | `-f` | forget added files, delete modified | `-f` / `--force` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### Git rm Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-r` / `--recursive` | recursive removal | sl remove is recursive by default |
| `--cached` | remove from index only | Use `sl forget` |
| `-n` / `--dry-run` | dry run | Not available for remove |
| `--ignore-unmatch` | exit success even if no match | Not available |
| `-q` / `--quiet` | suppress output | Global `-q` |

---

## 10. sl rename/move -> git mv

### sl rename Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--mark` | | mark rename without copying | (no direct equivalent) |
| `--amend` | | amend current commit to mark rename | (no direct equivalent) |
| `--force` | `-f` | forcibly copy over existing file | `-f` / `--force` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |
| `--dry-run` | `-n` | don't perform, just print | `-n` / `--dry-run` |

### Git mv Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-k` | skip errors | Not available |
| `-v` / `--verbose` | verbose output | Global `-v` |

---

## 11. sl clean/purge -> git clean

### sl clean Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--abort-on-err` | `-a` | abort if error occurs | (git default behavior) |
| `--ignored` | | delete ignored files too | `-x` |
| `--dirs` | | delete empty directories | `-d` |
| `--files` | | delete files (default) | (git default) |
| `--print` | `-p` | print filenames instead of deleting | `-n` / `--dry-run` |
| `--print0` | `-0` | NUL-terminate filenames | (no direct equivalent) |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | `-e` / `--exclude` |

### Git clean Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-f` / `--force` | required to actually clean | Not required by sl (dangerous!) |
| `-i` / `--interactive` | interactive mode | Not available |
| `-X` | remove only ignored files | Use `--ignored` without `--files` |
| `-e <pattern>` | exclude pattern | Use `-X` / `--exclude` |
| `-q` / `--quiet` | quiet mode | Global `-q` |

**Safety Note:** git requires `-f` to clean. sl cleans immediately without confirmation.

---

## 12. sl clone -> git clone

### sl clone Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--noupdate` | `-U` | clone without checkout | `--no-checkout` / `-n` |
| `--updaterev` | `-u` | revision to check out | `-b` / `--branch` (partial) |
| `--git` | | use git protocol | (inherent to git) |
| `--enable-profile` | | enable sparse profile | (no direct equivalent) |

### Git clone Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--depth=<n>` | shallow clone | Not supported |
| `--single-branch` | clone single branch | Not supported |
| `--mirror` | mirror clone | Not supported |
| `--bare` | bare clone | Not supported |
| `--recurse-submodules` | include submodules | Not supported |
| `-o` / `--origin` | set remote name | Not supported |
| `--template=` | template directory | Not supported |

---

## 13. sl grep -> git grep

### sl grep Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--after-context` | `-A` | print N lines after match | `-A` |
| `--before-context` | `-B` | print N lines before match | `-B` |
| `--context` | `-C` | print N lines of context | `-C` |
| `--ignore-case` | `-i` | case-insensitive | `-i` |
| `--files-with-matches` | `-l` | print only filenames | `-l` / `--files-with-matches` |
| `--line-number` | `-n` | print line numbers | `-n` |
| `--invert-match` | `-V` | select non-matching lines | `-v` / `--invert-match` |
| `--word-regexp` | `-w` | match whole words | `-w` |
| `--extended-regexp` | `-E` | use POSIX extended regex | `-E` |
| `--fixed-strings` | `-F` | interpret pattern as fixed string | `-F` |
| `--perl-regexp` | `-P` | use Perl-compatible regex | `-P` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### Git grep Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-c` / `--count` | show count per file | Not available |
| `-h` / `--no-filename` | suppress filenames | Not available |
| `-H` / `--with-filename` | show filenames (default) | Default behavior |
| `--heading` | group matches by file | Not available |
| `--break` | empty line between files | Not available |
| `-e <pattern>` | specify pattern | Positional argument |
| `--and` / `--or` / `--not` | boolean operators | Not available |
| `--all-match` | require all patterns match | Not available |
| `-W` / `--function-context` | show full function | Not available |

**Note:** sl grep searches working directory. git grep can search specific commits with revision arguments.

---

## 14. sl config -> git config

### sl config Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--user` | `-u` | edit user config | `--global` |
| `--local` | `-l` | edit repository config | `--local` |
| `--system` | `-s` | edit system config | `--system` |
| `--delete` | `-d` | delete config items | `--unset` |

### Git config Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--list` / `-l` | list all config | `sl config` with no args |
| `--get` | get a value | `sl config section.name` |
| `--get-all` | get all values for key | Not available |
| `--get-regexp` | get values matching pattern | Not available |
| `--add` | add new value | Not available |
| `--unset-all` | unset all matching values | Not available |
| `-e` / `--edit` | open editor | sl opens editor when no args |
| `--show-origin` | show config file path | `--debug` shows source |
| `--type=` | ensure value type | Not available |

**Key Difference:** git `--global` = sl `--user`

---

## 15. sl shelve/unshelve -> git stash

### sl shelve Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--addremove` | `-A` | mark new/missing files before shelve | (partial - stash includes tracked) |
| `--unknown` | `-u` | store unknown files | `-u` / `--include-untracked` |
| `--cleanup` | | delete all shelved changes | `git stash clear` |
| `--date` | | shelve with specified date | (no equivalent) |
| `--delete` | `-d` | delete named shelve | `git stash drop` |
| `--edit` | `-e` | invoke editor on message | (no direct equivalent) |
| `--list` | `-l` | list current shelves | `git stash list` |
| `--message` | `-m` | use text as shelve message | `-m` |
| `--name` | `-n` | use given name for shelve | (stashes are numbered, not named) |
| `--patch` | `-p` | show patch | `git stash show -p` |
| `--interactive` | `-i` | interactive mode | (no direct equivalent) |
| `--stat` | | output diffstat summary | `git stash show` (default) |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |

### sl unshelve Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--abort` | `-a` | abort incomplete unshelve | (no direct equivalent) |
| `--continue` | `-c` | continue incomplete unshelve | (no direct equivalent) |
| `--keep` | `-k` | keep shelve after unshelving | `git stash apply` (vs pop) |
| `--name` | `-n` | restore shelve with given name | `git stash apply stash@{n}` |
| `--tool` | `-t` | specify merge tool | (no direct equivalent) |

### Git stash Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-a` / `--all` | include ignored files | Not available |
| `-S` / `--staged` | stash only staged changes | **Not applicable** - no staging area |
| `-k` / `--keep-index` | don't stash staged changes | **Not applicable** |
| `-p` / `--patch` | interactive stash selection | `-i` / `--interactive` (similar) |
| `--index` | try to reinstate index | **Not applicable** |

---

## 16. sl goto -> git checkout / git switch

### sl goto Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--clean` | `-C` | discard uncommitted changes | `-f` / `--force` |
| `--check` | `-c` | require clean working copy | (git default for switch) |
| `--merge` | `-m` | merge uncommitted changes | `-m` / `--merge` |
| `--date` | `-d` | tipmost revision matching date | (no direct equivalent) |
| `--rev` | `-r` | revision to go to | (positional argument in git) |
| `--inactive` | | update without activating bookmark | (no direct equivalent) |
| `--continue` | | resume interrupted merge | `git checkout --continue` (similar) |
| `--bookmark` | `-B` | create new bookmark | `-b` (git checkout/switch) |
| `--tool` | `-t` | specify merge tool | (no direct equivalent) |

### Git checkout/switch Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-b <name>` | create and switch to branch | `sl bookmark <name> && sl goto <name>` |
| `-B <name>` | create/reset and switch | Same + force |
| `--track` / `-t` | set up tracking | Not applicable (sl has different model) |
| `--detach` | detach HEAD | Not applicable (sl has different model) |
| `--guess` / `--no-guess` | DWIM for remote branches | Not available |
| `--orphan` | create orphan branch | Not available |
| `--ours` / `--theirs` | resolve conflicts | Use merge tool |

---

## 17. sl revert -> git restore / git checkout -- <file>

### sl revert Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--all` | `-a` | revert all changes | `.` (all files) |
| `--date` | `-d` | tipmost revision matching date | (no direct equivalent) |
| `--rev` | `-r` | revert to specified revision | `-s` / `--source` |
| `--no-backup` | `-C` | do not save backup copies | (git doesn't make backups) |
| `--interactive` | `-i` | interactively select changes | `-p` / `--patch` |
| `--include` | `-I` | include files matching patterns | (pathspec) |
| `--exclude` | `-X` | exclude files matching patterns | (pathspec) |
| `--dry-run` | `-n` | don't perform, just print | (no direct equivalent) |

### Git restore Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `--staged` / `-S` | restore staged content | **Not applicable** - no staging area |
| `--worktree` / `-W` | restore worktree (default) | Default sl behavior |
| `--source=<tree>` | restore from source | `-r` / `--rev` |
| `-m` / `--merge` | recreate conflicted merge | Not available |
| `--conflict=<style>` | conflict style | Not available |
| `--ignore-unmerged` | ignore unmerged entries | Not available |
| `--overlay` / `--no-overlay` | overlay mode | Not available |

---

## 18. sl bookmark -> git branch

### sl bookmark Flags

| sl Flag | Short | Description | Git Equivalent |
|---------|-------|-------------|----------------|
| `--force` | `-f` | force | `-f` / `--force` |
| `--rev` | `-r` | revision for bookmark action | (positional or `-c`) |
| `--delete` | `-d` | delete bookmark | `-d` / `--delete` |
| `--strip` | `-D` | delete bookmark AND strip commits | **DANGEROUS** - git `-D` only deletes label |
| `--rename` | `-m` | rename bookmark | `-m` / `--move` |
| `--inactive` | `-i` | mark bookmark inactive | (no direct equivalent) |
| `--template` | `-T` | display with template | `--format` |
| `--track` | `-t` | track remote bookmark | `-t` / `--track` |
| `--untrack` | `-u` | remove tracking | `--no-track` |
| `--list-remote` | | list remote bookmarks | `-r` / `--remote` |
| `--all` | `-a` | show remote and local | `-a` / `--all` |
| `--remote` | | fetch remote Git refs | `-r` / `--remote` |
| `--remote-path` | | remote path for fetch | (use remote name) |
| `--list-subscriptions` | | show locally available remotes | (no direct equivalent) |

### Git branch Flags with NO sl Equivalent

| git Flag | Description | Emulation Strategy |
|----------|-------------|-------------------|
| `-v` / `--verbose` | show commit with branch | Use template |
| `-vv` | show tracking info | Use template + track info |
| `--list` | list mode (with patterns) | Positional patterns |
| `--contains` | branches containing commit | Not available |
| `--merged` / `--no-merged` | filter by merge status | Not available |
| `--sort=<key>` | sort output | Not available |
| `-u` / `--set-upstream-to` | set upstream | `--track` |
| `--unset-upstream` | remove upstream | `--untrack` |
| `-c` / `--copy` | copy branch | Not available |

**CRITICAL SAFETY:**
- `git branch -D` = force delete label, commits preserved
- `sl bookmark -D` = delete label AND strip commits (DESTRUCTIVE!)
- gitsl must ALWAYS translate `-D` to `-d` to prevent data loss

---

## Flag Compatibility Matrix

### Flags That Pass Through Unchanged

These flags have identical or compatible syntax in both systems:

| Flag | Commands | Notes |
|------|----------|-------|
| `-m <message>` | commit, shelve | Identical |
| `-f` | rm, mv, goto, branch | Identical meaning |
| `-n` (dry-run) | add, mv | Identical |
| `-i` (ignore-case) | grep | Identical |
| `-l` (limit/list) | log, grep, shelve | Similar but different contexts |
| `-p` (patch) | log, show | Identical |
| `-w` (ignore-whitespace) | diff, show, annotate | Identical |
| `-U<n>` (context) | diff, show | Identical |
| `--stat` | diff, log, show | Identical |
| `--graph` | log | Identical |

### Flags Requiring Translation

| git Flag | sl Equivalent | Commands | Translation |
|----------|---------------|----------|-------------|
| `-n <N>` / `--max-count=<N>` | `-l <N>` | log | Number format |
| `--oneline` | `-T "{template}"` | log | Template-based |
| `-A` / `--all` (add) | `addremove` | add | Different command |
| `-u` / `--update` (add) | `remove --mark` | add | Different approach |
| `--porcelain` / `--short` | (emulate) | status | Output transformation |
| `-d` (clean) | `--dirs` | clean | Flag name |
| `-x` (clean) | `--ignored` | clean | Flag name |
| `--global` (config) | `--user` | config | Scope naming |

### Flags With No sl Equivalent (Need Emulation or Skip)

| git Flag | Commands | Emulation | Difficulty |
|----------|----------|-----------|------------|
| `--staged` / `--cached` | diff, restore | **Impossible** - no staging | N/A |
| `--porcelain` | status | Output transformation | Medium |
| `--short` | status | Output transformation | Medium |
| `--branch` | status | Additional command | Easy |
| `--oneline` | log | Template | Easy |
| `--decorate` | log | Template | Medium |
| `--show-toplevel` | rev-parse | `sl root` | Easy |
| `--name-only` | diff, show | Use status | Medium |
| `-L <range>` | blame | Not available | Hard |

---

## Sources

- `sl help <command> --verbose` (local Sapling installation)
- [sapling-scm.com/docs/commands/status](https://sapling-scm.com/docs/commands/status/)
- [sapling-scm.com/docs/commands/commit](https://sapling-scm.com/docs/commands/commit/)
- [sapling-scm.com/docs/commands/log](https://sapling-scm.com/docs/commands/log/)
- [sapling-scm.com/docs/commands/diff](https://sapling-scm.com/docs/commands/diff/)
- [sapling-scm.com/docs/commands/show](https://sapling-scm.com/docs/commands/show/)
- [sapling-scm.com/docs/commands/goto](https://sapling-scm.com/docs/commands/goto/)
- [sapling-scm.com/docs/commands/bookmark](https://sapling-scm.com/docs/commands/bookmark/)
- [sapling-scm.com/docs/commands/annotate](https://sapling-scm.com/docs/commands/annotate/)
- [sapling-scm.com/docs/commands/shelve](https://sapling-scm.com/docs/commands/shelve/)
- [sapling-scm.com/docs/commands/unshelve](https://sapling-scm.com/docs/commands/unshelve/)
- [sapling-scm.com/docs/commands/clean](https://sapling-scm.com/docs/commands/clean/)
- [sapling-scm.com/docs/commands/remove](https://sapling-scm.com/docs/commands/remove/)
- [sapling-scm.com/docs/commands/clone](https://sapling-scm.com/docs/commands/clone/)
- [sapling-scm.com/docs/commands/config](https://sapling-scm.com/docs/commands/config/)
