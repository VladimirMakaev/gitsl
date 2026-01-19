# Features Research: v1.2 Command Expansion

**Domain:** Git to Sapling CLI shim command translation
**Researched:** 2026-01-19
**Research Mode:** Features dimension for v1.2 milestone
**Confidence:** HIGH

---

## Executive Summary

This research documents the expected git command behaviors, flags, and output formats for each new command being added in v1.2. Each command is analyzed for its Sapling equivalent, with flags categorized into table stakes (must support), differentiators (nice-to-have), and out of scope (too complex). The focus is on **practical translation accuracy** rather than comprehensive flag coverage.

---

## Command-by-Command Analysis

### Direct Mappings

---

### git show

**Sapling translation:** `sl show`

**Behavior:** Displays information about commits, tags, or objects. By default shows the most recent commit with its diff.

**Output format differences:**
- Git uses 40-char commit hashes by default; Sapling uses 12-char by default
- Git shows `commit <hash>` header; Sapling shows similar format
- Diff output is compatible when using `--git` flag in Sapling

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (none - show latest commit) | `sl show` | Direct passthrough |
| **Table Stakes** | `<commit>` (positional) | `sl show <commit>` | Direct passthrough |
| **Table Stakes** | `--stat` | `sl show --stat` | Direct mapping |
| **Table Stakes** | `-p`, `--patch` | `sl show` (default) | Default behavior |
| **Table Stakes** | `--no-patch`, `-s` | Not directly available | Need output filtering or template |
| **Differentiator** | `--oneline` | `sl show -T "{node|short} {desc|firstline}\n"` | Requires template |
| **Differentiator** | `--format=<format>` | `sl show -T "<template>"` | Partial; template syntax differs |
| **Differentiator** | `-U<n>`, `--unified=<n>` | `sl show -U<n>` | Direct mapping |
| **Differentiator** | `-w`, `--ignore-all-space` | `sl show -w` | Direct mapping |
| **Differentiator** | `-b`, `--ignore-space-change` | `sl show -b` | Direct mapping |
| **Out of Scope** | `--name-only` | No direct equivalent | Complex output transformation |
| **Out of Scope** | `--name-status` | No direct equivalent | Complex output transformation |
| **Out of Scope** | `--abbrev-commit` | Default in sl | Already abbreviated |

**Recommended implementation:**
```python
# Passthrough with optional flag translation
# Most flags map directly or are ignored safely
sl_cmd = ['show'] + args  # Most args passthrough
```

