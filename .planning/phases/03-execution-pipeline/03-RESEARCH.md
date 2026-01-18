# Phase 3: Execution Pipeline - Research

**Researched:** 2026-01-18
**Domain:** Python subprocess management, CLI architecture, signal handling
**Confidence:** HIGH

## Summary

Phase 3 transforms gitsl from a stub that prints "[STUB] Would process" into a real execution pipeline that runs Sapling commands via subprocess and faithfully relays all I/O and exit codes to the caller. This requires:

1. **Multi-file architecture refactoring:** Moving shared logic to `common.py`, creating `cmd_*.py` pattern for command handlers, keeping `gitsl.py` as entry-point-only
2. **Subprocess execution:** Using Python's `subprocess.run()` with default I/O inheritance for real-time passthrough
3. **Exit code propagation:** Returning subprocess's returncode via `sys.exit()`
4. **Signal handling:** Leveraging process group inheritance so Ctrl+C terminates both parent and child cleanly

**Primary recommendation:** Use `subprocess.run()` with `stdin=None, stdout=None, stderr=None` (all defaults) to inherit parent's file descriptors. This provides real-time I/O passthrough without buffering, avoids deadlocks, and correctly propagates signals. Exit code propagates via `sys.exit(result.returncode)`.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute external commands | Python's official process management module |
| importlib | stdlib | Dynamic module loading | Recommended for programmatic imports (replaces deprecated `imp`) |
| sys | stdlib | Exit code propagation | `sys.exit(returncode)` is the standard pattern |
| signal | stdlib | Signal handling (if needed) | Standard for SIGINT/SIGTERM handling |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shlex | stdlib | Command quoting for debug output | Display "would execute" in debug mode |
| os | stdlib | Environment variable access | GITSL_DEBUG checking |
| typing | stdlib | Type hints | Function signatures |
| dataclasses | stdlib | Data structures | ParsedCommand and similar |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| subprocess.run() | subprocess.Popen() | Popen offers more control but run() is simpler for our passthrough use case |
| Dynamic imports | Static imports | Dynamic allows adding commands without modifying dispatch; static is simpler but requires touching entry point for each command |
| Dictionary dispatch | Match statement | Dictionary is more extensible; match requires Python 3.10+ and hardcoded cases |

**Installation:**
```bash
# No installation needed - all stdlib
```

## Architecture Patterns

### Recommended Project Structure
```
gitsl/
├── gitsl.py           # Entry point ONLY: parse argv, dispatch to handlers, exit
├── common.py          # Shared utilities: parsing, subprocess runner, debug mode
├── cmd_status.py      # Handler for 'status' command
├── cmd_commit.py      # Handler for 'commit' command
├── cmd_log.py         # Handler for 'log' command
└── tests/
    ├── conftest.py
    ├── helpers/
    └── test_*.py
```

### Pattern 1: Entry Point Dispatch (Dictionary-Based)
**What:** Entry point contains ONLY: argument parsing, command lookup, dispatch, exit
**When to use:** Always for gitsl.py to satisfy ARCH-01

**Example:**
```python
# Source: Official Python subprocess documentation pattern
# gitsl.py - Entry point only

import sys
from common import parse_argv, is_debug_mode, print_debug_info

# Command registry - maps command names to handler modules
COMMAND_HANDLERS = {
    "status": "cmd_status",
    "commit": "cmd_commit",
    "log": "cmd_log",
    "diff": "cmd_diff",
    "add": "cmd_add",
    "init": "cmd_init",
}

def main(argv: list[str] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parsed = parse_argv(argv)

    # Handle special flags (--version, --help)
    if parsed.command in ("--version", "-v"):
        print(f"gitsl version {VERSION}")
        return 0

    if parsed.command in ("--help", "-h", "help"):
        print("usage: git <command> [<args>]")
        return 0

    # Debug mode
    if is_debug_mode():
        print_debug_info(parsed)
        return 0

    # Dispatch to handler
    if parsed.command in COMMAND_HANDLERS:
        handler = get_handler(parsed.command)
        return handler(parsed)

    # Unknown command - will be handled in Phase 9
    return handle_unknown(parsed)

if __name__ == "__main__":
    sys.exit(main())
```

### Pattern 2: Command Handler Interface
**What:** Each cmd_*.py exports a `handle(parsed: ParsedCommand) -> int` function
**When to use:** All command handler files

**Example:**
```python
# Source: Standard Python CLI pattern
# cmd_status.py

from common import run_sl, ParsedCommand

def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git status' command.

    Translates to 'sl status' and passes through all arguments.
    """
    return run_sl(["status"] + parsed.args)
```

