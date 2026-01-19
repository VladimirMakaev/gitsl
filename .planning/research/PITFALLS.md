# Pitfalls Research: v1.2 Git Command Expansion

**Domain:** Git-to-Sapling CLI command translation
**Researched:** 2026-01-19
**Confidence:** HIGH (verified against Sapling official documentation and Git documentation)

---

## Summary

Expanding gitsl to support additional commands (show, blame, rm, mv, clean, clone, grep, config, stash, checkout, switch, restore, branch) introduces significant complexity due to fundamental differences between Git and Sapling models. The most critical pitfalls involve:

1. **Semantic model differences** - Git branches vs Sapling bookmarks, Git staging vs Sapling's no-staging model
2. **Command overloading** - Git checkout does 3+ different things, requiring disambiguation
3. **Output format incompatibility** - Tools parse git blame/branch output; format differences break tooling
4. **Stash/shelve behavioral differences** - Conflict handling, naming conventions, list formats differ
5. **Destructive operations** - clean/purge, checkout --force can cause data loss

This research identifies 25 specific pitfalls organized by command category with prevention strategies and phase recommendations.

---

## Critical Pitfalls

### Pitfall 1: checkout Command Overloading

**Risk:** `git checkout` does multiple unrelated things - switching commits, restoring files, and creating branches. Translating incorrectly causes data loss or unexpected behavior.

**What goes wrong:**
- `git checkout <branch>` = switch to branch (sl goto)
- `git checkout <file>` = restore file to HEAD (sl revert)
- `git checkout <commit> -- <file>` = restore file to specific commit (sl revert -r)
- `git checkout -b <branch>` = create and switch to new branch (sl bookmark + goto)

If gitsl guesses wrong about whether an argument is a branch/commit or a file, it either:
- Switches to wrong commit instead of restoring file
- Restores file when user wanted to switch commits
- Both can cause work loss

**Warning signs:**
- Tests pass with clear branch names but fail with ambiguous arguments
- User reports "file disappeared" or "ended up on wrong commit"
- Arguments that look like paths but are also valid refs

**Prevention:**
```python
# Disambiguation strategy (match git's approach):
def disambiguate_checkout_target(args):
    # 1. If -- separator present, everything after is paths
    if '--' in args:
        return parse_with_separator(args)

    # 2. Check if arg exists as file on disk
    # 3. Check if arg exists as ref (commit/branch/bookmark)
    # 4. If both, prefer ref (git behavior) but consider --
    # 5. If neither, error
```

**Phase:** Checkout/Switch/Restore implementation. This is the most complex command to implement correctly.

