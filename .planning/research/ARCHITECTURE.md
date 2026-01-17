# Architecture Research: Git-to-Sapling CLI Shim

**Domain:** CLI Command Translation / VCS Wrapper
**Researched:** 2026-01-17
**Confidence:** HIGH (patterns well-established in CLI/subprocess domains)

## Executive Summary

A git-to-Sapling CLI shim follows a **pipeline architecture** with four distinct stages: Parse, Translate, Execute, Transform. Within a single-file constraint, this maps to clearly separated functions organized by responsibility. The dictionary dispatch pattern is ideal for command translation, providing O(1) lookup and maintainable command mappings.

---

## Component Structure

Given the single-file constraint, organize the script into logical sections using comments and function groupings.

### Recommended File Layout

```python
#!/usr/bin/env python3
"""
Git-to-Sapling CLI Shim
Translates git commands to their Sapling (sl) equivalents.
"""

# ============================================================
# SECTION 1: IMPORTS AND CONSTANTS
# ============================================================

import sys
import subprocess
import shlex
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable

# ============================================================
# SECTION 2: DATA STRUCTURES
# ============================================================

@dataclass
class ParsedCommand:
    """Parsed representation of a git command."""
    command: str              # e.g., "commit", "push", "status"
    subcommand: Optional[str] # e.g., for "git remote add"
    flags: Dict[str, str]     # e.g., {"--message": "msg", "-a": None}
    positional_args: List[str]
    raw_args: List[str]       # original argv for passthrough

@dataclass
class TranslatedCommand:
    """Translated Sapling command ready for execution."""
    executable: str           # "sl"
    command: str              # e.g., "commit", "goto", "amend"
    args: List[str]           # all arguments
    needs_output_transform: bool
    transform_type: Optional[str]

@dataclass
class ExecutionResult:
    """Result from executing a command."""
    exit_code: int
    stdout: str
    stderr: str

# ============================================================
# SECTION 3: COMMAND TRANSLATION TABLES
# ============================================================

# Direct 1:1 command mappings
DIRECT_COMMAND_MAP: Dict[str, str] = {
    "clone": "clone",
    "status": "status",
    "diff": "diff",
    "log": "log",
    "add": "add",
    "rm": "rm",
    "mv": "mv",
    "blame": "blame",
    "show": "show",
    # ... more mappings
}

# Commands requiring special translation logic
COMPLEX_COMMANDS: Dict[str, Callable] = {
    "commit": translate_commit,
    "push": translate_push,
    "pull": translate_pull,
    "checkout": translate_checkout,
    "reset": translate_reset,
    "rebase": translate_rebase,
    "stash": translate_stash,
    "branch": translate_branch,
    # ... more complex handlers
}

# Flag translation per command
FLAG_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "commit": {
        "-m": "-m",
        "--message": "-m",
        "-a": "",  # Sapling commits all by default
        "--amend": "",  # handled specially
    },
    # ... more flag mappings
}

# ============================================================
# SECTION 4: PARSING FUNCTIONS
# ============================================================

def parse_argv(argv: List[str]) -> ParsedCommand: ...
def extract_command(args: List[str]) -> tuple[str, List[str]]: ...
def parse_flags(args: List[str]) -> tuple[Dict[str, str], List[str]]: ...

# ============================================================
# SECTION 5: TRANSLATION FUNCTIONS
# ============================================================

def translate_command(parsed: ParsedCommand) -> TranslatedCommand: ...
def translate_commit(parsed: ParsedCommand) -> TranslatedCommand: ...
def translate_push(parsed: ParsedCommand) -> TranslatedCommand: ...
def translate_checkout(parsed: ParsedCommand) -> TranslatedCommand: ...
# ... other complex translators

# ============================================================
# SECTION 6: EXECUTION FUNCTIONS
# ============================================================

def execute_command(translated: TranslatedCommand) -> ExecutionResult: ...
def run_sl_command(args: List[str]) -> ExecutionResult: ...

# ============================================================
# SECTION 7: OUTPUT TRANSFORMATION
# ============================================================

def transform_output(result: ExecutionResult, transform_type: str) -> str: ...
def transform_branch_output(output: str) -> str: ...
def transform_log_output(output: str) -> str: ...

# ============================================================
# SECTION 8: ERROR HANDLING
# ============================================================

def handle_unknown_command(command: str, args: List[str]) -> int: ...
def handle_execution_error(result: ExecutionResult) -> int: ...

# ============================================================
# SECTION 9: MAIN ENTRY POINT
# ============================================================

def main(argv: List[str] = None) -> int: ...

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

### Component Responsibilities

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| **Data Structures** | Define ParsedCommand, TranslatedCommand, ExecutionResult | None |
| **Translation Tables** | Map git commands/flags to Sapling equivalents | Data Structures |
| **Parsing Functions** | Convert argv into ParsedCommand | Data Structures |
| **Translation Functions** | Convert ParsedCommand to TranslatedCommand | Tables, Data Structures |
| **Execution Functions** | Run Sapling commands via subprocess | TranslatedCommand |
| **Output Transformation** | Convert Sapling output to git-like format | ExecutionResult |
| **Error Handling** | Graceful degradation, helpful messages | All |
| **Main** | Orchestrate pipeline | All |

---

## Data Flow

### High-Level Pipeline

```
sys.argv
    |
    v
