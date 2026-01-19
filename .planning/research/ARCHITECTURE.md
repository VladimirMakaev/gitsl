# Architecture Research: v1.2 Command Expansion

**Domain:** Git-to-Sapling CLI Shim - Command Handler Integration
**Researched:** 2026-01-19
**Confidence:** HIGH (based on direct codebase analysis)

## Summary

The existing gitsl architecture is well-suited for the v1.2 command expansion. The codebase follows a consistent pattern: each command has a dedicated `cmd_*.py` module exporting a `handle(parsed: ParsedCommand) -> int` function. The main `gitsl.py` dispatcher routes commands to handlers via simple if-statements. New commands integrate by: (1) creating a `cmd_*.py` handler, (2) importing it in `gitsl.py`, (3) adding a dispatch condition, and (4) updating `pyproject.toml` py-modules list. The five command categories (pass-through, rename, subcommand translation, complex disambiguation, model translation) each have established patterns in the existing codebase that can be extended.

---

## Existing Patterns Analysis

### Entry Point and Dispatch (`gitsl.py`)

The dispatcher is straightforward:

```python
# Import all command handlers
import cmd_status
import cmd_log
# ... etc

def main(argv: List[str] = None) -> int:
    parsed = parse_argv(argv)

    # Special flags (--version, --help)
    # ...

    # Debug mode early exit
    if is_debug_mode():
        print_debug_info(parsed)
        return 0

    # Command dispatch
    if parsed.command == "status":
        return cmd_status.handle(parsed)
    if parsed.command == "log":
        return cmd_log.handle(parsed)
    # ... more commands

    # Unsupported fallback
    print(f"gitsl: unsupported command: ...", file=sys.stderr)
    return 0
```

**Pattern:** Each command is a simple if-condition. No routing table, no registry. This works well for the current 7 commands but may become unwieldy with 20+ commands. Consider introducing a command registry for v1.2.

### Command Handler Interface (`common.py`)

All handlers share the same signature:

```python
def handle(parsed: ParsedCommand) -> int:
    """Handle the command. Return exit code."""
```

Where `ParsedCommand` contains:
- `command: Optional[str]` - The git command (e.g., "commit", "status")
- `args: List[str]` - Remaining arguments after the command
- `raw_argv: List[str]` - Original argv for debugging

**Pattern:** Handlers receive the full argument list and are responsible for their own parsing and translation.

### Handler Complexity Levels

The existing handlers demonstrate three complexity levels:

**Level 1: Pass-through (simplest)**
```python
# cmd_commit.py, cmd_diff.py, cmd_init.py
def handle(parsed: ParsedCommand) -> int:
    return run_sl(["commit"] + parsed.args)  # Just change command name
```

**Level 2: Flag translation**
```python
# cmd_log.py
def handle(parsed: ParsedCommand) -> int:
    # Parse args to identify --oneline, -N, etc.
    # Build sl command with translated flags
    return run_sl(sl_args)
```

**Level 3: Output transformation**
```python
# cmd_status.py
def handle(parsed: ParsedCommand) -> int:
    if needs_transform:
        # Capture sl output, transform, print
        result = subprocess.run(['sl', 'status'] + sl_args, capture_output=True)
        transformed = transform_to_porcelain(result.stdout)
        sys.stdout.write(transformed)
        return result.returncode
    return run_sl(['status'] + parsed.args)
```

**Level 4: Multi-step operations**
```python
# cmd_add.py (for -u flag)
def handle(parsed: ParsedCommand) -> int:
    if "-u" in parsed.args:
        # Query sl for deleted files
        deleted_files = get_deleted_files(pathspec)
        # Mark deleted files for removal
        if deleted_files:
            subprocess.run(["sl", "remove", "--mark"] + deleted_files)
        return 0
    return run_sl(["add"] + parsed.args)
```

### Shared Utilities (`common.py`)

Current utilities:
- `ParsedCommand` - Dataclass for parsed arguments
- `parse_argv(argv)` - Parse git-style arguments
- `is_debug_mode()` - Check GITSL_DEBUG environment variable
- `print_debug_info(parsed)` - Debug output
- `run_sl(args)` - Execute sl command with I/O passthrough

