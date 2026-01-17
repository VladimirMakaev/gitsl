# Phase 1 Research: Script Skeleton

**Researched:** 2026-01-17
**Domain:** Python CLI argument parsing and debug mode
**Confidence:** HIGH

## Summary

Phase 1 establishes the foundational script structure for parsing git-style command line arguments without executing anything. The key insight is that git-style CLIs have a specific structure (`git <command> [<args>]`) that is simpler to parse manually than with argparse.

The standard approach is:
1. Extract the command (first positional argument after the script name)
2. Preserve remaining arguments for later translation
3. Handle debug mode via environment variable or flag
4. Structure the script with a clean `main()` entry point that returns exit codes

**Primary recommendation:** Use manual two-phase parsing (extract command, then pass remaining args) rather than argparse. Implement debug mode via `GITSL_DEBUG` environment variable.

## Standard Stack

### Core (stdlib only)

| Module | Purpose | Why Standard |
|--------|---------|--------------|
| `sys` | `sys.argv` access, `sys.exit()` for exit codes | Required for CLI arg handling |
| `os` | `os.environ` for debug mode detection | Required for env var access |
| `shlex` | `shlex.join()` for safe command display | Python 3.8+, safe shell quoting |

### Not Needed

| Module | Why Avoid |
|--------|-----------|
| `argparse` | Git-style args have quirks argparse handles poorly (dash-prefixed values, passthrough) |
| `click`, `typer` | External dependencies, violates "stdlib only" constraint |
| `getopt` | Deprecated, less readable than manual parsing |

## Architecture Patterns

### Recommended Script Structure

```
gitsl.py
  - Constants (VERSION, DEBUG detection)
  - ParsedCommand dataclass (or NamedTuple)
  - parse_argv() function
  - format_command_for_display() function
  - main() function
  - if __name__ == "__main__" guard
```

### Pattern 1: Two-Phase Command Extraction

**What:** Extract the git command first, then preserve remaining args.

**When to use:** Always for git-style CLIs.

**Example:**
```python
# Source: Python sys.argv documentation + project ARCHITECTURE.md
import sys
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    """Parsed representation of a git command."""
    command: Optional[str]    # e.g., "commit", "status", None if empty
    args: List[str]           # remaining arguments after command
    raw_argv: List[str]       # original argv for debugging

def parse_argv(argv: List[str]) -> ParsedCommand:
    """
    Parse git-style arguments.

    Examples:
        [] -> ParsedCommand(command=None, args=[], raw_argv=[])
        ["status"] -> ParsedCommand(command="status", args=[], raw_argv=["status"])
        ["commit", "-m", "msg"] -> ParsedCommand(command="commit", args=["-m", "msg"], raw_argv=...)
    """
    if not argv:
        return ParsedCommand(command=None, args=[], raw_argv=[])

    command = argv[0]
    args = argv[1:]
    return ParsedCommand(command=command, args=args, raw_argv=argv)
```

### Pattern 2: Debug Mode via Environment Variable

**What:** Check environment variable for debug mode, not a command-line flag.

**When to use:** For shim/wrapper scripts where you cannot consume args.

**Why env var over flag:**
- Flags would be consumed by the shim, not passed through
- `--debug` as a flag would conflict with potential git flags
- Env var is invisible to the underlying command translation
- Matches how git uses `GIT_TRACE` for debugging

**Example:**
```python
# Source: Python os.environ documentation + dagster best practices
import os

def is_debug_mode() -> bool:
    """Check if debug mode is enabled via environment variable."""
    debug_val = os.environ.get("GITSL_DEBUG", "").lower()
    return debug_val in ("1", "true", "yes", "on")
```

### Pattern 3: Main Entry Point with Exit Code

**What:** Use `main()` function that returns int, guard with `if __name__`.

**When to use:** Always.

**Example:**
```python
# Source: Python __main__ documentation
import sys

def main(argv: List[str] = None) -> int:
    """Main entry point. Returns exit code."""
    if argv is None:
        argv = sys.argv[1:]

    parsed = parse_argv(argv)

    if is_debug_mode():
        print_debug_info(parsed)
        return 0

    # Later phases: translate and execute
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Pattern 4: Safe Command Display with shlex.join()

**What:** Use `shlex.join()` to safely format commands for display.

**When to use:** Debug output, error messages showing what would run.

**Example:**
```python
# Source: Python shlex documentation
import shlex

