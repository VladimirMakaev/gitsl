# Stack Research: v1.2 Command Expansion

**Project:** gitsl - Git to Sapling CLI shim
**Researched:** 2026-01-19
**Scope:** Adding 13 new git commands (show, blame, rm, mv, clean, clone, grep, config, stash, checkout, switch, restore, branch)
**Confidence:** HIGH (verified with official Sapling documentation)

---

## Summary

The existing gitsl stack is **fully sufficient** for implementing all 13 new commands. No new libraries are required. The current patterns (Python stdlib only, one file per command, subprocess-based execution) scale well to the new command set. The key challenge is not tooling but semantic translation - understanding how git concepts map to Sapling equivalents, particularly for stash (shelve), checkout/switch/restore (goto/revert), and branch (bookmark).

---

## Existing Stack Assessment

### Current Dependencies

| Component | Version | Purpose | Status for v1.2 |
|-----------|---------|---------|-----------------|
| Python | >=3.8 | Runtime | Sufficient |
| subprocess (stdlib) | - | Execute sl commands | Sufficient |
| dataclasses (stdlib) | - | ParsedCommand structure | Sufficient |
| shlex (stdlib) | - | Argument handling | Sufficient |
| re (stdlib) | - | Argument parsing (log) | Sufficient |
| pytest | >=7.0 | Testing | Sufficient |

**Assessment:** The stdlib-only approach is a strength. All 13 new commands can be implemented using the existing patterns without adding dependencies.

### Current Architecture Patterns

The project follows a clean pattern that scales well:

1. **Entry point dispatch** (`gitsl.py`): Routes to command handlers
2. **Command handlers** (`cmd_*.py`): One file per command with `handle(parsed)` function
3. **Shared utilities** (`common.py`): `ParsedCommand`, `run_sl()`, `parse_argv()`

**Pattern assessment for new commands:**

| New Command | Pattern Fit | Notes |
|-------------|-------------|-------|
| show | Direct passthrough | Like `cmd_diff.py` |
| blame | Direct passthrough with alias | `sl annotate` has `blame` alias |
| rm | Direct passthrough | `sl remove` |
| mv | Direct passthrough | `sl move` |
| clean | Direct passthrough with flag translation | `-n` -> `--print` |
| clone | Direct passthrough | `sl clone` |
| grep | **No equivalent** | Sapling has no grep |
| config | Direct passthrough with scope translation | `--global` -> `--user` |
| stash | Subcommand routing | Maps to `sl shelve/unshelve` |
| checkout | Multi-mode dispatch | Commit vs file vs branch creation |
| switch | Direct passthrough | Maps to `sl goto` |
| restore | Direct passthrough with flag translation | Maps to `sl revert` |
| branch | Subcommand routing | Maps to `sl bookmark` |

---

## Command Translation Research

### Direct Mappings (8 commands)

These commands have straightforward 1:1 Sapling equivalents:

| Git Command | Sapling Command | Complexity | Notes |
|-------------|-----------------|------------|-------|
| `git show` | `sl show` | Low | Nearly identical |
| `git blame` | `sl annotate` (alias: `blame`) | Low | Direct equivalent |
| `git rm` | `sl remove` (alias: `rm`) | Low | Direct equivalent |
| `git mv` | `sl move` (alias: `mv`) | Low | Direct equivalent |
| `git clean` | `sl clean` (alias: `purge`) | Low | Flag differences: `-n` -> `--print` |
| `git clone` | `sl clone` | Low | Direct equivalent |
| `git config` | `sl config` | Medium | Scope flags differ |
| `git switch` | `sl goto` | Low | Direct equivalent |

### Stash Workflow (5 subcommands)

Git stash maps to Sapling shelve/unshelve. Key difference: Sapling uses separate commands rather than subcommands.

| Git Command | Sapling Command | Translation Notes |
|-------------|-----------------|-------------------|
| `git stash` | `sl shelve` | Direct |
| `git stash push` | `sl shelve` | Strip `push` subcommand |
| `git stash pop` | `sl unshelve` | Direct |
| `git stash apply` | `sl unshelve --keep` | Preserve shelve after applying |
| `git stash list` | `sl shelve --list` | Flag-based listing |
| `git stash drop` | `sl shelve --delete <name>` | Flag-based deletion |
| `git stash show` | `sl shelve --list --patch` | Combined flags |

**Implementation approach:** Create `cmd_stash.py` with subcommand routing:

```python
def handle(parsed: ParsedCommand) -> int:
    if not parsed.args or parsed.args[0] == "push":
        return handle_stash_push(parsed)
    elif parsed.args[0] == "pop":
        return handle_stash_pop(parsed)
    elif parsed.args[0] == "apply":
        return handle_stash_apply(parsed)
    elif parsed.args[0] == "list":
        return handle_stash_list(parsed)
    elif parsed.args[0] == "drop":
        return handle_stash_drop(parsed)
    elif parsed.args[0] == "show":
        return handle_stash_show(parsed)
    else:
        # Unknown subcommand
        ...
```