---

## New Command Categories

Based on the project context, the 13 new commands fall into 5 categories:

### Category 1: Simple Pass-through

**Commands:** `show`, `clone`, `grep`, `config`

**Pattern:** Same as `cmd_commit.py`, `cmd_diff.py`, `cmd_init.py`

```python
# cmd_show.py
from common import ParsedCommand, run_sl

def handle(parsed: ParsedCommand) -> int:
    return run_sl(["show"] + parsed.args)
```

**Complexity:** LOW - One function, 3-5 lines each
**Dependencies:** None (can be implemented in any order)
**Testing:** Verify command reaches sl, exit code propagates

### Category 2: Command Rename

**Commands:**
- `blame` -> `annotate`
- `rm` -> `remove`
- `mv` -> `rename`
- `clean` -> `purge`

**Pattern:** Similar to pass-through but with command substitution:

```python
# cmd_blame.py
from common import ParsedCommand, run_sl

def handle(parsed: ParsedCommand) -> int:
    return run_sl(["annotate"] + parsed.args)  # blame -> annotate
```

**Complexity:** LOW - Same as pass-through
**Dependencies:** None
**Testing:** Verify correct sl command is called, args pass through

### Category 3: Subcommand Translation

**Command:** `stash` with subcommands `pop`, `list`, `drop`, `apply`

**Pattern:** Parse first argument to determine subcommand, translate to sl equivalents:

```python
# cmd_stash.py
from common import ParsedCommand, run_sl

STASH_SUBCOMMANDS = {
    "pop": "shelve --continue",     # or appropriate sl equivalent
    "list": "shelve --list",
    "drop": "shelve --delete",
    "apply": "shelve --apply",
    # default (no subcommand): "shelve"
}

def handle(parsed: ParsedCommand) -> int:
    if parsed.args and parsed.args[0] in STASH_SUBCOMMANDS:
        subcommand = parsed.args[0]
        remaining_args = parsed.args[1:]
        # Translate and execute
        ...
    else:
        # git stash (no subcommand) -> sl shelve
        return run_sl(["shelve"] + parsed.args)
```

**Complexity:** MEDIUM - Subcommand parsing, translation mapping
**Dependencies:** Research needed on sl shelve semantics
**Testing:** Each subcommand needs separate test cases

**Note:** Sapling uses `shelve` for stash-like functionality. Verify:
- `sl shelve` (save)
- `sl unshelve` (restore)
- `sl shelve --list` (list)
- `sl shelve --delete <name>` (drop)

### Category 4: Complex Disambiguation

**Command:** `checkout` - Can mean different things:

1. `git checkout <branch>` -> `sl goto <bookmark>`
2. `git checkout <file>` -> `sl revert <file>`
3. `git checkout -b <branch>` -> `sl bookmark <name> && sl goto <name>`

**Pattern:** Analyze arguments to determine intent:

```python
# cmd_checkout.py
from common import ParsedCommand, run_sl
import subprocess

def handle(parsed: ParsedCommand) -> int:
    # Case 1: -b flag (create and switch to new branch)
    if "-b" in parsed.args:
        return handle_create_branch(parsed)

    # Case 2: File path (revert file)
    # Need heuristic: is argument a file or a branch?
    if is_file_path(parsed.args):
        return handle_revert_files(parsed)

    # Case 3: Branch/bookmark name
    return handle_goto_branch(parsed)

def is_file_path(args):
    """Heuristic to detect file paths vs branch names."""
    # Check if args contain paths that exist on disk
    # Or use -- separator if present
    ...
```

**Complexity:** HIGH - Requires disambiguation logic
**Dependencies:** May need new utilities in `common.py`
**Testing:** Extensive - each use case needs coverage

**Disambiguation strategies:**
1. **Explicit separator:** `git checkout -- file.txt` (the `--` indicates paths follow)
2. **File existence check:** If argument is an existing file, treat as revert
3. **Fail-safe:** When ambiguous, prefer safer interpretation or error