**Source:** [Git Checkout Documentation](https://git-scm.com/docs/git-checkout), [Sapling goto](https://sapling-scm.com/docs/commands/goto/), [Sapling revert](https://sapling-scm.com/docs/commands/revert/) - HIGH confidence

---

### Pitfall 2: Bookmark vs Branch Model Mismatch

**Risk:** Git branches and Sapling bookmarks have fundamentally different semantics, causing confusion and incorrect behavior.

**What goes wrong:**
- **Git branches are mandatory** - you're always on a branch (or detached HEAD, which is a warning state)
- **Sapling bookmarks are optional** - commits exist without bookmarks, visible in smartlog
- **Rebase behavior differs** - Git rebasing affects only current branch; Sapling rebasing moves ALL bookmarks on affected commits
- **Deletion semantics differ** - Deleting git branch makes commits hard to find; deleting Sapling bookmark doesn't hide commits

**Warning signs:**
- User expects to be "on a branch" but Sapling shows no active bookmark
- `git branch` output is empty when user expects to see branches
- Rebase moves more bookmarks than expected

**Prevention:**
```python
# For `git branch` listing:
# - Include all bookmarks from `sl bookmark`
# - May need to indicate "no active bookmark" state differently than detached HEAD

# For `git branch -d`:
# - Warn that commits will still be visible (different from git)
# - Map to `sl bookmark -d`

# Consider: Should we show "detached HEAD" warning when no bookmark active?
# Git users expect this; Sapling users don't care
```

**Phase:** Branch/Bookmark implementation. Design decision needed about how to represent Sapling's bookmarkless state.

**Source:** [Sapling Bookmarks Overview](https://sapling-scm.com/docs/overview/bookmarks/), [Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) - HIGH confidence

---

### Pitfall 3: blame/annotate Output Format Incompatibility

**Risk:** Many tools parse `git blame` output programmatically. Sapling's `sl annotate` produces different output format, breaking these tools.

**What goes wrong:**
Git blame default format:
```
abc1234 (Author Name 2024-01-15 10:30:45 +0000 42) line content
```

Git blame --porcelain format includes structured headers:
```
abc1234567890123456789012345678901234567890 42 42 1
author Author Name
author-mail <author@example.com>
author-time 1705315845
...
```

Sapling annotate format differs - uses changeset IDs, different date formats, different spacing.

Tools that break:
- IDE blame integrations
- Code review tools
- `git blame --porcelain | some-parser`

**Warning signs:**
- blame output "looks different" in visual inspection
- Tools that parse blame output fail silently or crash
- Date parsing fails due to format differences

**Prevention:**
```python
# Options for handling:

# Option 1: Output transformation (HIGH effort)
# Capture sl annotate output, transform to git format
# Must handle: hash length, author format, date format, line numbers

# Option 2: Pass-through with documentation (LOW effort)
# Document that blame output format differs
# Tools may need adjustment

# Option 3: Support only git blame --porcelain
# Easier to emit structured format from sl annotate data

# Recommendation: Start with pass-through, add --porcelain support
# if user feedback indicates need
```

**Phase:** Blame implementation. Consider output transformation if tools depend on exact format.

**Source:** [Git blame Documentation](https://git-scm.com/docs/git-blame), [Sapling annotate](https://sapling-scm.com/docs/commands/annotate/) - HIGH confidence

---

### Pitfall 4: stash/shelve Naming and Listing Differences

**Risk:** `git stash list` format differs from `sl shelve --list`, breaking scripts that parse stash output.

**What goes wrong:**
Git stash list format:
```
stash@{0}: WIP on main: abc1234 Commit message
stash@{1}: On feature: def5678 Another message
```

Tools parse the `stash@{N}` syntax to reference stashes. Sapling shelve uses names:
```
name1           (1 hour ago) description
name2           (2 days ago) another description
```

**Warning signs:**
- Scripts using `git stash pop stash@{1}` fail
- Parsing stash list for automation fails
- Different default naming conventions

**Prevention:**
```python
# For `git stash list`:
# Transform sl shelve --list output to git format
# Generate stash@{N} references from shelve list order

def transform_shelve_list_to_stash_format(shelve_output):
    lines = []
    for i, shelf in enumerate(parse_shelves(shelve_output)):
        # Format: stash@{N}: message or WIP description
        lines.append(f"stash@{{i}}: {shelf.description or 'WIP'}")
    return '\n'.join(lines)

# For `git stash pop stash@{1}`:
# Convert stash@{N} reference to shelve name
# Get Nth shelve from list, use its name for unshelve
```

**Phase:** Stash/Shelve implementation. Output format transformation required.

**Source:** [Git stash Documentation](https://git-scm.com/docs/git-stash), [Sapling shelve](https://sapling-scm.com/docs/commands/shelve/) - HIGH confidence

---

### Pitfall 5: stash pop Conflict Handling Differences

**Risk:** When `git stash pop` encounters conflicts, it keeps the stash. `sl unshelve` may behave differently, causing data loss or confusion.

**What goes wrong:**
- Git: On conflict, stash is NOT dropped - use `git stash drop` after resolving
- Sapling: On conflict, enters unfinished merge state, must use `--continue` or `--abort`
- If gitsl doesn't handle this correctly, user may lose shelved changes

**Warning signs:**
- User reports "stash disappeared after conflict"
- Conflict resolution workflow differs
- `git stash list` shows different count than expected after conflict

**Prevention:**
```python
# For `git stash pop`:
# 1. Run sl unshelve
# 2. Check for conflict state (exit code, output)
# 3. If conflict:
#    - Print message matching git's behavior
#    - Ensure shelve is preserved (--keep behavior)
# 4. If success:
#    - Shelve is removed (default unshelve behavior matches git)

# Key: sl unshelve on conflict requires --continue or --abort
# git stash pop on conflict leaves stash intact
# Must detect conflict and NOT remove shelve
```

**Phase:** Stash/Shelve implementation. Critical to prevent data loss.

**Source:** [Git stash pop behavior](https://www.geeksforgeeks.org/git/how-to-undo-git-stash-pop-that-results-in-merge-conflict/), [Sapling unshelve](https://sapling-scm.com/docs/commands/unshelve/) - HIGH confidence

---

### Pitfall 6: clean/purge Data Loss Without Confirmation

**Risk:** `git clean` and `sl purge/clean` permanently delete untracked files. Incorrect flag translation or missing safety checks causes irreversible data loss.

**What goes wrong:**
- `git clean` requires `-f` to actually delete (safety mechanism)
- `sl clean` deletes by default (requires `--print` for dry-run)
- If gitsl passes through without requiring `-f`, user may lose files unexpectedly

Flag differences:
- Git: `-f` force (required), `-d` directories, `-x` ignored files, `-n` dry-run
- Sapling: `--files` (default), `--dirs`, `--ignored`, `--print` (dry-run)

**Warning signs:**
- Files deleted without `-f` flag
- Dry-run flag doesn't work as expected
- Different files deleted than expected

**Prevention:**
```python
# For `git clean`:
# CRITICAL: Do not execute deletion without -f flag (match git safety)

def handle_clean(args):
    # Require -f for actual deletion (git behavior)
    if '-f' not in args and '--force' not in args:
        if '-n' not in args and '--dry-run' not in args:
            print("fatal: clean.requireForce defaults to true", file=sys.stderr)
            return 1

    # Translate flags:
    # -n, --dry-run -> --print
    # -d -> --dirs
    # -x -> --ignored
    # -f -> (remove, it's default behavior in sl)

    sl_args = translate_clean_flags(args)
    return run_sl(['clean'] + sl_args)
```

**Phase:** Clean implementation. Safety-critical - extensive testing required.

**Source:** [Sapling clean](https://sapling-scm.com/docs/commands/clean/) - HIGH confidence

---

### Pitfall 7: checkout/goto with Uncommitted Changes

**Risk:** `git checkout` and `sl goto` handle uncommitted changes differently, causing unexpected merges or blocked operations.

**What goes wrong:**
- Git checkout: Fails if uncommitted changes would be overwritten, allows if changes are in unaffected files
- Sapling goto: By default, attempts to merge uncommitted changes if destination is ancestor/descendant; aborts otherwise

Flag mapping:
- `git checkout --force` / `-f` -> `sl goto --clean` (discards changes)
- `git checkout --merge` / `-m` -> `sl goto --merge` (explicit merge)

**Warning signs:**
- User expects checkout to fail but it merges instead
- User expects checkout to work but it aborts
- Changes unexpectedly merged or lost

**Prevention:**
```python
# For `git checkout <commit>`:
# Consider: Should default behavior match git (fail) or sapling (merge if safe)?

# Recommendation: Match git behavior for compatibility
# Add warning when sapling would have merged but gitsl blocks

def handle_checkout_commit(commit, args):
    # Check for uncommitted changes
    if has_uncommitted_changes():
        if '--force' in args or '-f' in args:
            return run_sl(['goto', '--clean', commit])
        elif '--merge' in args or '-m' in args:
            return run_sl(['goto', '--merge', commit])
        else:
            # Match git: check if changes would be overwritten
            # This may require additional logic
            pass
```

**Phase:** Checkout/Switch implementation. Behavior alignment decision needed.

**Source:** [Sapling goto](https://sapling-scm.com/docs/commands/goto/), [Git checkout](https://git-scm.com/docs/git-checkout) - HIGH confidence

---

### Pitfall 8: config Scope Flag Differences

**Risk:** `git config` and `sl config` have different scope flags and behaviors, causing configuration to be written to wrong location.

**What goes wrong:**
Git scopes:
- `--global` - User-level (~/.gitconfig)
- `--local` - Repository-level (.git/config)
- `--system` - System-wide (/etc/gitconfig)
- Default: local for writes, cascading for reads

Sapling scopes:
- `--user` / `-u` - User-level
- `--local` / `-l` - Repository-level
- `--system` / `-s` - System-wide

If gitsl maps `--global` incorrectly, config written to wrong location.

**Warning signs:**
- Config setting doesn't take effect
- Wrong config file modified
- Config appears to disappear after repo change

**Prevention:**
```python
# Flag mapping:
# --global -> --user / -u
# --local -> --local / -l (same)
# --system -> --system / -s (same)

# Additional differences:
# - sl config with no args opens editor
# - git config with no args shows help
# - sl config section.name=value works
# - git config section.name value works (space-separated)

def translate_config_args(args):
    translated = []
    for arg in args:
        if arg == '--global':
            translated.append('--user')
        elif arg.startswith('--global='):
            translated.append('--user')
        else:
            translated.append(arg)
    return translated
```

**Phase:** Config implementation. Flag translation required.

**Source:** [Sapling config](https://sapling-scm.com/docs/commands/config/), [Git config](https://git-scm.com/docs/git-config) - HIGH confidence

---

### Pitfall 9: rm/remove with Unstaged Modifications

**Risk:** `git rm` and `sl remove` behave differently when files have local modifications, potentially causing work loss.

**What goes wrong:**
Git rm behavior:
- Fails if file has local modifications (safety)
- Requires `-f` to force removal of modified files
- `--cached` removes from index only, keeps file

Sapling remove behavior matrix:
| Options | Clean | Modified | Missing |
|---------|-------|----------|---------|
| None    | Remove | Warn    | Remove  |
| -f      | Remove | Remove  | Remove  |

**Warning signs:**
- Modified file removed without warning
- User expects removal to fail but file is deleted
- `--cached` behavior not implemented

**Prevention:**
```python
# For `git rm`:
# 1. Check if file has local modifications
# 2. If modified and no -f flag, fail with warning
# 3. Handle --cached flag (may not have direct sl equivalent)

# Note: sl remove has --mark for already-deleted files
# git rm doesn't need this - it handles missing files

# --cached handling options:
# Option A: Use sl forget (stops tracking, keeps file)
# Option B: Error "not supported"
# Recommendation: Map --cached to sl forget
```

**Phase:** rm/mv implementation. Safety behavior must match git.

**Source:** [Sapling remove](https://sapling-scm.com/docs/commands/remove/) - HIGH confidence

---

### Pitfall 10: mv/rename with Destination Conflicts

**Risk:** File rename when destination exists behaves differently between git and sapling.

**What goes wrong:**
- Git mv: Fails if destination exists (unless -f)
- Sapling rename: May have different conflict behavior

Additionally:
- Git tracks renames through content similarity
- Sapling explicitly tracks copies/renames

**Warning signs:**
- Overwrite happens without -f flag
- Rename history not preserved correctly
- Directory rename edge cases

**Prevention:**
```python
# For `git mv`:
# 1. Check if destination exists
# 2. If exists and no -f flag, fail
# 3. Use sl rename (or sl mv alias)

# Directory handling:
# git mv dir1 dir2 - renames directory
# sl rename dir1 dir2 - should work similarly

# -n/--dry-run: Check if sl rename supports this
# -f/--force: Force overwrite
```

**Phase:** rm/mv implementation.

**Source:** [Sapling basic commands](https://sapling-scm.com/docs/overview/basic-commands/) - MEDIUM confidence

---

## Moderate Pitfalls

### Pitfall 11: show Command Rev Specification Differences

**Risk:** `git show <rev>` accepts various revision specifications that may not translate directly to Sapling.

**What goes wrong:**
Git revision specs:
- `HEAD` -> `.` in Sapling
- `HEAD^` -> `.^` in Sapling
- `HEAD~3` -> Sapling equivalent needed
- `branch:file` -> Different syntax
- `@{n}` reflog references -> No direct Sapling equivalent

**Warning signs:**
- Complex rev specs fail
- HEAD references not translated
- Relative references fail

**Prevention:**
```python
# Translation layer for common rev specs:
def translate_revision(rev):
    if rev == 'HEAD':
        return '.'
    if rev == 'HEAD^' or rev == 'HEAD~1':
        return '.^'
    if rev.startswith('HEAD~'):
        n = rev[5:]
        return f'.~{n}'  # May need different syntax
    # Pass through for commit hashes
    return rev
```

**Phase:** Show implementation. May need revision translation utility.

**Source:** [Sapling show](https://sapling-scm.com/docs/commands/show/) - HIGH confidence

---

### Pitfall 12: grep Working Directory vs History Search

**Risk:** `git grep` can search working directory or commit history. Flag translation may cause wrong search scope.

**What goes wrong:**
Git grep modes:
- `git grep pattern` - Search working directory
- `git grep pattern HEAD` - Search specific commit
- `git grep pattern HEAD -- path` - Search commit with path filter

Need to verify sl grep has equivalent modes.

**Warning signs:**
- Search returns unexpected results (wrong commit)
- Path filtering doesn't work
- Binary file handling differs

**Prevention:**
```python
# Verify sl grep supports:
# - Working directory search (default)
# - Commit search with -r/--rev
# - Path filtering

# Flag translation:
# -n (line numbers) -> may be default or need flag
# -l (files only) -> --files-with-matches?
# -c (count) -> --count?
# -i (case insensitive) -> -i?
```

**Phase:** Grep implementation. Verify flag compatibility.

**Source:** [Sapling basic commands](https://sapling-scm.com/docs/overview/basic-commands/) - MEDIUM confidence

---

### Pitfall 13: clone Depth and Filter Options

**Risk:** `git clone --depth` and other clone options may not translate to Sapling, which has different lazy-fetch model.

**What goes wrong:**
Git clone options:
- `--depth N` - Shallow clone
- `--single-branch` - One branch only
- `--branch` - Clone specific branch
- `--mirror` - Mirror clone

Sapling clone:
- Lazy fetching by default (different model than shallow)
- May not support all git clone options

**Warning signs:**
- Clone options silently ignored
- Clone takes unexpected time (full vs shallow)
- Branch options don't work

**Prevention:**
```python
# Options to support:
# --branch / -b -> Likely supported
# --depth -> May not apply (Sapling uses lazy fetch)

# Recommendation:
# 1. Pass-through basic clone
# 2. Warn on unsupported options
# 3. Document differences in lazy fetch behavior

def handle_clone(args):
    unsupported = ['--depth', '--shallow-since', '--shallow-exclude']
    for opt in unsupported:
        if opt in ' '.join(args):
            print(f"Warning: {opt} not supported, using Sapling lazy fetch",
                  file=sys.stderr)
```

**Phase:** Clone implementation. Document limitations.

**Source:** [Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) - MEDIUM confidence

---

### Pitfall 14: switch --create vs checkout -b Flag Differences

**Risk:** `git switch -c` and `git checkout -b` create branches differently; translation must handle both.

**What goes wrong:**
- `git checkout -b newbranch` = create and switch
- `git checkout -B newbranch` = create/reset and switch
- `git switch -c newbranch` = create and switch
- `git switch -C newbranch` = create/reset and switch

All need to map to: `sl bookmark newbranch` + `sl goto newbranch`
Or possibly: `sl goto --bookmark newbranch`

**Warning signs:**
- New bookmark not created
- Not switched to new bookmark after creation
- -B/-C reset behavior not implemented

**Prevention:**
```python
# For git checkout -b:
def handle_checkout_create_branch(branch_name, start_point=None):
    # Create bookmark
    if start_point:
        run_sl(['bookmark', branch_name, '-r', start_point])
    else:
        run_sl(['bookmark', branch_name])
    # Switch to it
    return run_sl(['goto', branch_name])

# For -B (force/reset):
# May need to delete existing bookmark first, then recreate
```

**Phase:** Checkout/Switch implementation.

**Source:** [Sapling bookmark](https://sapling-scm.com/docs/commands/bookmark/) - HIGH confidence

---

### Pitfall 15: restore --staged Flag (No Sapling Equivalent)

**Risk:** `git restore --staged` removes files from staging area. Sapling has no staging area, making this meaningless.

**What goes wrong:**
- User runs `git restore --staged file`
- In git: Removes file from staging, keeps working tree change
- In Sapling: No staging area exists - what should happen?

**Warning signs:**
- `--staged` flag silently ignored
- User confused about what happened
- Different behavior than expected

**Prevention:**
```python
# Options:
# 1. Warn that --staged is not applicable
# 2. Treat as no-op with message
# 3. Map to some Sapling equivalent (uncommit?)

# Recommendation:
def handle_restore_staged(args):
    if '--staged' in args or '-S' in args:
        print("gitsl: --staged has no effect (Sapling has no staging area)",
              file=sys.stderr)
        # Remove flag and continue? Or exit?
        # Depends on whether other args present
```

**Phase:** Restore implementation. Design decision needed.

**Source:** [Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) - HIGH confidence

---

### Pitfall 16: branch -r and -a Remote Branch Listing

**Risk:** `git branch -r` lists remote branches; Sapling has different remote model.

**What goes wrong:**
- `git branch` - Local branches
- `git branch -r` - Remote branches
- `git branch -a` - All branches

Sapling: `sl bookmark --remote` or `sl bookmark -a` for all

**Warning signs:**
- Remote branches not showing
- Different format than expected
- Remote names not prefixed correctly (origin/)

**Prevention:**
```python
# Flag mapping:
# -r, --remotes -> --remote
# -a, --all -> -a / --all

# Output format:
# Git: origin/main, origin/feature
# Sapling: remote/main, remote/feature (verify format)

# May need output transformation to match git format
```

**Phase:** Branch implementation.

**Source:** [Sapling bookmark](https://sapling-scm.com/docs/commands/bookmark/) - HIGH confidence

---

### Pitfall 17: stash with Untracked Files

**Risk:** `git stash -u` includes untracked files; `sl shelve` may handle this differently.

**What goes wrong:**
- `git stash` - Only tracked modified files
- `git stash -u` / `--include-untracked` - Also untracked files
- `git stash -a` / `--all` - Also ignored files

Sapling shelve has `--unknown` flag for untracked files.

**Warning signs:**
- Untracked files not stashed when expected
- Different default behavior
- Flag translation incorrect

**Prevention:**
```python
# Flag mapping:
# -u, --include-untracked -> --unknown
# -a, --all -> --unknown + (ignored handling?)

# Verify sl shelve --unknown behavior matches expectations
```

**Phase:** Stash implementation.

**Source:** [Sapling shelve](https://sapling-scm.com/docs/commands/shelve/) - MEDIUM confidence

---

### Pitfall 18: stash drop vs shelve --delete Syntax

**Risk:** `git stash drop stash@{n}` uses special syntax; Sapling uses shelve names.

**What goes wrong:**
Git syntax:
- `git stash drop` - Drop latest
- `git stash drop stash@{2}` - Drop specific by index

Sapling syntax:
- `sl shelve --delete` - Delete all? Or prompt?
- `sl shelve --delete name` - Delete specific by name

**Warning signs:**
- Wrong stash deleted
- Index-based reference fails
- All stashes accidentally deleted

**Prevention:**
```python
# Need to:
# 1. Parse stash@{n} syntax
# 2. Get list of shelves
# 3. Find Nth shelve
# 4. Delete by name

def handle_stash_drop(args):
    if not args or args[0] == 'stash@{0}':
        # Get first shelve name
        name = get_first_shelve_name()
    else:
        # Parse stash@{n}
        n = parse_stash_ref(args[0])
        name = get_nth_shelve_name(n)

    return run_sl(['shelve', '--delete', name])
```

**Phase:** Stash implementation.

**Source:** [Sapling shelve](https://sapling-scm.com/docs/commands/shelve/) - HIGH confidence

---

### Pitfall 19: revert Semantic Confusion (git revert vs sl revert)

**Risk:** `git revert` creates a new commit that undoes a previous commit. `sl revert` restores files to a previous state. These are completely different operations.

**What goes wrong:**
- User runs `git revert <commit>` expecting to undo that commit
- If gitsl maps to `sl revert`, files change but no undo commit is created
- User's mental model completely broken

Note: The correct Sapling equivalent is `sl backout`.

**Warning signs:**
- No new commit created when expected
- Changes appear in working directory instead of new commit
- User confusion about what happened

**Prevention:**
```python
# CRITICAL: Do NOT implement git revert mapping to sl revert
# git revert <commit> -> sl backout <commit>
# git checkout <file> -> sl revert <file>
# git restore <file> -> sl revert <file>

# Make this very clear in implementation:
# These are DIFFERENT commands despite similar names
```

**Phase:** Command planning. Document this distinction clearly.

**Source:** [Sapling revert](https://sapling-scm.com/docs/commands/revert/) - HIGH confidence (explicitly documented)

---

### Pitfall 20: Empty Stash/Shelve Operations

**Risk:** Running stash operations when there's nothing to stash or no stashes exist.

**What goes wrong:**
- `git stash` with clean working tree - Creates nothing, no error
- `git stash pop` with no stashes - Error
- `git stash drop` with no stashes - Error

Need to match these behaviors exactly.

**Warning signs:**
- No error when expected
- Error when not expected
- Different exit codes

**Prevention:**
```python
# For git stash (save):
# Check if there are changes first
# If no changes, print "No local changes to save" and exit 0

# For git stash pop/drop/apply:
# Check if any shelves exist
# If none, error: "No stash entries found"
```

**Phase:** Stash implementation.

**Source:** [Git stash Documentation](https://git-scm.com/docs/git-stash) - HIGH confidence

---

## Minor Concerns

### Pitfall 21: clone Output Progress Display

**Risk:** Clone progress output format differs, potentially confusing users or breaking parsers.

**Prevention:** Pass through sl clone output directly; document any format differences.

**Phase:** Clone implementation.

---

### Pitfall 22: show --stat Format Differences

**Risk:** `git show --stat` format may differ from `sl show --stat`.

**Prevention:** Both support --stat; verify format compatibility or document differences.

**Phase:** Show implementation.

---

### Pitfall 23: branch --merged/--no-merged Filtering

**Risk:** `git branch --merged` shows branches merged into current; Sapling may not have direct equivalent.

**Prevention:** Check if sl bookmark supports this filtering; warn if unsupported.

**Phase:** Branch implementation.

---

### Pitfall 24: grep --cached vs Working Tree

**Risk:** `git grep --cached` searches index (staged content); Sapling has no index.

**Prevention:** Warn that --cached is not applicable or treat as no-op.

**Phase:** Grep implementation.

---

### Pitfall 25: config --unset and --remove-section

**Risk:** Config removal commands may have different syntax between git and sl.

**Prevention:** Verify sl config --delete behavior; translate --unset appropriately.

**Phase:** Config implementation.

---

## Phase-Specific Warning Summary

| Phase/Category | Critical Pitfalls | Moderate Pitfalls | Key Prevention |
|----------------|-------------------|-------------------|----------------|
| Checkout/Switch/Restore | #1 (overloading), #7 (uncommitted), #15 (--staged) | #14 (create flags), #19 (revert confusion) | Disambiguation logic, behavior alignment |
| Branch/Bookmark | #2 (model mismatch) | #16 (remote listing), #23 (--merged) | Design decisions about bookmarkless state |
| Stash/Shelve | #4 (list format), #5 (conflict handling) | #17 (untracked), #18 (drop syntax), #20 (empty) | Output transformation, conflict detection |
| Blame/Show | #3 (output format) | #11 (rev specs), #22 (--stat) | Format transformation or documentation |
| Clean/Purge | #6 (data loss) | - | Safety flag requirement |
| Config | #8 (scope flags) | #25 (--unset) | Flag translation |
| rm/mv | #9 (modifications), #10 (conflicts) | - | Safety checks |
| Clone | - | #13 (depth options), #21 (progress) | Document lazy fetch differences |
| Grep | - | #12 (history search), #24 (--cached) | Verify flag compatibility |

---

## Implementation Priority Recommendation

Based on pitfall severity and complexity:

### Phase 1: Safe Direct Mappings
Commands with minimal pitfall risk:
- `git show` -> `sl show` (Pitfall #11 minor)
- `git grep` -> `sl grep` (Pitfall #12, #24 minor)
- `git clone` -> `sl clone` (Pitfall #13, #21 minor)

### Phase 2: Moderate Complexity
Commands requiring flag translation:
- `git config` -> `sl config` (Pitfall #8)
- `git rm` -> `sl remove` (Pitfall #9)
- `git mv` -> `sl rename` (Pitfall #10)
- `git clean` -> `sl clean` (Pitfall #6 - CRITICAL safety)

### Phase 3: High Complexity - Stash
Commands requiring output transformation:
- `git stash` -> `sl shelve` (Pitfalls #4, #5, #17, #18, #20)

### Phase 4: High Complexity - Checkout Family
Commands requiring disambiguation and complex logic:
- `git checkout` (Pitfalls #1, #7, #14)
- `git switch` (Pitfall #14)
- `git restore` (Pitfall #15)

### Phase 5: Model Translation
Commands exposing fundamental model differences:
- `git branch` (Pitfalls #2, #16, #23)
- `git blame` (Pitfall #3)

---

## Sources

- [Sapling Differences from Git](https://sapling-scm.com/docs/introduction/differences-git/) - HIGH confidence
- [Sapling Bookmarks Overview](https://sapling-scm.com/docs/overview/bookmarks/) - HIGH confidence
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - HIGH confidence
- [Sapling goto Command](https://sapling-scm.com/docs/commands/goto/) - HIGH confidence
- [Sapling revert Command](https://sapling-scm.com/docs/commands/revert/) - HIGH confidence
- [Sapling annotate Command](https://sapling-scm.com/docs/commands/annotate/) - HIGH confidence
- [Sapling shelve Command](https://sapling-scm.com/docs/commands/shelve/) - HIGH confidence
- [Sapling unshelve Command](https://sapling-scm.com/docs/commands/unshelve/) - HIGH confidence
- [Sapling clean Command](https://sapling-scm.com/docs/commands/clean/) - HIGH confidence
- [Sapling config Command](https://sapling-scm.com/docs/commands/config/) - HIGH confidence
- [Sapling remove Command](https://sapling-scm.com/docs/commands/remove/) - HIGH confidence
- [Sapling bookmark Command](https://sapling-scm.com/docs/commands/bookmark/) - HIGH confidence
- [Sapling show Command](https://sapling-scm.com/docs/commands/show/) - HIGH confidence
- [Git blame Documentation](https://git-scm.com/docs/git-blame) - HIGH confidence
- [Git checkout Documentation](https://git-scm.com/docs/git-checkout) - HIGH confidence
- [Git stash Documentation](https://git-scm.com/docs/git-stash) - HIGH confidence
- [Git config Documentation](https://git-scm.com/docs/git-config) - HIGH confidence
- [Graphite: Git Checkout vs Switch](https://graphite.com/guides/git-checkout-vs-switch) - MEDIUM confidence