### Checkout Variants (3 modes)

Git checkout is overloaded with multiple behaviors. Sapling splits these into distinct commands.

| Git Usage | Sapling Equivalent | Detection |
|-----------|-------------------|-----------|
| `git checkout <commit>` | `sl goto <commit>` | Argument is commit-ish |
| `git checkout <branch>` | `sl goto <branch>` | Argument is bookmark |
| `git checkout -- <file>` | `sl revert <file>` | Has `--` separator or file path |
| `git checkout -b <name>` | `sl goto -B <name>` | Has `-b` flag |
| `git checkout -B <name>` | `sl goto -B <name>` | Has `-B` flag |

**Implementation approach:** Parse arguments to detect mode, then dispatch:

```python
def handle(parsed: ParsedCommand) -> int:
    if "-b" in parsed.args or "-B" in parsed.args:
        return handle_checkout_new_branch(parsed)
    elif "--" in parsed.args or looks_like_file(parsed.args):
        return handle_checkout_file(parsed)
    else:
        return handle_checkout_commit(parsed)
```

**Complexity note:** Distinguishing commit from file requires heuristics or `sl status` query.

### Switch and Restore (Git 2.23+ commands)

Git 2.23 split checkout into switch (branch switching) and restore (file restoration).

| Git Command | Sapling Equivalent | Notes |
|-------------|-------------------|-------|
| `git switch <branch>` | `sl goto <branch>` | Direct |
| `git switch -c <name>` | `sl goto -B <name>` | Create and switch |
| `git restore <file>` | `sl revert <file>` | Restore working tree |
| `git restore --staged <file>` | N/A | No staging in Sapling |
| `git restore -s <commit> <file>` | `sl revert -r <commit> <file>` | From specific revision |

**Note on --staged:** Sapling has no staging area. `git restore --staged` has no equivalent - should warn and exit.

### Branch Operations

Git branch maps to Sapling bookmark.

| Git Command | Sapling Equivalent | Notes |
|-------------|-------------------|-------|
| `git branch` | `sl bookmark` | List branches |
| `git branch <name>` | `sl bookmark <name>` | Create branch at current commit |
| `git branch -d <name>` | `sl bookmark -d <name>` | Delete branch |
| `git branch -D <name>` | `sl bookmark -d <name>` | Force delete (same in sl) |
| `git branch -m <old> <new>` | `sl bookmark -m <old> <new>` | Rename branch |
| `git branch -a` | `sl bookmark --all` | List all including remote |
| `git branch -r` | `sl bookmark --remote` | List remote only |

### Grep (No Equivalent)

**Finding:** Sapling has no built-in grep command. This was verified by checking:
- [Sapling Commands documentation](https://sapling-scm.com/docs/category/commands/)
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/)

**Recommendation:** Mark as unsupported with helpful message:

```
gitsl: 'grep' has no Sapling equivalent.
Use system grep or ripgrep directly: rg <pattern>
```

---

## Additional Requirements

### No New Libraries Needed

The existing stdlib-only approach handles all requirements:

| Requirement | Solution | Library |
|-------------|----------|---------|
| Argument parsing | Manual parsing (existing pattern) | stdlib |
| Subprocess execution | `subprocess.run()` (existing) | stdlib |
| Output transformation | String manipulation | stdlib |
| Path detection | `os.path.exists()` for checkout file mode | stdlib |

### Patterns to Add to common.py

Consider adding these utility functions to `common.py`:

```python
def run_sl_capture(args: List[str]) -> Tuple[int, str, str]:
    """Execute sl and capture stdout/stderr."""
    result = subprocess.run(["sl"] + args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def is_file_path(arg: str) -> bool:
    """Heuristic: does this argument look like a file path?"""
    # Used by checkout to distinguish file from commit
    return os.path.exists(arg) or "/" in arg or "\\" in arg
```

**Note:** `run_sl_capture` already exists implicitly in `cmd_status.py` and `cmd_rev_parse.py`. Extracting to common.py would reduce duplication.

---

## Recommendations

### Stack Decisions

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| New libraries | None | Stdlib sufficient, maintains simplicity |
| Argument parsing | Continue manual parsing | Project pattern, keeps deps minimal |
| Command structure | One file per command | Existing pattern works well |
| Stash handling | Single file with subcommand routing | Keeps related logic together |
| Checkout handling | Single file with mode detection | Complex but localized |

### What NOT to Use

| Avoided | Why |
|---------|-----|
| argparse | Overkill for translation shim; adds complexity without benefit |
| click | External dependency; violates stdlib-only principle |
| typer | External dependency; too heavy for simple dispatch |
| Regular expressions (excessive) | Manual parsing is clearer for simple flag translation |