### Category 5: Model Translation

**Command:** `branch` -> `bookmark`

Git branches are conceptually similar to Sapling bookmarks. Translation:

| Git Command | Sapling Equivalent |
|-------------|-------------------|
| `git branch` | `sl bookmark` (list) |
| `git branch <name>` | `sl bookmark <name>` |
| `git branch -d <name>` | `sl bookmark --delete <name>` |
| `git branch -D <name>` | `sl bookmark --delete --force <name>` |
| `git branch -m <old> <new>` | `sl bookmark --rename <old> <new>` |
| `git branch -a` | `sl bookmark --all` (or remote equivalent) |

```python
# cmd_branch.py
from common import ParsedCommand, run_sl

def handle(parsed: ParsedCommand) -> int:
    sl_args = ["bookmark"]

    # Translate flags
    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        if arg == "-d":
            sl_args.append("--delete")
        elif arg == "-D":
            sl_args.extend(["--delete", "--force"])
        elif arg == "-m":
            sl_args.append("--rename")
        elif arg == "-a":
            sl_args.append("--all")  # verify this exists
        else:
            sl_args.append(arg)

        i += 1

    return run_sl(sl_args)
```

**Complexity:** MEDIUM - Flag translation similar to `cmd_log.py`
**Dependencies:** Research sl bookmark flag semantics
**Testing:** Each flag combination needs coverage

---

## Suggested Build Order

### Phase 1: Pass-through Commands (Lowest Risk)

**Commands:** `show`, `clone`, `grep`, `config`

**Rationale:**
- Simplest pattern (Level 1 complexity)
- No argument translation needed
- Establishes rhythm for v1.2 development
- Provides quick wins to validate process

**Dependencies:** None
**Estimated effort:** 1 handler = 10-15 min each (with tests)

### Phase 2: Command Renames (Low Risk)

**Commands:** `blame`->`annotate`, `rm`->`remove`, `mv`->`rename`, `clean`->`purge`

**Rationale:**
- Same pattern as pass-through
- Only difference is command name substitution
- Still no argument translation

**Dependencies:** None (can parallelize with Phase 1)
**Estimated effort:** 1 handler = 10-15 min each (with tests)

### Phase 3: Model Translation - Branch (Medium Risk)

**Command:** `branch` -> `bookmark`

**Rationale:**
- Establishes flag translation pattern for more complex commands
- Well-defined flag mappings
- Single command to focus on before tackling more complex cases

**Dependencies:** Phases 1-2 (for pattern validation)
**Estimated effort:** 30-45 min (with comprehensive flag testing)

### Phase 4: Subcommand Translation - Stash (Medium Risk)

**Command:** `stash` with pop/list/drop/apply

**Rationale:**
- New pattern (subcommand parsing)
- Requires research into sl shelve behavior
- Contained complexity (clear subcommand boundaries)

**Dependencies:** Phase 3 (for flag translation patterns)
**Estimated effort:** 45-60 min (with research and testing)

### Phase 5: Complex Disambiguation - Checkout (Highest Risk)

**Command:** `checkout` (goto, revert, or bookmark+goto)

**Rationale:**
- Most complex command in v1.2
- Requires disambiguation heuristics
- May need new common.py utilities
- Save for last to benefit from all prior patterns

**Dependencies:** Phases 1-4 (all patterns established)
**Estimated effort:** 60-90 min (with extensive edge case testing)

### Dependency Graph

```
Phase 1: Pass-through (show, clone, grep, config)
    |
    v
Phase 2: Rename (blame, rm, mv, clean) [can parallelize with Phase 1]
    |
    v
Phase 3: Branch -> Bookmark
    |
    v
Phase 4: Stash -> Shelve
    |
    v
Phase 5: Checkout (disambiguation)
```

---

## Shared Utilities

### Recommended Additions to `common.py`

**1. Command Registry (Optional but Recommended)**

Replace if-chain dispatch with registry pattern:

```python
# common.py
from typing import Callable, Dict

# Type alias for handler functions
Handler = Callable[[ParsedCommand], int]

# Command registry
COMMAND_HANDLERS: Dict[str, Handler] = {}

def register_command(name: str):
    """Decorator to register a command handler."""
    def decorator(handler: Handler) -> Handler:
        COMMAND_HANDLERS[name] = handler
        return handler
    return decorator

def dispatch(parsed: ParsedCommand) -> int:
    """Dispatch to registered handler or return unsupported."""
    handler = COMMAND_HANDLERS.get(parsed.command)
    if handler:
        return handler(parsed)
    return handle_unsupported(parsed)
```

Usage in handlers:
```python
# cmd_show.py
from common import ParsedCommand, run_sl, register_command

@register_command("show")
def handle(parsed: ParsedCommand) -> int:
    return run_sl(["show"] + parsed.args)
```

**Benefits:**
- Eliminates 20+ if-statements in gitsl.py
- Self-documenting (handlers self-register)
- Easier to test (can inspect registry)

**Tradeoff:** More abstraction, slightly harder to trace code flow. Given current codebase is 7 commands going to 20+, the registry is justified.

**2. File vs Branch Detection Utility (for checkout)**

```python
# common.py
import os

def is_file_path(path: str, cwd: str = None) -> bool:
    """
    Check if argument looks like a file path.

    Returns True if:
    - Path exists on disk
    - Path contains directory separators
    - Previous argument was '--'
    """
    if cwd:
        full_path = os.path.join(cwd, path)
    else:
        full_path = path

    if os.path.exists(full_path):
        return True
    if '/' in path or '\\' in path:
        return True
    return False

def parse_checkout_args(args: List[str]) -> dict:
    """
    Parse checkout arguments to determine intent.

    Returns dict with:
    - mode: "create_branch" | "switch_branch" | "revert_files"
    - branch: branch name (if applicable)
    - files: file list (if applicable)
    - create_flag: -b or -B (if applicable)
    """
    ...
```

**3. Flag Translation Helper (for branch, stash, etc.)**

```python
# common.py
from typing import Dict, List, Tuple

def translate_flags(
    args: List[str],
    flag_map: Dict[str, str],
    value_flags: List[str] = None
) -> List[str]:
    """
    Translate git flags to sl flags.

    Args:
        args: Original git arguments
        flag_map: Mapping of git flag -> sl flag (e.g., {"-d": "--delete"})
        value_flags: Flags that take a value argument (e.g., ["-m"])

    Returns:
        Translated argument list
    """
    result = []
    value_flags = value_flags or []
    i = 0

    while i < len(args):
        arg = args[i]

        if arg in flag_map:
            translated = flag_map[arg]
            if isinstance(translated, list):
                result.extend(translated)  # e.g., -D -> ["--delete", "--force"]
            else:
                result.append(translated)
        else:
            result.append(arg)

        i += 1

    return result
```

---

## Component Boundaries

### Current Architecture

```
+-------------------+
|     gitsl.py      |  Entry point, dispatch
+--------+----------+
         |
         v
+--------+----------+
|    common.py      |  Shared utilities, ParsedCommand, run_sl
+--------+----------+
         |
    +----+----+----+----+----+----+----+
    |    |    |    |    |    |    |    |
    v    v    v    v    v    v    v    v
  cmd_  cmd_  cmd_  cmd_  cmd_  cmd_  cmd_
status log  diff  init  rev_  add commit
                        parse
```

### Proposed v1.2 Architecture

```
+-------------------+
|     gitsl.py      |  Entry point (simplified with registry)
+--------+----------+
         |
         v
+--------+----------+
|    common.py      |  ParsedCommand, run_sl, registry, utilities
+--------+----------+
         |
    +----+----+----+...+----+----+----+
    |    |    |       |    |    |    |
    v    v    v       v    v    v    v
  cmd_* (20+ handlers, each self-registering)
```

### File Responsibilities