def format_command(args: List[str]) -> str:
    """Format a command list for human-readable display."""
    # shlex.join() is Python 3.8+, handles quoting properly
    return shlex.join(args)

# Example output: "sl commit -m 'my message'"
```

### Anti-Patterns to Avoid

- **Using argparse:** Git has dash-prefixed values (`git commit -m "-WIP-"`) that argparse mishandles. Also, subparsers cause ambiguity issues.
- **Consuming flags for debug:** Don't use `--debug` as a flag. It would be consumed by the shim, not passed through, and could conflict with git flags.
- **Reconstructing args with string concatenation:** Use `shlex.join()`, not `" ".join(args)` which breaks on spaces.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Shell quoting | String concatenation | `shlex.join()` | Handles spaces, quotes, special chars |
| Env var parsing | Custom parsing | `os.environ.get()` with default | Standard pattern, handles missing |
| Exit code handling | Try/except that loses code | Return int from `main()` | Proper propagation |

## Common Pitfalls

### Pitfall 1: Empty Argument Handling

**What goes wrong:** Script crashes or behaves unexpectedly with no arguments.

**Why it happens:** Accessing `argv[0]` without checking length.

**How to avoid:** Check for empty argv before extracting command.

**Warning signs:** IndexError on `git` with no arguments.

### Pitfall 2: Argv[0] Confusion

**What goes wrong:** Including script name in parsed arguments.

**Why it happens:** `sys.argv[0]` is the script name, not the first argument.

**How to avoid:** Pass `sys.argv[1:]` to main(), not `sys.argv`.

**Warning signs:** First argument is always the script path.

### Pitfall 3: Environment Variable Case Sensitivity

**What goes wrong:** `GITSL_DEBUG=true` works but `GITSL_DEBUG=True` doesn't.

**Why it happens:** String comparison without normalization.

**How to avoid:** Use `.lower()` before comparing: `val.lower() in ("1", "true", "yes", "on")`.

**Warning signs:** Inconsistent debug behavior across terminals.

### Pitfall 4: Return Value from main()

**What goes wrong:** Script always exits 0 even when it should fail.

**Why it happens:** Missing return statement or exception handling swallowing errors.

**How to avoid:** Always `return` explicit int from main(), use `sys.exit(main())`.

**Warning signs:** CI passes when it should fail.

## Code Examples

### Complete Minimal Script Skeleton

```python
#!/usr/bin/env python3
"""
gitsl - Git to Sapling CLI shim.

Translates git commands to their Sapling (sl) equivalents.
Set GITSL_DEBUG=1 to see what would be executed without running.
"""

import os
import shlex
import sys
from dataclasses import dataclass
from typing import List, Optional


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1.0"


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class ParsedCommand:
    """Parsed representation of a git command."""
    command: Optional[str]    # e.g., "commit", "status", None if empty
    args: List[str]           # remaining arguments after command
    raw_argv: List[str]       # original argv for debugging


# ============================================================
# PARSING
# ============================================================

def parse_argv(argv: List[str]) -> ParsedCommand:
    """
    Parse git-style arguments.

    Args:
        argv: Command line arguments (without script name, i.e., sys.argv[1:])

    Returns:
        ParsedCommand with extracted command and remaining args
    """
    if not argv:
        return ParsedCommand(command=None, args=[], raw_argv=[])

    command = argv[0]
    args = argv[1:]
    return ParsedCommand(command=command, args=args, raw_argv=argv)


# ============================================================
# DEBUG MODE
# ============================================================

def is_debug_mode() -> bool:
    """Check if debug mode is enabled via GITSL_DEBUG environment variable."""
    debug_val = os.environ.get("GITSL_DEBUG", "").lower()
    return debug_val in ("1", "true", "yes", "on")