+-------------------+
|   parse_argv()    |  Stage 1: PARSE
|                   |  - Extract command name
|                   |  - Parse flags and arguments
|                   |  - Return ParsedCommand
+-------------------+
    |
    v
+-------------------+
| translate_command |  Stage 2: TRANSLATE
|                   |  - Lookup command in tables
|                   |  - Apply flag translations
|                   |  - Handle complex commands
|                   |  - Return TranslatedCommand
+-------------------+
    |
    v
+-------------------+
| execute_command() |  Stage 3: EXECUTE
|                   |  - Build sl command line
|                   |  - Run subprocess
|                   |  - Capture output
|                   |  - Return ExecutionResult
+-------------------+
    |
    v
+-------------------+
| transform_output()|  Stage 4: TRANSFORM (optional)
|                   |  - Convert Sapling output
|                   |  - Match git output format
|                   |  - Print to stdout/stderr
+-------------------+
    |
    v
sys.exit(code)
```

### Detailed Data Flow Example

**Input:** `git commit -am "Fix bug"`

```
1. PARSE
   argv = ["commit", "-am", "Fix bug"]

   ParsedCommand(
       command="commit",
       subcommand=None,
       flags={"-a": None, "-m": "Fix bug"},
       positional_args=[],
       raw_args=["commit", "-am", "Fix bug"]
   )

2. TRANSLATE
   - "commit" found in COMPLEX_COMMANDS
   - translate_commit() called
   - Sapling commits all tracked changes by default (no -a needed)
   - -m maps to -m
   - "--amend" not present, so use "commit" not "amend"

   TranslatedCommand(
       executable="sl",
       command="commit",
       args=["-m", "Fix bug"],
       needs_output_transform=False,
       transform_type=None
   )

3. EXECUTE
   subprocess.run(["sl", "commit", "-m", "Fix bug"], ...)

   ExecutionResult(
       exit_code=0,
       stdout="",
       stderr=""
   )

4. OUTPUT (passthrough - no transformation needed)
   Print stdout/stderr as-is
   Exit with code 0
```

### Decision Points in Pipeline

```
                    Is command known?
                          |
              +-----------+-----------+
              |                       |
             YES                      NO
              |                       |
     Is it in DIRECT_MAP?      Passthrough to sl?
              |                       |
      +-------+-------+        +------+------+
      |               |        |             |
     YES              NO      YES            NO
      |               |        |             |
  Simple map    Complex     Execute      Error msg
  to Sapling    handler     `sl <cmd>`   + exit 1
```

---

## Build Order

### Phase 1: Core Pipeline (MVP)

Implement the minimal viable pipeline first.

**Order:**
1. **Data structures** - Define the dataclasses
2. **Main entry point skeleton** - Basic argv handling
3. **Simple command table** - DIRECT_COMMAND_MAP with 5-10 common commands
4. **Basic parser** - Extract command name, pass remaining args
5. **Basic executor** - subprocess.run with output capture
6. **Passthrough for unknowns** - Forward unknown commands to sl

**Result:** Working shim for simple commands like `git status`, `git diff`, `git log`

### Phase 2: Flag Translation

Add flag handling for commands that need it.

**Order:**
1. **Flag parsing** - Parse `-x`, `--flag`, `--flag=value`
2. **Flag translation table** - Per-command flag mappings
3. **First complex handler** - `commit` (most common)
4. **Second complex handler** - `checkout` (maps to `goto`)

**Result:** Handle `git commit -am "msg"`, `git checkout branch`

### Phase 3: Complex Commands

Handle commands with significant behavioral differences.

**Order:**
1. **push translation** - `git push` -> `sl push --to`
2. **pull translation** - `git pull` -> `sl pull`
3. **reset translation** - Different semantics
4. **stash translation** - `stash` -> `shelve`
5. **branch translation** - `branch` -> `bookmark`

**Result:** Comprehensive git workflow support

### Phase 4: Output Transformation

Make output look git-like where needed.

**Order:**
1. **Output transformer registry**
2. **Branch output transformer** - If output differs significantly
3. **Log output transformer** - If needed for scripts

**Result:** Drop-in git replacement for most workflows

### Dependency Graph

```
Data Structures ─────────────────────────┐
      │                                  │
      v                                  │