### Pattern 3: Subprocess Passthrough (No Capture)
**What:** Use subprocess.run() with default None for stdin/stdout/stderr
**When to use:** Executing sl commands where output should go directly to terminal

**Example:**
```python
# Source: Python subprocess documentation
# https://docs.python.org/3/library/subprocess.html
# common.py

import subprocess
import sys
from typing import List

def run_sl(args: List[str]) -> int:
    """
    Execute sl command with passthrough I/O.

    Args:
        args: Arguments to pass to sl (command and flags)

    Returns:
        Exit code from sl process
    """
    # stdin=None, stdout=None, stderr=None (defaults)
    # means child inherits parent's file descriptors
    # - stdout appears on caller's stdout in real-time
    # - stderr appears on caller's stderr in real-time
    # - stdin can receive input (for interactive commands)
    result = subprocess.run(["sl"] + args)
    return result.returncode
```

### Pattern 4: Dynamic Command Loading (Optional)
**What:** Load command handlers dynamically using importlib
**When to use:** When you want to add commands without modifying dispatch table

**Example:**
```python
# Source: Python importlib documentation
# https://docs.python.org/3/library/importlib.html

import importlib

def get_handler(command: str):
    """Dynamically load handler for command."""
    module_name = f"cmd_{command}"
    try:
        module = importlib.import_module(module_name)
        return module.handle
    except ImportError:
        return None
```

### Anti-Patterns to Avoid

- **Capturing output when not needed:** Using `capture_output=True` or `stdout=PIPE` when you just want passthrough. This causes buffering and breaks real-time display.

- **Using communicate() for passthrough:** `communicate()` is for when you need to capture output. For passthrough, just let subprocess.run() complete.

- **Hardcoding exit codes:** Don't `return 1` on failure. Always propagate subprocess's actual returncode.

- **Ignoring signals:** Don't catch KeyboardInterrupt and hide it. Let it propagate naturally.

- **Putting logic in entry point:** gitsl.py should ONLY dispatch. Translation logic, flag handling, output formatting all belong in handlers or common.py.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Process execution | os.system(), manual fork | subprocess.run() | subprocess handles quoting, encoding, signals correctly |
| Output streaming | Line-by-line readline loop | subprocess.run() with default I/O | Passthrough is automatic when you don't capture |
| Exit code handling | Custom error codes | subprocess returncode | sl's exit codes are meaningful; preserve them |
| Signal forwarding | Manual signal handlers | Process group inheritance | When stdin/stdout/stderr=None, child is in same process group and receives SIGINT directly |
| Module loading | __import__ | importlib.import_module() | importlib is the modern, documented approach |

**Key insight:** The subprocess module with default settings does almost everything we need. The mistake would be adding complexity (PIPE, communicate, signal handlers) when the default passthrough behavior is exactly what we want.

## Common Pitfalls

### Pitfall 1: Using capture_output When Passthrough is Needed
**What goes wrong:** Output appears only after command completes, not in real-time
**Why it happens:** `capture_output=True` sets stdout=PIPE, stderr=PIPE which buffers all output
**How to avoid:** Use default `stdout=None, stderr=None` for passthrough
**Warning signs:** User doesn't see long-running command progress, or output appears all at once

### Pitfall 2: Deadlock with PIPE and read()
**What goes wrong:** Script hangs indefinitely
**Why it happens:** Reading from stdout.read() while stderr buffer fills up (or vice versa), child blocks waiting for buffer to drain
**How to avoid:** Either use communicate() when capturing, or don't capture at all (use passthrough)
**Warning signs:** Script works for small output, hangs for large output

### Pitfall 3: Swallowing Exit Codes
**What goes wrong:** Caller can't detect when sl command failed
**Why it happens:** Returning 0 always, or using check=True and catching CalledProcessError
**How to avoid:** Always `return result.returncode` or `sys.exit(result.returncode)`
**Warning signs:** `echo $?` after gitsl always shows 0 even when sl failed

### Pitfall 4: Breaking Ctrl+C
**What goes wrong:** Ctrl+C kills parent but leaves child running, or child doesn't terminate cleanly
**Why it happens:** Custom signal handling that doesn't forward to child, or creating new process group
**How to avoid:** Use default subprocess.run() behavior - child inherits process group and receives SIGINT directly from terminal
**Warning signs:** Zombie processes, child continues after parent exits

### Pitfall 5: Monolithic Entry Point
**What goes wrong:** Violates ARCH-01, makes testing harder, creates merge conflicts
**Why it happens:** Putting command logic directly in main() instead of separate handlers
**How to avoid:** Entry point does ONLY: parse, dispatch, exit. All command logic in cmd_*.py
**Warning signs:** gitsl.py grows beyond ~50 lines, has command-specific if/else branches