**Sources:** [git show docs](https://git-scm.com/docs/git-show), [sl show docs](https://sapling-scm.com/docs/commands/show/)

---

### git blame

**Sapling translation:** `sl annotate` (alias: `sl blame`)

**Behavior:** Shows per-line commit information for a file. Displays who last modified each line.

**Output format differences:**
- Git default: `<hash> (<author> <date> <line-num>) <content>`
- Sapling default: `<changeset>: <content>` (more compact)
- Output transformation may be needed for exact git format

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<file>` (positional) | `sl annotate <file>` | Direct mapping |
| **Table Stakes** | `-L <start>,<end>` | Not directly available | Sapling annotates whole file |
| **Differentiator** | `-l` (long hash) | `sl annotate` shows changeset | Different format |
| **Differentiator** | `-t` (timestamp) | `-d` shows date | Flag translation |
| **Differentiator** | `-e`, `--show-email` | Not available | No equivalent |
| **Differentiator** | `-s` (suppress author/time) | Default sl output | Close match |
| **Differentiator** | `-u`, `--user` | `sl annotate -u` | Direct mapping |
| **Differentiator** | `-d`, `--date` | `sl annotate -d` | Direct mapping |
| **Differentiator** | `-n`, `--number` | `sl annotate -n` | Direct mapping |
| **Differentiator** | `-c`, `--changeset` | `sl annotate -c` | Direct mapping (default) |
| **Differentiator** | `-w` (ignore whitespace) | `sl annotate -w` | Direct mapping |
| **Out of Scope** | `--porcelain`, `-p` | No equivalent | Complex output format |
| **Out of Scope** | `-M` (detect moves) | Not available | Sapling tracks differently |
| **Out of Scope** | `-C` (detect copies) | Not available | Sapling tracks differently |
| **Out of Scope** | `--ignore-rev` | Not available | Git-specific feature |

**Semantic differences:**
- Sapling `annotate` uses changeset identifiers, not commit hashes
- Line range selection (`-L`) not available in Sapling annotate
- Move/copy detection works differently (Sapling tracks renames internally)

**Recommended implementation:**
```python
# Basic translation with flag mapping
# sl annotate -u -d <file> gives similar output to git blame
sl_cmd = ['annotate'] + translated_flags + [file]
```

**Sources:** [git blame docs](https://git-scm.com/docs/git-blame), [sl annotate docs](https://sapling-scm.com/docs/commands/annotate/)

---

### git rm

**Sapling translation:** `sl remove` (alias: `sl rm`)

**Behavior:** Removes files from the working tree and stages the removal.

**Semantic differences:**
- Git has staging area; Sapling does not (removal is immediate for next commit)
- Both support keeping file on disk with appropriate flag

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<files>` (positional) | `sl remove <files>` | Direct mapping |
| **Table Stakes** | `-f`, `--force` | `sl remove -f` | Direct mapping |
| **Table Stakes** | `--cached` | `sl remove` | Sapling default; file stays on disk |
| **Table Stakes** | `-r` | `sl remove` | Recursive is default |
| **Differentiator** | `-n`, `--dry-run` | Not available | Need manual check |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress output manually |
| **Out of Scope** | `--ignore-unmatch` | Not available | Exit code handling |
| **Out of Scope** | `--sparse` | Not available | Sparse checkout specific |

**Note:** The `--mark` flag in Sapling is useful for files already deleted from disk (similar to what gitsl already uses for `git add -u`).

**Recommended implementation:**
```python
# Handle --cached specially (Sapling default behavior)
# Most flags map directly
if '--cached' in args:
    args.remove('--cached')  # Sapling keeps file by default
sl_cmd = ['remove'] + args
```

**Sources:** [git rm docs](https://git-scm.com/docs/git-rm), [sl remove docs](https://sapling-scm.com/docs/commands/remove/)

---

### git mv

**Sapling translation:** `sl mv` (also `sl move`, `sl rename`)

**Behavior:** Moves or renames files, tracking the change for version control.

**Semantic differences:**
- Git records rename in staging area; Sapling records immediately
- Sapling tracks renames internally (when not using git backend)

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<src> <dst>` (positional) | `sl mv <src> <dst>` | Direct mapping |
| **Table Stakes** | `-f`, `--force` | `sl mv -f` | Direct mapping (force overwrite) |
| **Differentiator** | `-n`, `--dry-run` | Not available | Need manual check |
| **Differentiator** | `-v`, `--verbose` | Not available | Output manually |
| **Differentiator** | `-k` (skip errors) | Not available | Error handling differs |

**Recommended implementation:**
```python
# Simple passthrough with flag filtering
sl_cmd = ['mv'] + [a for a in args if a not in ('-n', '--dry-run', '-v', '--verbose', '-k')]
```

**Sources:** [git mv docs](https://git-scm.com/docs/git-mv), [sl mv via basic commands](https://sapling-scm.com/docs/overview/basic-commands/)

---

### git clean

**Sapling translation:** `sl clean` (also `sl purge`)

**Behavior:** Removes untracked files from the working tree.

**Semantic differences:**
- Git requires `-f` by default (unless `clean.requireForce=false`)
- Sapling `clean` removes untracked files by default without requiring force

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `-f`, `--force` | `sl clean` | Sapling doesn't require force |
| **Table Stakes** | `-d` (include directories) | `sl clean --dirs` | Direct mapping |
| **Table Stakes** | `-n`, `--dry-run` | `sl clean --print` | Flag translation |
| **Differentiator** | `-x` (include ignored) | `sl clean --ignored` | Direct mapping |
| **Differentiator** | `-X` (only ignored) | `sl clean --ignored` + filter | Partial; different semantics |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress output manually |
| **Differentiator** | `-e <pattern>` | `-X, --exclude` | Flag translation |
| **Out of Scope** | `-i`, `--interactive` | Not available | Interactive mode |

**Important:** Git's `-f` is required for safety; Sapling does not require this. Translation should handle `-f` gracefully (ignore it).

**Recommended implementation:**
```python
# Translate git clean flags to sl clean
# -f is ignored (not needed in Sapling)
# -n/--dry-run -> --print
# -d -> --dirs
sl_args = ['clean']
if '-n' in args or '--dry-run' in args:
    sl_args.append('--print')
if '-d' in args:
    sl_args.append('--dirs')
if '-x' in args:
    sl_args.append('--ignored')
```

**Sources:** [git clean docs](https://git-scm.com/docs/git-clean), [sl clean docs](https://sapling-scm.com/docs/commands/clean/)

---

### git clone

**Sapling translation:** `sl clone`

**Behavior:** Creates a copy of a repository.

**Semantic differences:**
- Both support cloning from URLs and local paths
- Sapling uses git under the hood for remote operations
- Shallow clone support differs

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<url>` (positional) | `sl clone <url>` | Direct mapping |
| **Table Stakes** | `<url> <dir>` (positional) | `sl clone <url> <dir>` | Direct mapping |
| **Differentiator** | `-b <branch>`, `--branch` | `-u, --updaterev` | Flag translation |
| **Differentiator** | `-n`, `--no-checkout` | `-U, --noupdate` | Flag translation |
| **Differentiator** | `--depth <n>` | Not directly available | Shallow clone differs |
| **Differentiator** | `-q`, `--quiet` | Not available | Output differs |
| **Out of Scope** | `--mirror` | Not available | Different model |
| **Out of Scope** | `--bare` | Not available | Different model |
| **Out of Scope** | `--recurse-submodules` | Not available | Submodule model differs |
| **Out of Scope** | `--single-branch` | Implicit with `-u` | Different semantics |
| **Out of Scope** | `--shallow-*` | Not available | Limited shallow support |

**Recommended implementation:**
```python
# Basic clone with branch/checkout translation
sl_args = ['clone']
for i, arg in enumerate(args):
    if arg in ('-b', '--branch'):
        sl_args.extend(['-u', args[i+1]])
        skip_next = True
    elif arg in ('-n', '--no-checkout'):
        sl_args.append('-U')
    else:
        sl_args.append(arg)
```

**Sources:** [git clone docs](https://git-scm.com/docs/git-clone), [sl clone docs](https://sapling-scm.com/docs/commands/clone/)

---

### git grep

**Sapling translation:** `sl grep`

**Behavior:** Searches for patterns in tracked files.

**Semantic differences:**
- Both support regex and literal string matching
- Context line options are similar
- Sapling grep is generally compatible

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<pattern>` (positional) | `sl grep <pattern>` | Direct mapping |
| **Table Stakes** | `<pattern> <pathspec>` | `sl grep <pattern> <pathspec>` | Direct mapping |
| **Table Stakes** | `-n`, `--line-number` | Default in sl | Already shows line numbers |
| **Table Stakes** | `-i`, `--ignore-case` | `sl grep -i` | Direct mapping |
| **Differentiator** | `-l`, `--files-with-matches` | `sl grep -l` | Direct mapping |
| **Differentiator** | `-L`, `--files-without-match` | Not available | No equivalent |
| **Differentiator** | `-c`, `--count` | Not available | No equivalent |
| **Differentiator** | `-w`, `--word-regexp` | Not available | Use regex |
| **Differentiator** | `-v`, `--invert-match` | Not available | No equivalent |
| **Differentiator** | `-E`, `--extended-regexp` | Default | Already extended regex |
| **Differentiator** | `-F`, `--fixed-strings` | Not available | Escape pattern manually |
| **Differentiator** | `-A <n>`, `--after-context` | `sl grep -A <n>` | Direct mapping |
| **Differentiator** | `-B <n>`, `--before-context` | `sl grep -B <n>` | Direct mapping |
| **Differentiator** | `-C <n>`, `--context` | `sl grep -A <n> -B <n>` | Combine flags |
| **Out of Scope** | `-P`, `--perl-regexp` | Not available | Use standard regex |
| **Out of Scope** | `--cached` | Different semantics | Sapling searches working copy |
| **Out of Scope** | `-p`, `--show-function` | Not available | No equivalent |

**Note:** Sapling grep is well-aligned with git grep for common use cases. Advanced git grep features like `--and`, `--or`, `--all-match` are not available.

**Recommended implementation:**
```python
# Most flags pass through directly
# Handle -C by splitting into -A and -B
sl_cmd = ['grep'] + args  # Most passthrough
```

**Sources:** [git grep docs](https://git-scm.com/docs/git-grep), [sl grep via basic commands](https://sapling-scm.com/docs/overview/basic-commands/)

---

### git config

**Sapling translation:** `sl config`

**Behavior:** Gets and sets configuration values.

**Semantic differences:**
- Git uses `--global`, `--system`, `--local`; Sapling uses `-u`, `-s`, `-l`
- Configuration file locations differ
- Sapling config command structure is similar

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<key>` (get) | `sl config <key>` | Direct mapping |
| **Table Stakes** | `<key> <value>` (set) | `sl config <section.key> <value>` | Direct mapping |
| **Table Stakes** | `--global` | `-u`, `--user` | Flag translation |
| **Table Stakes** | `--local` | `-l`, `--local` | Direct mapping |
| **Table Stakes** | `--system` | `-s`, `--system` | Flag translation |
| **Table Stakes** | `--list`, `-l` | `sl config` (no args) | Different invocation |
| **Differentiator** | `--get` | Default behavior | Just `sl config <key>` |
| **Differentiator** | `--unset` | `-d`, `--delete` | Flag translation |
| **Differentiator** | `-e`, `--edit` | `-u`/`-l`/`-s` with no args | Opens editor |
| **Out of Scope** | `--get-regexp` | Not available | Different query model |
| **Out of Scope** | `--get-all` | Not available | Multi-value differs |
| **Out of Scope** | `--type` | Not available | Type coercion differs |
| **Out of Scope** | `--show-origin` | `--debug` | Different output |

**Important notes:**
- Git config keys use format `section.key`; Sapling uses same format
- User config file: Git `~/.gitconfig`; Sapling `~/.sapling/sapling.conf` or `~/.hgrc`
- Not all git config keys have Sapling equivalents

**Recommended implementation:**
```python
# Translate scope flags
if '--global' in args:
    args = ['-u' if a == '--global' else a for a in args]
if '--system' in args:
    args = ['-s' if a == '--system' else a for a in args]
if '--unset' in args:
    args = ['-d' if a == '--unset' else a for a in args]
sl_cmd = ['config'] + args
```

**Sources:** [git config docs](https://git-scm.com/docs/git-config), [sl config docs](https://sapling-scm.com/docs/commands/config/)

---

## Stash/Shelve Workflow

---

### git stash (push)

**Sapling translation:** `sl shelve`

**Behavior:** Temporarily saves uncommitted changes.

**Semantic differences:**
- Git stash uses a stack with `stash@{n}` references
- Sapling shelve uses named shelves (can auto-generate names)
- Both can include untracked files optionally

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl shelve` | Direct mapping |
| **Table Stakes** | `-m <message>` | `sl shelve -m <message>` | Direct mapping |
| **Differentiator** | `-u`, `--include-untracked` | `-u`, `--unknown` | Flag translation |
| **Differentiator** | `-k`, `--keep-index` | Not available | No staging area in Sapling |
| **Differentiator** | `-S`, `--staged` | Not available | No staging area in Sapling |
| **Differentiator** | `-a`, `--all` | `--unknown` | Close equivalent |
| **Differentiator** | `-p`, `--patch` | `-i`, `--interactive` | Interactive mode |
| **Out of Scope** | `push` subcommand | Implicit | Just `sl shelve` |

**Recommended implementation:**
```python
sl_args = ['shelve']
if '-u' in args or '--include-untracked' in args:
    sl_args.append('--unknown')
if '-m' in args:
    idx = args.index('-m')
    sl_args.extend(['-m', args[idx + 1]])
```

**Sources:** [git stash docs](https://git-scm.com/docs/git-stash), [sl shelve docs](https://sapling-scm.com/docs/commands/shelve/)

---

### git stash pop

**Sapling translation:** `sl unshelve`

**Behavior:** Applies stashed changes and removes from stash.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl unshelve` | Direct mapping; uses most recent |
| **Table Stakes** | `stash@{n}` | `sl unshelve -n <name>` | Reference translation needed |
| **Differentiator** | `--index` | Not available | No staging area |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress output manually |

**Note:** Git uses `stash@{n}` notation; Sapling uses named shelves. Translation requires mapping or using default (most recent).

**Recommended implementation:**
```python
# Default: unshelve most recent
sl_args = ['unshelve']
# Note: stash@{n} translation is complex; recommend just supporting default
```

**Sources:** [git stash docs](https://git-scm.com/docs/git-stash), [sl unshelve docs](https://sapling-scm.com/docs/commands/unshelve/)

---

### git stash list

**Sapling translation:** `sl shelve --list`

**Behavior:** Lists all stashed changes.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl shelve --list` | Direct mapping |
| **Out of Scope** | `--format` | Not available | Output format fixed |

**Output format differences:**
- Git: `stash@{0}: WIP on branch: <commit> <message>`
- Sapling: Shows shelve names and descriptions

**Recommended implementation:**
```python
sl_cmd = ['shelve', '--list']
```

---

### git stash drop

**Sapling translation:** `sl shelve --delete`

**Behavior:** Removes a stash entry.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl shelve --delete` | Deletes most recent |
| **Table Stakes** | `stash@{n}` | `sl shelve --delete <name>` | Reference translation |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress manually |

**Recommended implementation:**
```python
# Default: delete most recent
# With arg: need to translate stash@{n} to shelve name
sl_args = ['shelve', '--delete']
```

---

### git stash apply

**Sapling translation:** `sl unshelve --keep`

**Behavior:** Applies stashed changes but keeps the stash.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl unshelve --keep` | Direct mapping |
| **Table Stakes** | `stash@{n}` | `sl unshelve --keep -n <name>` | Reference translation |
| **Differentiator** | `--index` | Not available | No staging area |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress manually |

**Recommended implementation:**
```python
sl_args = ['unshelve', '--keep']
```

---

## Checkout/Switch/Restore Commands

---

### git checkout (branch/commit)

**Sapling translation:** `sl goto`

**Behavior:** Switches to a different branch or commit.

**Semantic differences:**
- Git `checkout` is overloaded (branches, files, detached HEAD)
- Sapling separates: `goto` for navigation, `revert` for files
- Detection logic needed to determine user intent

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<branch>` | `sl goto <branch>` | Direct mapping |
| **Table Stakes** | `<commit>` | `sl goto <commit>` | Direct mapping |
| **Table Stakes** | `-f`, `--force` | `-C`, `--clean` | Flag translation |
| **Differentiator** | `-m`, `--merge` | `-m`, `--merge` | Direct mapping |
| **Differentiator** | `--detach` | Implicit for commits | Sapling behavior |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress manually |
| **Out of Scope** | `-t`, `--track` | Different model | Bookmarks work differently |
| **Out of Scope** | `--guess` | Not available | Remote tracking differs |

**Recommended implementation:**
```python
# Detect if target is a file (use revert) or ref (use goto)
# This is the most complex translation
if is_existing_file(target) and not is_ref(target):
    return handle_checkout_file(args)
else:
    return handle_checkout_ref(args)
```

---

### git checkout (file restoration)

**Sapling translation:** `sl revert`

**Behavior:** Restores file(s) to a previous state.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `-- <file>` | `sl revert <file>` | Direct mapping |
| **Table Stakes** | `<commit> -- <file>` | `sl revert -r <commit> <file>` | Flag addition |
| **Differentiator** | `-p`, `--patch` | `-i`, `--interactive` | Interactive mode |
| **Out of Scope** | `--ours` / `--theirs` | Not available | Conflict resolution differs |

---

### git checkout -b

**Sapling translation:** `sl bookmark <name>` + optionally `sl goto`

**Behavior:** Creates a new branch and switches to it.

**Semantic differences:**
- Git creates branch ref pointing to current commit, then switches
- Sapling bookmarks are lightweight markers; creating one at current location is immediate
- No need to explicitly goto if already at the location

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `-b <branch>` | `sl bookmark <name>` | Create bookmark at current |
| **Table Stakes** | `-b <branch> <start>` | `sl goto <start>` + `sl bookmark <name>` | Two commands |
| **Differentiator** | `-B <branch>` (force) | `sl bookmark -f <name>` | Force overwrite |
| **Out of Scope** | `-t`, `--track` | Not available | Tracking differs |
| **Out of Scope** | `--orphan` | Not available | Different model |

**Recommended implementation:**
```python
# git checkout -b <name> [<start>]
if start_point:
    run_sl(['goto', start_point])
run_sl(['bookmark', name])
```

---

### git switch

**Sapling translation:** `sl goto`

**Behavior:** Modern replacement for `git checkout` (branch switching only).

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<branch>` | `sl goto <branch>` | Direct mapping |
| **Table Stakes** | `-c <branch>` | `sl bookmark <name>` | Create new branch |
| **Table Stakes** | `-C <branch>` | `sl bookmark -f <name>` | Force create |
| **Table Stakes** | `-d`, `--detach` | `sl goto <commit>` | Implicit for commits |
| **Differentiator** | `-f`, `--force` | `-C`, `--clean` | Flag translation |
| **Differentiator** | `-m`, `--merge` | `-m`, `--merge` | Direct mapping |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress manually |
| **Differentiator** | `--guess` | Not available | Remote guessing differs |
| **Out of Scope** | `-t`, `--track` | Not available | Tracking differs |
| **Out of Scope** | `--orphan` | Not available | Different model |

**Recommended implementation:**
```python
# Simpler than checkout - only handles refs
if '-c' in args:
    # Create new branch
    name = args[args.index('-c') + 1]
    run_sl(['bookmark', name])
else:
    sl_args = ['goto']
    if '-f' in args or '--force' in args:
        sl_args.append('-C')
    sl_args.append(target)
    run_sl(sl_args)
```

**Sources:** [git switch docs](https://git-scm.com/docs/git-switch), [sl goto docs](https://sapling-scm.com/docs/commands/goto/)

---

### git restore

**Sapling translation:** `sl revert`

**Behavior:** Modern replacement for `git checkout` (file restoration only).

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<file>` | `sl revert <file>` | Direct mapping |
| **Table Stakes** | `-s <source>`, `--source` | `sl revert -r <source>` | Flag translation |
| **Differentiator** | `-W`, `--worktree` | Default behavior | Already default |
| **Differentiator** | `-S`, `--staged` | Not applicable | No staging area |
| **Differentiator** | `-p`, `--patch` | `-i`, `--interactive` | Interactive mode |
| **Differentiator** | `-q`, `--quiet` | Not available | Suppress manually |
| **Out of Scope** | `--ours` / `--theirs` | Not available | Conflict resolution |
| **Out of Scope** | `--overlay` / `--no-overlay` | Not available | Different model |

**Note:** `--staged` is meaningless in Sapling (no staging area). Should either warn or ignore.

**Recommended implementation:**
```python
sl_args = ['revert']
if '-s' in args or '--source' in args:
    # Extract source and translate to -r
    source = get_arg_value(args, '-s', '--source')
    sl_args.extend(['-r', source])
sl_args.extend(files)
```

**Sources:** [git restore docs](https://git-scm.com/docs/git-restore), [sl revert docs](https://sapling-scm.com/docs/commands/revert/)

---

## Branch/Bookmark Commands

---

### git branch (list)

**Sapling translation:** `sl bookmark`

**Behavior:** Lists local branches.

**Semantic differences:**
- Git branches are refs; Sapling bookmarks are lightweight markers
- Git shows current branch with `*`; Sapling shows active bookmark differently
- Output format differs significantly

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | (no args) | `sl bookmark` | Lists bookmarks |
| **Differentiator** | `-a`, `--all` | `sl bookmark --all` | Include remote |
| **Differentiator** | `-r`, `--remotes` | `sl bookmark --remote` | Remote only |
| **Differentiator** | `-v`, `--verbose` | Not available | Different output |
| **Differentiator** | `--list <pattern>` | Not available | Filter manually |
| **Out of Scope** | `--show-current` | `sl whereami` | Different command |
| **Out of Scope** | `--contains` | Not available | Commit ancestry differs |
| **Out of Scope** | `--merged` / `--no-merged` | Not available | Different model |

**Output format differences:**
- Git: `* main` (current with asterisk), `  feature`
- Sapling: Different format, may need transformation for exact match

**Recommended implementation:**
```python
# Basic listing - output format will differ
sl_cmd = ['bookmark']
if '-a' in args or '--all' in args:
    sl_cmd.append('--all')
if '-r' in args or '--remotes' in args:
    sl_cmd.append('--remote')
```

---

### git branch <name>

**Sapling translation:** `sl bookmark <name>`

**Behavior:** Creates a new branch at current commit.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `<name>` | `sl bookmark <name>` | Direct mapping |
| **Table Stakes** | `<name> <start>` | `sl bookmark -r <start> <name>` | Flag addition |
| **Differentiator** | `-f`, `--force` | `sl bookmark -f` | Direct mapping |
| **Out of Scope** | `-t`, `--track` | Different model | Tracking differs |
| **Out of Scope** | `--set-upstream-to` | Different model | Tracking differs |

**Recommended implementation:**
```python
sl_args = ['bookmark']
if start_point:
    sl_args.extend(['-r', start_point])
if '-f' in args or '--force' in args:
    sl_args.append('-f')
sl_args.append(name)
```

---

### git branch -d

**Sapling translation:** `sl bookmark -d`

**Behavior:** Deletes a branch.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `-d <name>` | `sl bookmark -d <name>` | Direct mapping |
| **Table Stakes** | `-D <name>` | `sl bookmark -d <name>` | Sapling doesn't check merge |
| **Differentiator** | `-f`, `--force` | Not needed | Sapling always deletes |

**Semantic difference:** Git `-d` checks if branch is merged; Sapling `-d` always deletes. No safety check in Sapling.

**Recommended implementation:**
```python
# Both -d and -D translate to sl bookmark -d
sl_cmd = ['bookmark', '-d', name]
```

---

### git branch -m

**Sapling translation:** `sl bookmark -m`

**Behavior:** Renames a branch.

| Category | Flags | Sapling Equivalent | Notes |
|----------|-------|-------------------|-------|
| **Table Stakes** | `-m <old> <new>` | `sl bookmark -m <old> <new>` | Direct mapping |
| **Table Stakes** | `-m <new>` (current) | `sl bookmark -m <current> <new>` | Need current name |
| **Differentiator** | `-M` (force) | `sl bookmark -m` | Sapling doesn't check |

**Sources:** [git branch docs](https://git-scm.com/docs/git-branch), [sl bookmark docs](https://sapling-scm.com/docs/commands/bookmark/)

---

## Summary Tables

### Table Stakes (Must Support)

| Command | Core Behavior | Key Flags |
|---------|---------------|-----------|
| `git show` | View commit details | `<commit>`, `--stat` |
| `git blame` | Per-line annotations | `<file>`, `-u`, `-d` |
| `git rm` | Remove files | `<files>`, `-f`, `--cached` |
| `git mv` | Move/rename files | `<src> <dst>`, `-f` |
| `git clean` | Remove untracked | `-f`, `-d`, `-n` |
| `git clone` | Clone repository | `<url>`, `-b`, `-n` |
| `git grep` | Search files | `<pattern>`, `-i`, `-n` |
| `git config` | Get/set config | `<key>`, `--global`, `--local` |
| `git stash` | Save changes | (none), `-m` |
| `git stash pop` | Apply and remove | (none) |
| `git stash list` | List stashes | (none) |
| `git stash drop` | Remove stash | (none) |
| `git stash apply` | Apply keep stash | (none) |
| `git checkout <ref>` | Switch branch/commit | `<ref>`, `-f` |
| `git checkout <file>` | Restore file | `-- <file>` |
| `git checkout -b` | Create and switch | `-b <name>` |
| `git switch` | Switch branch | `<branch>`, `-c` |
| `git restore` | Restore file | `<file>`, `-s` |
| `git branch` (list) | List branches | (none) |
| `git branch <name>` | Create branch | `<name>` |
| `git branch -d` | Delete branch | `-d <name>` |

### Differentiators (Nice to Have)

| Command | Feature | Notes |
|---------|---------|-------|
| `git show` | `--oneline`, `-U<n>` | Template translation |
| `git blame` | `-w`, `-f`, `-l` | Most map directly |
| `git stash` | `-u` (untracked) | Maps to `--unknown` |
| `git grep` | `-A`, `-B`, `-C` context | Direct mapping |
| `git branch` | `-a`, `-r` | Remote listing |
| `git switch` | `-m` (merge) | Direct mapping |

### Out of Scope

| Command | Feature | Reason |
|---------|---------|--------|
| `git show` | `--name-only`, `--name-status` | Complex output transformation |
| `git blame` | `--porcelain`, `-M`, `-C` | Machine format, move detection |
| `git clone` | `--mirror`, `--bare`, `--shallow-*` | Different repository models |
| `git config` | `--get-regexp`, `--type` | Advanced query/type features |
| `git stash` | `stash@{n}` references | Complex reference translation |
| `git checkout` | `--track`, `--orphan` | Different branch model |
| `git branch` | `--contains`, `--merged` | Commit ancestry analysis |
| All | Interactive modes (`-i`, `-p`) | Terminal control required |

---

## Implementation Complexity Ranking

| Rank | Command | Complexity | Reason |
|------|---------|------------|--------|
| 1 | `git show` | LOW | Direct passthrough |
| 2 | `git rm` | LOW | Direct passthrough |
| 3 | `git mv` | LOW | Direct passthrough |
| 4 | `git clone` | LOW | Minor flag translation |
| 5 | `git branch` (list) | LOW | Direct passthrough |
| 6 | `git branch -d` | LOW | Direct mapping |
| 7 | `git grep` | LOW | Mostly passthrough |
| 8 | `git stash list` | LOW | Direct flag |
| 9 | `git blame` | MEDIUM | Flag translation |
| 10 | `git clean` | MEDIUM | Flag translation |
| 11 | `git config` | MEDIUM | Scope flag translation |
| 12 | `git stash` (push) | MEDIUM | Flag translation |
| 13 | `git stash pop/apply` | MEDIUM | Simple but needs `--keep` |
| 14 | `git stash drop` | MEDIUM | Name translation optional |
| 15 | `git branch <name>` | MEDIUM | Start point handling |
| 16 | `git switch` | MEDIUM | Create/force logic |
| 17 | `git restore` | MEDIUM | Source flag translation |
| 18 | `git checkout -b` | MEDIUM | Two-step operation |
| 19 | `git checkout <file>` | HIGH | Detection logic |
| 20 | `git checkout <ref>` | HIGH | Detection logic, ambiguity |

---

## Sources

### Git Documentation
- [git show](https://git-scm.com/docs/git-show) - Show command reference
- [git blame](https://git-scm.com/docs/git-blame) - Blame command reference
- [git rm](https://git-scm.com/docs/git-rm) - Remove command reference
- [git mv](https://git-scm.com/docs/git-mv) - Move command reference
- [git clean](https://git-scm.com/docs/git-clean) - Clean command reference
- [git clone](https://git-scm.com/docs/git-clone) - Clone command reference
- [git grep](https://git-scm.com/docs/git-grep) - Grep command reference
- [git config](https://git-scm.com/docs/git-config) - Config command reference
- [git stash](https://git-scm.com/docs/git-stash) - Stash command reference
- [git checkout](https://git-scm.com/docs/git-checkout) - Checkout command reference
- [git switch](https://git-scm.com/docs/git-switch) - Switch command reference
- [git restore](https://git-scm.com/docs/git-restore) - Restore command reference
- [git branch](https://git-scm.com/docs/git-branch) - Branch command reference

### Sapling Documentation
- [sl show](https://sapling-scm.com/docs/commands/show/) - Show command reference
- [sl annotate](https://sapling-scm.com/docs/commands/annotate/) - Annotate command reference
- [sl remove](https://sapling-scm.com/docs/commands/remove/) - Remove command reference
- [sl clean](https://sapling-scm.com/docs/commands/clean/) - Clean command reference
- [sl clone](https://sapling-scm.com/docs/commands/clone/) - Clone command reference
- [sl config](https://sapling-scm.com/docs/commands/config/) - Config command reference
- [sl shelve](https://sapling-scm.com/docs/commands/shelve/) - Shelve command reference
- [sl unshelve](https://sapling-scm.com/docs/commands/unshelve/) - Unshelve command reference
- [sl goto](https://sapling-scm.com/docs/commands/goto/) - Goto command reference
- [sl revert](https://sapling-scm.com/docs/commands/revert/) - Revert command reference
- [sl bookmark](https://sapling-scm.com/docs/commands/bookmark/) - Bookmark command reference
- [Basic commands](https://sapling-scm.com/docs/overview/basic-commands/) - Overview of common commands