Translation Tables ──────────────────────┤
      │                                  │
      v                                  │
Parser ──────────────────────────────────┤
      │                                  │
      v                                  │
Translator ──────────────────────────────┤
      │                                  │
      v                                  │
Executor ────────────────────────────────┤
      │                                  │
      v                                  │
Output Transformer ──────────────────────┤
      │                                  │
      v                                  │
Main ────────────────────────────────────┘
```

---

## Error Handling Strategy

### Error Categories

| Category | Example | Strategy |
|----------|---------|----------|
| **Unknown command** | `git foo` | Attempt passthrough to `sl foo`, report if fails |
| **Parse error** | Malformed flags | Show usage hint, exit 1 |
| **Translation error** | Unsupported flag combo | Warn, attempt best-effort translation |
| **Execution error** | `sl` command fails | Pass through exit code and output |
| **Environment error** | `sl` not installed | Clear error message, exit 127 |

### Implementation Pattern

```python
def main(argv: List[str] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Handle no-args case
    if not argv:
        return show_help()

    try:
        # Stage 1: Parse
        parsed = parse_argv(argv)
    except ParseError as e:
        print(f"git: {e}", file=sys.stderr)
        return 1

    try:
        # Stage 2: Translate
        translated = translate_command(parsed)
    except UnsupportedCommandError as e:
        return attempt_passthrough(parsed)
    except TranslationError as e:
        print(f"git: translation error: {e}", file=sys.stderr)
        return 1

    try:
        # Stage 3: Execute
        result = execute_command(translated)
    except FileNotFoundError:
        print("git: 'sl' not found. Is Sapling installed?", file=sys.stderr)
        return 127
    except subprocess.SubprocessError as e:
        print(f"git: execution error: {e}", file=sys.stderr)
        return 1

    # Stage 4: Output
    if translated.needs_output_transform:
        output = transform_output(result, translated.transform_type)
        print(output)
    else:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

    return result.exit_code
```

### Passthrough Strategy

For unrecognized commands, attempt transparent passthrough:

```python
def attempt_passthrough(parsed: ParsedCommand) -> int:
    """Try to run command directly with sl."""
    try:
        result = subprocess.run(
            ["sl"] + parsed.raw_args,
            capture_output=False  # Stream directly to terminal
        )
        return result.returncode
    except FileNotFoundError:
        print(f"git: '{parsed.command}' is not a git command.", file=sys.stderr)
        return 1
```

### Exit Code Preservation

**Critical:** Preserve Sapling's exit codes for script compatibility.

```python
def execute_command(translated: TranslatedCommand) -> ExecutionResult:
    cmd = [translated.executable, translated.command] + translated.args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return ExecutionResult(
        exit_code=result.returncode,  # Preserve!
        stdout=result.stdout,
        stderr=result.stderr
    )
```

---

## Key Design Decisions

### 1. Dictionary Dispatch over argparse

**Recommendation:** Use dictionary dispatch, not argparse subparsers.

**Why:**
- Git command syntax is not standard argparse (git allows `commit -am "msg"`)
- Need flexible passthrough for unknown commands
- Translation logic is simpler with lookup tables
- argparse subparsers would require defining every command upfront

**Pattern:**
```python
def translate_command(parsed: ParsedCommand) -> TranslatedCommand:
    cmd = parsed.command

    # Check direct mapping first (O(1))
    if cmd in DIRECT_COMMAND_MAP:
        return TranslatedCommand(
            executable="sl",
            command=DIRECT_COMMAND_MAP[cmd],
            args=parsed.raw_args[1:],  # Pass remaining args
            needs_output_transform=False,
            transform_type=None
        )

    # Check complex handlers
    if cmd in COMPLEX_COMMANDS:
        return COMPLEX_COMMANDS[cmd](parsed)

    # Unknown - mark for passthrough attempt
    raise UnsupportedCommandError(cmd)
```

### 2. Dataclasses for Structure

**Recommendation:** Use `@dataclass` for ParsedCommand, TranslatedCommand, ExecutionResult.

**Why:**
- Self-documenting structure
- Type hints for IDE support
- No external dependencies (Python 3.7+)
- Immutable-by-default behavior with `frozen=True`

### 3. subprocess.run() for Execution

**Recommendation:** Use `subprocess.run()` with `capture_output=True` for most commands.

**Why:**
- Modern Python standard (3.5+)
- Clean API for output capture
- Built-in timeout support
- Easy exit code access

**Exception:** For long-running commands or when streaming is needed, use `subprocess.Popen()` with line-by-line reading.

### 4. Minimal Output Transformation

**Recommendation:** Only transform output when necessary for compatibility.

**Why:**
- Most Sapling output is already similar to git
- Transformation adds complexity and maintenance
- Passthrough is faster and less error-prone

**Transform only when:**
- Scripts depend on specific git output format
- Branch/bookmark output differs significantly
- Error messages need translation

---

## Sapling Command Mapping Reference

Based on [Sapling's Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/):

### Direct Mappings (Same Command, Same Args)

| Git | Sapling | Notes |
|-----|---------|-------|
| `git clone` | `sl clone` | Direct |
| `git status` | `sl status` | Direct |
| `git diff` | `sl diff` | Direct |
| `git log` | `sl log` | Direct |
| `git add FILE` | `sl add FILE` | Direct |
| `git rm FILE` | `sl rm FILE` | Direct |
| `git mv OLD NEW` | `sl mv OLD NEW` | Direct |
| `git blame FILE` | `sl blame FILE` | Direct |
| `git show` | `sl show` | Direct |

### Semantic Mappings (Different Command)

| Git | Sapling | Notes |
|-----|---------|-------|
| `git checkout COMMIT` | `sl goto COMMIT` | Different verb |
| `git checkout -- FILE` | `sl revert FILE` | Different command |
| `git branch` | `sl bookmark` | Different concept |
| `git stash` | `sl shelve` | Different verb |
| `git stash pop` | `sl unshelve` | Different verb |
| `git cherry-pick` | `sl graft` | Different verb |
| `git reflog` | `sl journal` | Different verb |

### Flag Translations

| Git | Sapling | Notes |
|-----|---------|-------|
| `git commit -a` | `sl commit` | Sapling commits all tracked by default |
| `git commit --amend` | `sl amend` | Separate command |
| `git reset --soft HEAD^` | `sl uncommit` | Separate command |
| `git reset --hard` | `sl revert --all` | Different flags |
| `git add -A .` | `sl addremove` | Separate command |
| `git push HEAD:BRANCH` | `sl push --to BRANCH` | Different syntax |

### Complex Behaviors

| Git | Sapling | Complexity |
|-----|---------|------------|
| `git rebase -i` | `sl histedit` | Different interactive model |
| `git add -p` | `sl commit -i` | Part of commit, not add |
| `git fetch origin REFSPEC` | `sl pull -B BRANCH` | Different semantics |

---

## Sources

### Primary (HIGH Confidence)
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Official command mappings
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html) - Standard library reference
- [GeeksforGeeks: Executing Shell Commands](https://www.geeksforgeeks.org/python/executing-shell-commands-with-python/) - subprocess patterns

### Secondary (MEDIUM Confidence)
- [Hacker News: Dictionary Dispatch Pattern](https://news.ycombinator.com/item?id=37271162) - Community patterns discussion
- [GitHub Gist: argparse subparsers](https://gist.github.com/amarao/36327a6f77b86b90c2bca72ba03c9d3a) - Subparser examples
- [dev.to: g wrapper tool](https://dev.to/pcdevil/g-a-wrapper-around-git-with-additional-feature-extension-3m11) - Wrapper architecture example
- [GeeksforGeeks: Retrieving subprocess output](https://www.geeksforgeeks.org/python/retrieving-the-output-of-subprocesscall-in-python/) - Output capture patterns