### Pitfall 6: Import Errors on Unknown Commands
**What goes wrong:** ImportError crashes script instead of graceful "unknown command" message
**Why it happens:** Dynamic import without try/except
**How to avoid:** Either use static dictionary (safer) or catch ImportError for dynamic loads
**Warning signs:** "ModuleNotFoundError: No module named 'cmd_foo'" in user-facing output

## Code Examples

Verified patterns from official sources:

### Subprocess Passthrough (Real-Time I/O)
```python
# Source: Python subprocess documentation
# https://docs.python.org/3/library/subprocess.html
#
# "With the default settings of None, no redirection will occur."
# "Child process inherits parent's file descriptors"

import subprocess

def run_sl(args: list[str]) -> int:
    """Execute sl command with I/O passthrough."""
    result = subprocess.run(["sl"] + args)
    # stdout/stderr went directly to terminal
    # stdin was available for interactive input
    return result.returncode
```

### Exit Code Propagation
```python
# Source: Python subprocess documentation
# https://docs.python.org/3/library/subprocess.html
#
# "A negative value -N indicates that the child was terminated by signal N (POSIX only)."

import subprocess
import sys

def main():
    result = subprocess.run(["sl", "status"])
    # returncode is:
    # - 0 for success
    # - positive for error exit
    # - negative (-N) if killed by signal N (POSIX)
    sys.exit(result.returncode)
```

### Dynamic Module Import
```python
# Source: Python importlib documentation
# https://docs.python.org/3/library/importlib.html
#
# "importlib.import_module(name, package=None)"
# "Return the specified module"

import importlib

def get_handler(command: str):
    """Load command handler dynamically."""
    module_name = f"cmd_{command}"
    try:
        module = importlib.import_module(module_name)
        return module.handle
    except ImportError:
        return None

# Usage
handler = get_handler("status")
if handler:
    exit_code = handler(parsed)
```

### Dictionary-Based Command Dispatch
```python
# Source: Common Python CLI pattern
# Simpler than dynamic imports, explicit registration

HANDLERS = {
    "status": cmd_status.handle,
    "commit": cmd_commit.handle,
    "log": cmd_log.handle,
}

def dispatch(command: str, parsed: ParsedCommand) -> int:
    handler = HANDLERS.get(command)
    if handler:
        return handler(parsed)
    return handle_unknown(parsed)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| os.system() | subprocess.run() | Python 3.5 | Better security, error handling, return codes |
| subprocess.call() | subprocess.run() | Python 3.5 | run() is higher-level, returns CompletedProcess |
| __import__() | importlib.import_module() | Python 3.1+ | Cleaner API, returns target module directly |
| imp module | importlib | Python 3.4 | imp deprecated, removed in 3.12 |

**Deprecated/outdated:**
- `os.system()`: Use subprocess.run() instead for proper exit code handling
- `subprocess.call()`: Use subprocess.run() for consistency
- `imp` module: Removed in Python 3.12, use importlib

## Open Questions

Things that couldn't be fully resolved:

1. **Dynamic vs Static Dispatch**
   - What we know: Both patterns work; dynamic is more extensible, static is more explicit
   - What's unclear: Which is better for this specific project size
   - Recommendation: Start with static dictionary dispatch (simpler, explicit) - can refactor to dynamic later if needed

2. **Command Handler Return Type**
   - What we know: Handlers need to return exit codes
   - What's unclear: Should handlers raise exceptions or return error codes?
   - Recommendation: Return int exit codes (matches subprocess pattern); reserve exceptions for truly exceptional cases

3. **Debug Mode Integration**
   - What we know: Debug mode should show what would execute without running
   - What's unclear: Should debug mode be checked in entry point or in common.py's run_sl?
   - Recommendation: Check in entry point before dispatch (current pattern) - keeps handlers focused on execution

## Sources

### Primary (HIGH confidence)
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - subprocess.run() behavior, returncode, stdin/stdout/stderr inheritance, signal handling
- [Python importlib documentation](https://docs.python.org/3/library/importlib.html) - import_module() API and usage

### Secondary (MEDIUM confidence)
- [GeeksforGeeks SIGINT handling](https://www.geeksforgeeks.org/python/how-to-capture-sigint-in-python/) - KeyboardInterrupt patterns
- [CS Atlas subprocess exit codes](https://csatlas.com/python-subprocess-run-exit-code/) - returncode usage patterns

### Tertiary (LOW confidence)
- Various WebSearch results on CLI architecture patterns - informed design but not authoritative

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib, well-documented
- Architecture: HIGH - Follows established Python CLI patterns, constrained by prior decisions
- Pitfalls: HIGH - Well-documented subprocess edge cases

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable Python stdlib, patterns don't change)