def print_debug_info(parsed: ParsedCommand) -> None:
    """Print debug information about the parsed command."""
    print(f"[DEBUG] Command: {parsed.command}", file=sys.stderr)
    print(f"[DEBUG] Args: {parsed.args}", file=sys.stderr)

    # Show what would be executed (placeholder for Phase 1)
    if parsed.command:
        would_execute = ["sl", parsed.command] + parsed.args
        print(f"[DEBUG] Would execute: {shlex.join(would_execute)}", file=sys.stderr)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main(argv: List[str] = None) -> int:
    """
    Main entry point for gitsl.

    Args:
        argv: Command line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if argv is None:
        argv = sys.argv[1:]

    parsed = parse_argv(argv)

    # Handle empty command
    if parsed.command is None:
        print("usage: git <command> [<args>]", file=sys.stderr)
        return 1

    # Handle special flags
    if parsed.command in ("--version", "-v"):
        print(f"gitsl version {VERSION}")
        return 0

    if parsed.command in ("--help", "-h", "help"):
        print("usage: git <command> [<args>]")
        print("\nThis is gitsl, a git-to-Sapling translation shim.")
        print("Set GITSL_DEBUG=1 to see commands without executing.")
        return 0

    # Debug mode: show what would run, don't execute
    if is_debug_mode():
        print_debug_info(parsed)
        return 0

    # Future phases: translate and execute command
    # For Phase 1, just acknowledge the command
    print(f"[STUB] Would process: git {parsed.command}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Testing Argv Parsing

```python
# Example test cases for parse_argv
def test_parse_argv():
    # Empty args
    result = parse_argv([])
    assert result.command is None
    assert result.args == []

    # Single command
    result = parse_argv(["status"])
    assert result.command == "status"
    assert result.args == []

    # Command with args
    result = parse_argv(["commit", "-m", "message"])
    assert result.command == "commit"
    assert result.args == ["-m", "message"]

    # Command with complex args
    result = parse_argv(["log", "--oneline", "-5"])
    assert result.command == "log"
    assert result.args == ["--oneline", "-5"]
```

## Edge Cases

| Case | Input | Expected Behavior |
|------|-------|-------------------|
| No arguments | `git` | Show usage, exit 1 |
| Help flag | `git --help` or `git help` | Show help, exit 0 |
| Version flag | `git --version` | Show version, exit 0 |
| Unknown command | `git foobar` | Pass through (later phases), exit depends on sl |
| Debug + command | `GITSL_DEBUG=1 git status` | Show debug info, exit 0 |
| Args with spaces | `git commit -m "multi word"` | Preserve as single arg |
| Args with dashes | `git commit -m "-WIP-"` | Preserve literal (works with manual parse) |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `optparse` | `argparse` or manual | Python 2.7 deprecation | Use manual for git-style |
| String join for display | `shlex.join()` | Python 3.8 | Safe quoting built-in |
| Multiple env var patterns | `os.environ.get()` | Always preferred | Consistent, handles missing |

## Open Questions

1. **Help text content:** What should `git help` display? For Phase 1, minimal placeholder is fine. Later phases may want to list supported commands.

2. **Unknown command in debug mode:** Should debug mode show "[UNKNOWN]" for unrecognized commands, or just show what would be attempted? Recommend showing the translation (sl command) when known, stub when not.

## Sources

### Primary (HIGH confidence)
- [Python sys.argv documentation](https://docs.python.org/3/library/sys.html) - Official stdlib reference
- [Python __main__ documentation](https://docs.python.org/3/library/__main__.html) - Entry point best practices
- [Python shlex documentation](https://docs.python.org/3/library/shlex.html) - Safe shell quoting

### Secondary (MEDIUM confidence)
- [Dagster Python Environment Variables Best Practices](https://dagster.io/blog/python-environment-variables) - Env var patterns

### Project Prior Art (HIGH confidence)
- `.planning/research/ARCHITECTURE.md` - Recommends dictionary dispatch, two-phase parsing
- `.planning/research/PITFALLS.md` - Documents argparse issues to avoid

## Metadata

**Confidence breakdown:**
- Argv parsing: HIGH - Official Python docs, simple pattern
- Debug mode: HIGH - Standard env var pattern
- Entry point: HIGH - Official Python docs
- shlex usage: HIGH - Official Python docs, Python 3.8+ confirmed

**Research date:** 2026-01-17
**Valid until:** 90 days (stable stdlib patterns)
