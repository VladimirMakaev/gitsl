# Current GitSL Flag Implementation

**Audited:** 2026-01-20
**Source files:** `/Users/vmakaev/NonWork/gitsl/cmd_*.py`

## Summary

| Metric | Count |
|--------|-------|
| Total commands implemented | 21 |
| Commands with explicit flag handling | 11 |
| Commands with pure passthrough | 10 |
| Flags with explicit transformation | 18 |
| Flags stripped/filtered | 9 |

**Note:** The milestone lists 25 commands, but the current implementation has 21 distinct command handlers. The difference is that "stash" handles 5 subcommands (push, pop, apply, list, drop) internally rather than as separate commands.

---

## Per-Command Audit

### 1. git status

**File:** `cmd_status.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `--porcelain` | Emulated | Triggers output transformation to git porcelain v1 format |
| `--short` | Emulated | Triggers output transformation (same as porcelain) |
| `-s` | Emulated | Alias for --short, triggers output transformation |
| `--ignored` | Pass-through | Works via sl status (implicit) |
| All other flags | Pass-through | Forwarded directly to `sl status` |

**Output Transformation:**
- sl status codes mapped to git XY format:
  - `M` -> ` M` (modified in working tree)
  - `A` -> `A ` (staged addition)
  - `R` -> `D ` (staged deletion)
  - `?` -> `??` (untracked)
  - `!` -> ` D` (missing/deleted from disk)
  - `I` -> `!!` (ignored)

---

### 2. git add

**File:** `cmd_add.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-A` | Explicit | Translates to `sl addremove` |
| `--all` | Explicit | Translates to `sl addremove` |
| `-u` | Explicit | Runs `sl remove --mark` for deleted tracked files only |
| `--update` | Explicit | Same as `-u` |
| All other flags | Pass-through | Forwarded directly to `sl add` |

**Special Logic:**
- `-u`/`--update` mode queries `sl status -d -n` to find deleted files and marks them for removal
- Does NOT add untracked files in update mode

---

### 3. git commit

**File:** `cmd_commit.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl commit` |

**No explicit flag handling.** Pure passthrough.

---

### 4. git log

**File:** `cmd_log.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `--oneline` | Explicit | Translates to `-T "{node|short} {desc|firstline}\n"` |
| `-N` (e.g., `-5`) | Explicit | Translates to `-l N` |
| `-n N` | Explicit | Translates to `-l N` |
| `-nN` (e.g., `-n5`) | Explicit | Translates to `-l N` |
| `--max-count=N` | Explicit | Translates to `-l N` |
| All other flags | Pass-through | Forwarded directly to `sl log` |

**Template Note:**
- Uses `{node|short}` (12 chars) for hash display in oneline mode

---

### 5. git diff

**File:** `cmd_diff.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl diff` |

**No explicit flag handling.** Pure passthrough.

---

### 6. git init

**File:** `cmd_init.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl init` |

**No explicit flag handling.** Pure passthrough.

---

### 7. git rev-parse

**File:** `cmd_rev_parse.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `--short HEAD` | Explicit | Runs `sl whereami`, truncates to 7 chars |
| All other combinations | Unsupported | Returns error message |

**Very limited implementation:**
- Only supports `--short HEAD` pattern (in any order)
- All other rev-parse variants return error
- Does NOT support: `--show-toplevel`, `--git-dir`, `--is-inside-work-tree`, etc.

---

### 8. git show

**File:** `cmd_show.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl show` |

**No explicit flag handling.** Pure passthrough.
**Documented compatible flags:** `--stat`, `-U<n>`, `-w`

---

### 9. git blame

**File:** `cmd_blame.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl annotate` |

**Command Translation:** `git blame` -> `sl annotate`
**Documented compatible flags:** `-w`

---

### 10. git rm

**File:** `cmd_rm.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-r` | Stripped | Removed (sl remove is recursive by default) |
| `--recursive` | Stripped | Removed (sl remove is recursive by default) |
| `-f` | Pass-through | Forwarded to `sl remove` |
| All other flags | Pass-through | Forwarded to `sl remove` |

**Command Translation:** `git rm` -> `sl remove`

---

### 11. git mv

**File:** `cmd_mv.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl rename` |

**Command Translation:** `git mv` -> `sl rename`
**Documented compatible flags:** `-f`

---

### 12. git clean

**File:** `cmd_clean.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-f` | Explicit | Required for safety, enables operation |
| `--force` | Explicit | Same as `-f` |
| `-n` | Explicit | Translates to `--print` (dry run) |
| `--dry-run` | Explicit | Same as `-n` |
| `-d` | Explicit | Adds `--files --dirs` to remove dirs too |
| Combined flags (e.g., `-fd`, `-fn`) | Explicit | Parsed and handled correctly |

**Command Translation:** `git clean` -> `sl purge`
**Safety:** Refuses to run without `-f` or `-n` (matches git behavior)

---

### 13. git clone

**File:** `cmd_clone.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl clone` |

**No explicit flag handling.** Pure passthrough.

---

### 14. git grep

**File:** `cmd_grep.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl grep` |

**No explicit flag handling.** Pure passthrough.
**Documented compatible flags:** `-n`, `-i`, `-l`

---

### 15. git config

**File:** `cmd_config.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `--list` | Explicit | Stripped, translates to `sl config` with no args |
| `-l` | Explicit | Same as `--list` |
| `--global` | Pass-through | Forwarded to `sl config` |
| `--local` | Pass-through | Forwarded to `sl config` |
| `--system` | Pass-through | Forwarded to `sl config` |
| `--user` | Pass-through | Forwarded to `sl config` |

