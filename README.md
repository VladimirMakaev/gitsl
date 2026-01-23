# gitsl

[![CI](https://img.shields.io/github/actions/workflow/status/VladimirMakaev/gitsl/ci.yml?branch=master)](https://github.com/VladimirMakaev/gitsl/actions)
[![PyPI](https://img.shields.io/pypi/v/gitsl)](https://pypi.org/project/gitsl/)
[![Python](https://img.shields.io/pypi/pyversions/gitsl)](https://pypi.org/project/gitsl/)

Git to Sapling CLI shim - translates git commands to their Sapling (sl) equivalents.

## Installation

```bash
pip install gitsl
```

Requires Python 3.8 or later. Requires [Sapling](https://sapling-scm.com/) to be installed and available as `sl`.

## Quick Start

Use familiar git commands in any Sapling repository:

```bash
# Check status (outputs git-compatible format)
gitsl status --porcelain

# View recent commits
gitsl log --oneline -5

# Stage and commit changes
gitsl add -A
gitsl commit -m "Your message"
```

gitsl translates these to equivalent Sapling commands automatically.

## Supported Commands

| Command | Status | Translation |
|---------|--------|-------------|
| `init` | Full | `sl init` |
| `status` | Full | `sl status` with output transformation |
| `log` | Full | `sl log` with flag translation |
| `diff` | Full | `sl diff` |
| `add` | Full | `sl add` / `sl addremove` |
| `commit` | Full | `sl commit` |
| `rev-parse` | Full | Multiple flag support |
| `show` | Full | `sl show` |
| `blame` | Full | `sl annotate` |
| `rm` | Full | `sl remove` |
| `mv` | Full | `sl rename` |
| `clone` | Full | `sl clone` |
| `grep` | Full | `sl grep` |
| `clean` | Full | `sl purge` (requires `-f` or `-n`) |
| `config` | Full | `sl config` |
| `switch` | Full | `sl goto` / `sl bookmark` |
| `branch` | Full | `sl bookmark` |
| `restore` | Full | `sl revert` |
| `stash` | Full | `sl shelve` / `sl unshelve` |
| `checkout` | Full | `sl goto` / `sl revert` / `sl bookmark` |

Commands not listed are unsupported.

## Command Reference

### Staging Area Limitations

Sapling does not have a staging area (index). This affects several git flags:

| Flag | Command | Behavior |
|------|---------|----------|
| `--staged/--cached` | diff | Prints warning (no staging area) |
| `--staged/-S` | restore | Prints warning (no staging area) |
| `--keep-index/-k` | stash | Prints warning (no staging area) |
| `--cached` | rm | Prints warning (no staging area) |
| `-a/--all` | commit | **Removed** (sl -A adds untracked files - safety risk) |

**Sapling workflow:** Edit files directly (no staging step), then commit all changes with `sl commit`. Use `sl shelve` to set aside changes temporarily.

### Common Flag Translations

Quick reference for key flag differences between git and Sapling:

| Git Flag | Sapling Equivalent | Commands | Notes |
|----------|-------------------|----------|-------|
| `--author=` | `-u` | log, commit | |
| `-b <branch>` | `-u <bookmark>` | clone | |
| `-d/--detach` | `--inactive` | switch, checkout | |
| `-f/--force` | `-C` | checkout, switch | For goto paths |
| `--global` | `--user` | config | |
| `--graph` | `-G` | log | |
| `-n` (limit) | `-l` | log | |
| `--unset` | `--delete` | config | |
| `-v` (invert) | `-V` | grep | **Critical: uppercase V** |
| `-b` (blank SHA) | `--ignore-space-change` | blame | **Critical: sl -b differs** |

### git status

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| (none) | Yes | Passthrough to `sl status` |
| `--porcelain` | Yes | Output transformed to git XY format |
| `--short/-s` | Yes | Output transformed to git XY format |
| `--ignored` | Yes | Translates to `-i` |
| `-b/--branch` | Yes | Adds branch info header |
| `-v/--verbose` | Note | sl -v has different meaning |
| `-u/--untracked-files` | Yes | Controls untracked file display |

**Status code translation:**

| Sapling | Git | Meaning |
|---------|-----|---------|
| `M` | ` M` | Modified in working tree |
| `A` | `A ` | Added (staged) |
| `R` | `D ` | Removed (staged deletion) |
| `?` | `??` | Untracked |
| `!` | ` D` | Missing (deleted from disk) |

### git log

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| (none) | Yes | `sl log` |
| `--oneline` | Yes | Uses template output |
| `-n N`/`-N`/`--max-count=N` | Yes | Translates to `-l N` |
| `--graph` | Yes | Translates to `-G` |
| `--stat` | Yes | Passes through |
| `--patch/-p` | Yes | Passes through |
| `--author=<pattern>` | Yes | Translates to `-u <pattern>` |
| `--grep=<pattern>` | Yes | Translates to `-k <pattern>` |
| `--no-merges` | Yes | Passes through |
| `--all` | Yes | Passes through |
| `--follow` | Yes | Translates to `-f` |
| `--since/--after` | Yes | Translates to `-d ">date"` |
| `--until/--before` | Yes | Translates to `-d "<date"` |
| `--name-only` | Yes | Uses template output |
| `--name-status` | Yes | Uses template output |
| `--decorate` | Yes | Uses template with bookmarks |
| `--pretty/--format=` | Yes | Maps to `-T` template |
| `--first-parent` | Yes | Revset approximation |
| `--reverse` | Yes | Revset approximation |
| `-S/-G` (pickaxe) | Warning | No sl equivalent (use `sl grep`) |

### git diff

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| (none) | Yes | `sl diff` |
| `--stat` | Yes | Passes through |
| `-w/--ignore-all-space` | Yes | Passes through |
| `-b/--ignore-space-change` | Yes | Passes through |
| `-U<n>/--unified=<n>` | Yes | Passes through |
| `--name-only` | Yes | Uses `sl status -mard` for working dir |
| `--name-status` | Yes | Uses `sl status -mard` for working dir |
| `--staged/--cached` | Warning | No staging area in Sapling |
| `--raw` | Yes | Passes through |
| `-M/--find-renames` | Yes | Passes through |
| `-C/--find-copies` | Yes | Passes through |
| `--word-diff` | Yes | Passes through |
| `--color-moved` | Warning | Not supported in sl |

### git show

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| (none) | Yes | `sl show` |
| `--stat` | Yes | Passes through |
| `-U<n>` | Yes | Passes through |
| `-w` | Yes | Passes through |
| `--name-only` | Yes | Uses template output |
| `--name-status` | Yes | Uses template output |
| `--pretty/--format=` | Yes | Maps to `-T` template |
| `-s/--no-patch` | Yes | Passes through |
| `--oneline` | Yes | Uses template output |

### git add

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<files>` | Yes | `sl add <files>` |
| `-A/--all` | Yes | `sl addremove` |
| `-u/--update` | Yes | Marks deleted files with `sl remove --mark` |
| `--dry-run/-n` | Yes | Shows what would be added |
| `-f/--force` | Warning | Cannot add ignored files in Sapling |
| `-v/--verbose` | Yes | Passes through |
| `-p/--patch` | No | Not implemented |

### git commit

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `-m <message>` | Yes | Passes through |
| `--amend` | Yes | Translates to `sl amend` |
| `--no-edit` | Yes | Omits `-e` flag (sl amend default) |
| `-F/--file` | Yes | Translates to `-l` (logfile) |
| `--author=` | Yes | Translates to `-u` |
| `--date=` | Yes | Translates to `-d` |
| `-v/--verbose` | Warning | Different semantics in sl |
| `-s/--signoff` | Yes | Adds Signed-off-by trailer |
| `-n/--no-verify` | Warning | Hook bypass not available |
| `-a/--all` | **Removed** | Safety - sl -A adds untracked files |

### git clone

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<url>` | Yes | `sl clone <url>` |
| `-b/--branch <name>` | Yes | `sl clone -u <bookmark>` |
| `-n/--no-checkout` | Yes | `sl clone -U` |
| `--depth` | Warning | Use `--shallow` instead |
| `--single-branch` | Warning | Limited support |
| `-o/--origin` | Warning | Not supported |
| `--recursive/--recurse-submodules` | Warning | Not supported |
| `--no-tags` | Warning | Not supported |
| `-q/--quiet` | Yes | Passes through |
| `-v/--verbose` | Yes | Passes through |

### git grep

**Critical:** git grep `-v` (invert match) translates to sl grep `-V` (uppercase). The lowercase `-v` in Sapling means verbose.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<pattern>` | Yes | `sl grep <pattern>` |
| `-n/--line-number` | Yes | Passes through |
| `-i/--ignore-case` | Yes | Passes through |
| `-l/--files-with-matches` | Yes | Passes through |
| `-w/--word-regexp` | Yes | Passes through |
| `-v/--invert-match` | Yes | Translates to `-V` (**uppercase V**) |
| `-A <num>` | Yes | Passes through |
| `-B <num>` | Yes | Passes through |
| `-C <num>` | Yes | Passes through |
| `-F/--fixed-strings` | Yes | Passes through |
| `-q/--quiet` | Yes | Passes through |
| `-c/--count` | Warning | Not supported |
| `-h` | Warning | Would show help (sl -h) |
| `-H` | No-op | Already default behavior |
| `-o/--only-matching` | Warning | Not supported |

### git blame

Translates to `sl annotate`.

**Critical:** git blame `-b` does NOT pass through directly. Sapling `-b` shows blank SHA1; use `--ignore-space-change` instead.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<file>` | Yes | `sl annotate <file>` |
| `-w` | Yes | Passes through (ignore whitespace) |
| `-b` | Yes | Translates to `--ignore-space-change` (**NOT -b**) |
| `-n/--show-number` | Yes | Passes through |
| `-L <start>,<end>` | Warning | Not supported |
| `-e/--show-email` | Warning | Not supported |
| `-p/--porcelain` | Warning | Not supported |
| `-l` | Warning | **Don't pass through** (sl -l means line number) |

### git rm

Translates to `sl remove`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<files>` | Yes | `sl remove <files>` |
| `-f/--force` | Yes | Passes through |
| `--cached` | Warning | No staging area |
| `-n/--dry-run` | Warning | Not supported |
| `-q/--quiet` | Yes | Suppresses output |
| `-r` | Filtered | sl remove is recursive by default |

### git mv

Translates to `sl rename`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<source> <dest>` | Yes | `sl rename <source> <dest>` |
| `-f/--force` | Yes | Passes through |
| `-k` | Warning | Not supported |
| `-v/--verbose` | Yes | Passes through |
| `-n/--dry-run` | Yes | Passes through |

### git clean

Translates to `sl purge`. **Requires `-f` or `-n` flag** (safety validation).

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `-f` | Yes | `sl purge` |
| `-n/--dry-run` | Yes | `sl purge --print` |
| `-d` | Yes | Included by default in sl purge |
| `-x` | Yes | `sl purge --ignored` (remove ignored too) |
| `-X` | Warning | Use `--ignored` only for ignored files |
| `-e <pattern>` | Yes | Translates to `-X` (exclude pattern) |

### git config

Translates to `sl config`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<key>` | Yes | `sl config <key>` |
| `<key> <value>` | Yes | `sl config --local <key> <value>` |
| `--get` | No-op | Default behavior |
| `--unset` | Yes | Translates to `--delete --local` |
| `--list/-l` | Yes | `sl config` (no key) |
| `--global` | Yes | Translates to `--user` |
| `--local` | Yes | Passes through |
| `--system` | Yes | Passes through |
| `--show-origin` | Yes | Translates to `--debug` |
| `--all` | Warning | Not supported |

### git switch

Modern replacement for branch-switching behavior of `git checkout`. Translates to `sl goto` / `sl bookmark`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<branch>` | Yes | `sl goto <branch>` |
| `-c/--create <name>` | Yes | `sl bookmark <name>` + `sl goto <name>` |
| `-C/--force-create <name>` | Yes | `sl bookmark -f <name>` + `sl goto <name>` |
| `-d/--detach` | Yes | `sl goto --inactive` |
| `-f/--force/--discard-changes` | Yes | `sl goto -C` (discards local changes) |
| `-m/--merge` | Yes | `sl goto -m` (merge local changes) |

### git branch

Translates to `sl bookmark`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| (none) | Yes | `sl bookmark` (list) |
| `<name>` | Yes | `sl bookmark <name>` (create) |
| `-d <name>` | Yes | `sl bookmark -d <name>` |
| `-D <name>` | Yes | `sl bookmark -d` (safety: -D translated to -d) |
| `-m <old> <new>` | Yes | Translates to `-m` |
| `-a/--all` | Yes | Shows all including remote |
| `-r/--remotes` | Yes | Shows remote only |
| `-v/--verbose` | Yes | Uses template for commit info |
| `-l/--list` | Yes | Filters output |
| `--show-current` | Yes | Shows current branch name |
| `-t/--track` | Yes | Passes through |
| `-f/--force` | Yes | Passes through |
| `-c/--copy` | Yes | Two-step (get hash + create) |

### git restore

Modern replacement for file-restoring behavior of `git checkout`. Translates to `sl revert`.

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `<file>` | Yes | `sl revert <file>` |
| `.` | Yes | `sl revert --all` |
| `-s/--source=<tree>` | Yes | `sl revert -r <rev>` |
| `--staged/-S` | Warning | No staging area - prints warning |
| `-q/--quiet` | Yes | Suppresses output |
| `-W/--worktree` | Default | No-op (worktree is default behavior) |

### git stash

Translates to `sl shelve` / `sl unshelve`.

| Subcommand/Flag | Supported | Translation/Notes |
|-----------------|-----------|-------------------|
| (none) | Yes | `sl shelve` |
| `push` | Yes | `sl shelve` |
| `push <pathspec>` | Yes | `sl shelve <pathspec>` (selective file stashing) |
| `-m/--message` | Yes | `sl shelve -m` |
| `-u/--include-untracked` | Yes | `sl shelve -u` |
| `-a/--all` | Yes | `sl shelve -u` (includes ignored with note) |
| `-p/--patch` | Yes | `sl shelve -i` (interactive selection) |
| `-k/--keep-index` | Warning | No staging area - prints warning |
| `-q/--quiet` | Yes | Suppresses output |
| `pop` | Yes | `sl unshelve` |
| `apply` | Yes | `sl unshelve --keep` |
| `list` | Yes | `sl shelve --list` |
| `show` | Yes | `sl shelve --stat` |
| `show --stat` | Yes | Displays diffstat |
| `stash@{n}` | Yes | Maps to shelve name via `sl shelve --list` lookup |
| `drop` | Yes | `sl shelve --delete <name>` |
| `branch <name>` | Yes | Creates bookmark + unshelve |

**Note:** `-p/--patch` translates to `sl shelve -i` for interactive selection. The `stash@{n}` syntax is translated by looking up the nth shelve name from `sl shelve --list`.

### git checkout

Disambiguates between branches, files, and commits. Modern git recommends using `git switch` (for branches) and `git restore` (for files) instead.

| Usage/Flag | Supported | Translation/Notes |
|------------|-----------|-------------------|
| `<branch>` | Yes | `sl goto <branch>` |
| `<commit>` | Yes | `sl goto <commit>` |
| `<file>` | Yes | `sl revert <file>` |
| `-- <file>` | Yes | `sl revert <file>` |
| `-b <name>` | Yes | `sl bookmark <name>` + `sl goto <name>` |
| `-B <name>` | Yes | `sl bookmark -f <name>` + `sl goto <name>` |
| `--detach` | Yes | `sl goto --inactive` |
| `-t/--track` | Note | Limited emulation - accepts flag |
| `-f/--force` | Yes | `sl goto -C` (discards local changes) |
| `-m/--merge` | Yes | `sl goto -m` (merge local changes) |

### git rev-parse

| Flag | Supported | Translation/Notes |
|------|-----------|-------------------|
| `--short HEAD` | Yes | `sl whereami` (truncated to 7 chars) |
| `--show-toplevel` | Yes | `sl root` |
| `--git-dir` | Yes | Returns `.sl` directory path |
| `--is-inside-work-tree` | Yes | Returns true/false |
| `--abbrev-ref HEAD` | Yes | Returns current bookmark |
| `--verify` | Yes | Validates object reference |
| `--symbolic` | Yes | Outputs in symbolic form |

## Unsupported Commands

Commands not listed above will print a message to stderr and exit with code 0:

```
gitsl: unsupported command: git checkout main
```

This exit behavior prevents gitsl from breaking tools that expect git commands to succeed.

For unsupported operations, use Sapling commands directly. See the [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) for translations.

### Why Some Commands Are Unsupported

| Command | Reason |
|---------|--------|
| `merge` | Sapling prefers rebase workflow |
| `rebase` | Complex flag translation, use `sl rebase` directly |
| `push` / `pull` / `fetch` | Remote operations differ significantly |
| `revert` | Maps to `sl backout`, not `sl revert` - semantic confusion |

## Debug Mode

Set `GITSL_DEBUG=1` to see what command would be executed without running it:

```bash
$ GITSL_DEBUG=1 gitsl status --porcelain
[DEBUG] Command: status
[DEBUG] Args: ['--porcelain']
[DEBUG] Would execute: sl status
```

## How It Works

gitsl intercepts git commands and translates them to Sapling equivalents:
1. Parses the git command and flags
2. Translates to corresponding sl command
3. Transforms output to git-compatible format where needed (status, log)
4. Returns sl's exit code

For commands without translation, gitsl prints a message to stderr and exits 0.

## License

MIT