| Component | Current | v1.2 Addition |
|-----------|---------|---------------|
| `gitsl.py` | Dispatch via if-chain | Dispatch via registry |
| `common.py` | ParsedCommand, run_sl, debug | + register_command, translate_flags, is_file_path |
| `cmd_*.py` | One per command | 13 new files following existing pattern |
| `pyproject.toml` | Lists 7 cmd_* modules | Lists 20 cmd_* modules |

---

## Testing Patterns

### Existing Test Structure (to follow)

Each command has a test file `test_<command>.py` with:

1. **Module-level markers:** Skip if sl not installed
2. **Test classes by feature:** `TestLogBasic`, `TestLogOneline`, `TestLogLimit`
3. **Fixtures from conftest:** `sl_repo`, `sl_repo_with_commit`, etc.
4. **Assertion pattern:** Check exit code, verify sl state changes

### New Test Requirements

**Category 1-2 (Pass-through, Rename):**
- Verify correct sl command called (use debug mode or mock)
- Verify exit code propagation
- Verify arguments pass through unchanged

**Category 3 (Branch):**
- Test each flag translation independently
- Test flag combinations
- Test error cases (delete non-existent branch, etc.)

**Category 4 (Stash):**
- Test each subcommand
- Test stash with no subcommand
- Verify shelve state changes

**Category 5 (Checkout):**
- Test `-b` branch creation
- Test file revert with existing file
- Test branch switch
- Test ambiguous cases (file named same as branch)
- Test `--` separator

---

## Pitfalls to Avoid

### 1. Checkout Ambiguity

**Risk:** `git checkout main` - is `main` a file or a branch?

**Mitigation:**
- Check file existence first
- Respect `--` separator
- When truly ambiguous, prefer branch (safer - doesn't modify files)
- Consider warning message for ambiguous cases

### 2. Stash/Shelve Semantic Differences

**Risk:** Git stash and Sapling shelve may not be 1:1 equivalent.

**Mitigation:**
- Research sl shelve thoroughly before implementing
- Document any behavioral differences
- Consider subset of stash functionality that maps cleanly

### 3. Branch/Bookmark Model Differences

**Risk:** Git branches and Sapling bookmarks have different semantics (e.g., git branches track commits, bookmarks are just pointers).

**Mitigation:**
- Focus on common use cases
- Document limitations in README
- Consider "close enough" translations

### 4. Growing Dispatch Complexity

**Risk:** 20+ if-statements in gitsl.py becomes unmaintainable.

**Mitigation:**
- Implement command registry pattern
- OR accept longer dispatch block (it's still just a switch statement)

### 5. pyproject.toml Module List

**Risk:** Forgetting to add new cmd_*.py to py-modules list.

**Mitigation:**
- Add to checklist for each new command
- Consider wildcard pattern if supported

---

## Sources

### Codebase Files Reviewed (HIGH Confidence)

| File | Lines | Key Insights |
|------|-------|--------------|
| `gitsl.py` | 93 | Entry point, dispatch pattern |
| `common.py` | 106 | ParsedCommand, run_sl, debug utilities |
| `cmd_status.py` | 110 | Output transformation pattern |
| `cmd_log.py` | 72 | Flag translation pattern |
| `cmd_add.py` | 78 | Multi-step operation pattern |
| `cmd_commit.py` | 13 | Pass-through pattern |
| `cmd_diff.py` | 13 | Pass-through pattern |
| `cmd_init.py` | 13 | Pass-through pattern |
| `cmd_rev_parse.py` | 33 | Subprocess with output capture |
| `tests/conftest.py` | 193 | Test fixtures, sl_repo patterns |
| `tests/test_log.py` | 163 | Test class organization |
| `tests/test_add.py` | 249 | Comprehensive flag testing |
| `pyproject.toml` | 52 | Module list, entry point config |

### Sapling Documentation (Research Needed)

For v1.2 implementation, verify these sl commands:
- `sl shelve` / `sl unshelve` semantics
- `sl bookmark` flag equivalents
- `sl goto` vs `sl checkout` (if different)
- `sl revert` for file restoration