**Default behavior for writes:**
- If setting a value without scope flag, adds `--local` (matches git's default)

---

### 16. git stash

**File:** `cmd_stash.py`

**Subcommand-based implementation:**

| Subcommand | Translation | Notes |
|------------|-------------|-------|
| `git stash` (no args) | `sl shelve` | |
| `git stash push` | `sl shelve` | |
| `git stash pop` | `sl unshelve` | |
| `git stash apply` | `sl unshelve --keep` | |
| `git stash list` | `sl shelve --list` | |
| `git stash drop` | `sl shelve --delete <name>` | Auto-detects most recent |
| Flags like `-m` | `sl shelve -m` | Treated as push |

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-m` (with push) | Pass-through | Forwarded to `sl shelve` |
| `--keep` (apply) | Explicit | Added for `sl unshelve` |
| `--list` | Explicit | Added for list subcommand |
| `--delete` | Explicit | Added for drop subcommand |

**Special Logic for drop:**
- Without stash reference, queries `sl shelve --list` to get most recent name

---

### 17. git checkout

**File:** `cmd_checkout.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-b` | Explicit | Creates bookmark and switches: `sl bookmark` + `sl goto` |
| `-B` | Explicit | Same as `-b` (sl bookmark updates by default) |
| `--` separator | Explicit | Disambiguates files from revisions |
| All other flags | Pass-through | Context-dependent routing |

**Disambiguation Logic:**
1. If `-b`/`-B` present: create branch mode
2. If `--` present: args after are files, before may be commit
3. Otherwise: try as revision first, then file
4. If both match: error, require `--`

**Command Routing:**
- Commit/branch checkout -> `sl goto`
- File checkout -> `sl revert`
- File checkout with commit -> `sl revert -r <commit>`

---

### 18. git switch

**File:** `cmd_switch.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-c` | Explicit | Translates to `sl bookmark <name>` |
| `--create` | Explicit | Same as `-c` |
| All other flags | Pass-through | Forwarded to `sl goto` |

**Command Translation:** `git switch` -> `sl goto`

---

### 19. git restore

**File:** `cmd_restore.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| All flags | Pass-through | All arguments forwarded to `sl revert` |

**Command Translation:** `git restore` -> `sl revert`
**Note:** `--staged` flag mentioned as out of scope in comments

---

### 20. git branch

**File:** `cmd_branch.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `-d` | Pass-through | Forwarded to `sl bookmark -d` |
| `-D` | Explicit/Safety | **Translated to `-d`** to prevent commit stripping |
| All other flags | Pass-through | Forwarded to `sl bookmark` |

**Command Translation:** `git branch` -> `sl bookmark`

**CRITICAL SAFETY:**
- `git branch -D` (force delete label, commits preserved)
- `sl bookmark -D` (delete label AND strip commits - destructive!)
- gitsl always uses `-d` to avoid destroying commits

---

### 21. git --version / git --help

**File:** `gitsl.py`

| Flag | Handling Type | Behavior |
|------|---------------|----------|
| `--version` | Explicit | Prints gitsl version |
| `-v` | Explicit | Same as `--version` |
| `--help` | Explicit | Prints usage info |
| `-h` | Explicit | Same as `--help` |
| `help` | Explicit | Same as `--help` |

---

## Gap Analysis: Missing Common Git Flags

Based on the audit, here are commonly-used git flags that are NOT explicitly handled:

### High Priority (Commonly used)

| Command | Missing Flags | Notes |
|---------|---------------|-------|
| `status` | `-u`, `--untracked-files`, `-b`, `--branch` | Show branch info |
| `log` | `--graph`, `--all`, `--decorate`, `--stat` | Visual/info flags |
| `diff` | `--staged`, `--cached`, `--name-only`, `--stat` | Diff variants |
| `commit` | `-a`, `--all`, `--amend`, `--no-edit` | Common workflows |
| `rev-parse` | `--show-toplevel`, `--git-dir`, `--is-inside-work-tree` | Directory info |
| `show` | `--name-only`, `--name-status` | Output formats |
| `branch` | `-a`, `--all`, `-r`, `--remote`, `-v`, `--verbose` | List variants |
| `checkout` | `-f`, `--force` | Force checkout |
| `restore` | `--staged`, `-s`/`--source` | Staged restore |
| `stash` | `--include-untracked`, `-u` | Stash untracked |

### Medium Priority

| Command | Missing Flags | Notes |
|---------|---------------|-------|
| `add` | `-p`, `--patch`, `-i`, `--interactive` | Interactive staging |
| `log` | `-p`, `--patch`, `--since`, `--until`, `--author` | Filtering |
| `diff` | `-w`, `--ignore-all-space` | Whitespace handling |
| `grep` | `-c`, `--count`, `-w`, `--word-regexp` | Search variants |
| `config` | `--get`, `--unset`, `--get-all` | Query operations |

---

## Commands vs Milestone List Comparison

**Milestone lists 25 commands. Current implementation:**

| # | Command | Implemented | Handler File |
|---|---------|-------------|--------------|
| 1 | status | Yes | cmd_status.py |
| 2 | add | Yes | cmd_add.py |
| 3 | commit | Yes | cmd_commit.py |
| 4 | log | Yes | cmd_log.py |
| 5 | diff | Yes | cmd_diff.py |
| 6 | init | Yes | cmd_init.py |
| 7 | rev-parse | Yes | cmd_rev_parse.py |
| 8 | show | Yes | cmd_show.py |
| 9 | blame | Yes | cmd_blame.py |
| 10 | rm | Yes | cmd_rm.py |
| 11 | mv | Yes | cmd_mv.py |
| 12 | clean | Yes | cmd_clean.py |
| 13 | clone | Yes | cmd_clone.py |
| 14 | grep | Yes | cmd_grep.py |
| 15 | config | Yes | cmd_config.py |
| 16 | stash (push) | Yes | cmd_stash.py |
| 17 | stash (pop) | Yes | cmd_stash.py |
| 18 | stash (apply) | Yes | cmd_stash.py |
| 19 | stash (list) | Yes | cmd_stash.py |
| 20 | stash (drop) | Yes | cmd_stash.py |
| 21 | checkout | Yes | cmd_checkout.py |
| 22 | switch | Yes | cmd_switch.py |
| 23 | restore | Yes | cmd_restore.py |
| 24 | branch | Yes | cmd_branch.py |

**Total: 24 unique command/subcommand combinations covered by 21 handler files.**

The milestone count of 25 may include `stash` as a single command plus its 5 subcommands = 6 entries, or there may be an off-by-one in the original count. All documented v1.0 and v1.2 commands are implemented.

---

## Implementation Patterns Summary

### Pattern 1: Pure Passthrough (10 commands)
Commands that forward all arguments unchanged to sl:
- commit, diff, init, show, blame, mv, clone, grep, restore

### Pattern 2: Command Translation Only (4 commands)
Commands that change the sl command but pass flags through:
- blame -> annotate
- mv -> rename
- restore -> revert
- clone -> clone

### Pattern 3: Flag Filtering (2 commands)
Commands that remove git-specific flags before passing to sl:
- rm: removes `-r`/`--recursive`
- branch: converts `-D` to `-d`

### Pattern 4: Flag Translation (4 commands)
Commands that translate git flags to sl equivalents:
- log: `--oneline` -> `-T template`, `-N` -> `-l N`
- clean: `-n` -> `--print`, `-d` -> `--files --dirs`
- config: `--list` -> no args, adds `--local` for writes
- switch: `-c` -> uses `sl bookmark`

### Pattern 5: Output Transformation (1 command)
Commands that run sl and transform the output:
- status: transforms sl status output to git porcelain format

### Pattern 6: Complex Routing (3 commands)
Commands with subcommands or disambiguation logic:
- stash: routes to different sl commands based on subcommand
- checkout: routes to goto or revert based on target type
- add: routes to add, addremove, or remove based on flags

---

## Flags Requiring Output Transformation

| Command | Flags | Transformation |
|---------|-------|----------------|
| status | `--porcelain`, `--short`, `-s` | sl status -> git XY format |
| rev-parse | `--short HEAD` | sl whereami -> 7-char hash |
| log | `--oneline` | Template-based (no post-processing) |

---

## Recommendations for v1.3 Flag Compatibility

1. **Expand rev-parse:** Most limited command - only supports `--short HEAD`
2. **Add diff --staged:** Common workflow flag not currently handled
3. **Add log --graph:** Popular flag for visualizing history
4. **Add branch -a/-r:** Important for remote branch visibility
5. **Add commit --amend:** Common workflow flag
6. **Consider restore --staged:** Currently marked as out of scope