### Implementation Order

Based on complexity and dependencies:

1. **Direct mappings first** (show, blame, rm, mv, clean, clone)
   - Simplest implementations
   - Build confidence in patterns
   - 6 commands, ~30 lines each

2. **Config** (medium complexity)
   - Scope flag translation
   - Good test of flag transformation pattern

3. **Switch and restore** (medium complexity)
   - Cleaner than checkout
   - Good preparation for checkout

4. **Branch** (medium complexity)
   - Subcommand routing pattern
   - Good preparation for stash

5. **Stash** (higher complexity)
   - Multiple subcommands
   - Uses patterns from branch

6. **Checkout** (highest complexity)
   - Multi-mode detection
   - Builds on switch and restore

7. **Grep** (unsupported)
   - Just error message
   - Document why

---

## Testing Considerations

### Existing Test Infrastructure

The project has excellent test infrastructure that extends naturally:

- `conftest.py` provides `sl_repo`, `sl_repo_with_commit` fixtures
- `helpers/commands.py` provides `run_command`, `run_gitsl`
- Subprocess-based E2E testing pattern

### New Fixtures Needed

| Fixture | Purpose | Commands |
|---------|---------|----------|
| `sl_repo_with_shelve` | Repo with shelved changes | stash tests |
| `sl_repo_with_bookmarks` | Repo with multiple bookmarks | branch, switch tests |
| `sl_repo_with_multiple_commits` | Repo with commit history | show, blame tests |

### Test Categories per Command

| Command | Unit Tests | E2E Tests | Notes |
|---------|------------|-----------|-------|
| show | Flag translation | Output verification | |
| blame | Flag translation | Output verification | |
| rm/mv/clean | Passthrough | File operations | Need file fixtures |
| clone | Minimal | Repo creation | Slow, may limit |
| config | Scope translation | Config operations | |
| stash/* | Subcommand routing | Shelve operations | Multiple scenarios |
| checkout | Mode detection | Switch/revert | Complex |
| switch | Flag translation | Goto operations | |
| restore | Flag translation | Revert operations | |
| branch | Subcommand routing | Bookmark operations | |
| grep | Error message | N/A | Unsupported |

---

## Sources

### Official Sapling Documentation (HIGH Confidence)

- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Command mappings
- [Sapling Commands Reference](https://sapling-scm.com/docs/category/commands/) - Full command list
- [sl show](https://sapling-scm.com/docs/commands/show/) - Show command details
- [sl annotate](https://sapling-scm.com/docs/commands/annotate/) - Blame equivalent
- [sl shelve](https://sapling-scm.com/docs/commands/shelve/) - Stash equivalent
- [sl unshelve](https://sapling-scm.com/docs/commands/unshelve/) - Stash pop/apply
- [sl goto](https://sapling-scm.com/docs/commands/goto/) - Checkout/switch equivalent
- [sl revert](https://sapling-scm.com/docs/commands/revert/) - Restore equivalent
- [sl clean](https://sapling-scm.com/docs/commands/clean/) - Clean command
- [sl config](https://sapling-scm.com/docs/commands/config/) - Config command
- [sl bookmark](https://sapling-scm.com/docs/commands/bookmark/) - Branch equivalent
- [sl clone](https://sapling-scm.com/docs/commands/clone/) - Clone command
- [Sapling Shelve Overview](https://sapling-scm.com/docs/overview/shelve) - Shelve concepts

### Project Documentation (HIGH Confidence)

- Existing `cmd_*.py` files - Established patterns
- `common.py` - Shared utilities
- `tests/conftest.py` - Test fixtures

---

## Roadmap Implications

### Suggested Phase Structure

Based on stack research, recommend 4 phases:

1. **Phase 1: Direct Mappings** (6 commands)
   - show, blame, rm, mv, clean, clone
   - Low complexity, builds momentum
   - Estimated: 1-2 tasks

2. **Phase 2: Config and Simple Branch** (2 commands)
   - config (flag translation)
   - switch (direct mapping to goto)
   - Medium complexity
   - Estimated: 1 task

3. **Phase 3: Restore and Branch** (2 commands)
   - restore (maps to revert with flags)
   - branch (subcommand routing)
   - Introduces subcommand pattern
   - Estimated: 1-2 tasks

4. **Phase 4: Stash and Checkout** (2 commands + grep)
   - stash (all subcommands)
   - checkout (mode detection)
   - grep (unsupported message)
   - Highest complexity
   - Estimated: 2-3 tasks

### Risk Areas

| Risk | Mitigation |
|------|------------|
| checkout mode detection | Start with explicit flags, add heuristics later |
| stash subcommand edge cases | Test each subcommand independently |
| --staged flag (no equivalent) | Clear error message pointing to Sapling model |

### No Research Needed for Phases

All commands are well-documented in Sapling. Phase-specific research is **not required** - the mappings are clear from official documentation.
