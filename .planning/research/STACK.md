# Stack Research: Git-to-Sapling CLI Shim

**Project:** gitsl - Git to Sapling command translator
**Researched:** 2026-01-17
**Constraint:** Zero dependencies (stdlib only), single-file script

## Recommended Approach

**Use `sys.argv` directly with manual parsing, `subprocess.run()` for execution, and `os.execvp()` for passthrough mode.**

For a CLI shim that intercepts git commands and translates them to Sapling (`sl`) commands, the architecture should be:

1. **Minimal parsing** - Don't fully parse; extract command name, recognize known commands, pass rest through
2. **Direct exec when possible** - Use `os.execvp()` to replace the process entirely for simple translations
3. **Subprocess for transformations** - Use `subprocess.run()` only when output needs modification

This approach is optimal because:
- Zero parsing overhead for passthrough commands
- Process replacement via `execvp` eliminates parent process overhead
- No external dependencies required
- Maintains signal propagation and TTY behavior

---

## Argument Parsing

### Recommendation: Direct `sys.argv` Access

**Do NOT use `argparse`.** For a command translator/shim:

```python
import sys

def main():
    args = sys.argv[1:]  # Skip script name

    if not args:
        # No command - show help or pass to sl
        pass

    command = args[0]
    command_args = args[1:]

    # Route based on command
    if command in TRANSLATION_MAP:
        translate_and_execute(command, command_args)
    else:
        passthrough_to_sl(command, command_args)
```

### Why NOT argparse

| Consideration | argparse | sys.argv |
|---------------|----------|----------|
| Git-style subcommands | Awkward - requires subparsers | Natural - just extract first arg |
| Unknown flags | Fails/errors | Passes through unchanged |
| Complexity | High for this use case | Minimal |
| Error handling | Automatic but unwanted | Manual but appropriate |

**Key insight:** A shim should NOT validate arguments. That's the downstream tool's job. Argparse wants to own the argument space, but we just need to intercept and redirect.

### Pattern: Command Extraction

```python
def parse_git_command(args: list[str]) -> tuple[str | None, list[str], dict[str, str]]:
    """
    Extract git command from args.

    Returns:
        (command, remaining_args, global_options)

    Git pattern: git [global-opts] <command> [command-opts] [args]
    """
    global_opts = {}
    remaining = list(args)

    # Extract global options (ones before command)
    while remaining:
        arg = remaining[0]
        if arg.startswith('-'):
            if arg in ('-C', '--git-dir', '--work-tree'):
                # Options that take a value
                global_opts[arg] = remaining[1] if len(remaining) > 1 else ''
                remaining = remaining[2:]
            elif arg.startswith('--'):
                global_opts[arg] = True
                remaining = remaining[1:]
            else:
                # Unknown flag - might be command
                break
        else:
            # First non-flag is the command
            break

    command = remaining[0] if remaining else None
    command_args = remaining[1:] if len(remaining) > 1 else []

    return command, command_args, global_opts
```

### Confidence: HIGH

Source: [Python official subprocess documentation](https://docs.python.org/3.14/library/subprocess.html), [PyMOTW shlex reference](https://pymotw.com/3/shlex/)

---

## Subprocess Execution

### Recommendation: Three-Tier Strategy

Use different execution strategies based on the translation type:

#### Tier 1: Process Replacement (`os.execvp`)

**For 1:1 command translations where no output transformation is needed.**

```python
import os

def passthrough_to_sl(command: str, args: list[str]) -> None:
    """Replace current process with sl command."""
    sl_command = COMMAND_MAP.get(command, command)
    os.execvp('sl', ['sl', sl_command] + args)
    # Never returns - process is replaced
```

**Advantages:**
- Zero overhead - no parent process waiting
- Signals pass through naturally (Ctrl+C works)
- TTY/terminal behavior preserved
- Exit code propagates automatically

**Use when:**
- `git status` -> `sl status`
- `git diff` -> `sl diff`
- `git log` -> `sl log`

#### Tier 2: Simple Subprocess (`subprocess.run`)

**For commands needing argument transformation but not output transformation.**

```python
import subprocess
import sys

def run_translated(sl_args: list[str]) -> int:
    """Run sl with translated arguments, return exit code."""
    result = subprocess.run(
        ['sl'] + sl_args,
        # Don't capture - let output flow to terminal
    )
    return result.returncode

# Usage
sys.exit(run_translated(['push', '--to', branch_name]))
```

**Use when:**
- `git push origin main` -> `sl push --to main`
- `git fetch origin` -> `sl pull`
- Arguments need transformation, output does not

#### Tier 3: Captured Subprocess

**For commands needing output transformation.**

```python
import subprocess
import sys

def run_and_transform(sl_args: list[str], transform_fn) -> int:
    """Run sl, capture output, transform, print."""
    result = subprocess.run(
        ['sl'] + sl_args,
        capture_output=True,
        text=True,
    )

    # Transform output
    transformed = transform_fn(result.stdout)

    # Write to appropriate streams
    sys.stdout.write(transformed)
    if result.stderr:
        sys.stderr.write(result.stderr)

    return result.returncode
```

**Use when:**
- Output needs to reference "git" terminology for compatibility
- Commit hashes need reformatting
- Status output needs translation

### Streaming Output (for long-running commands)

When output must be transformed but you need real-time streaming:

```python
import subprocess
import sys

def run_streaming(sl_args: list[str], line_transform) -> int:
    """Run with real-time line-by-line output transformation."""
    process = subprocess.Popen(
        ['sl'] + sl_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
    )

    # Read stdout line by line
    for line in process.stdout:
        transformed = line_transform(line)
        sys.stdout.write(transformed)
        sys.stdout.flush()

    # Wait for completion and get stderr
    _, stderr = process.communicate()
    if stderr:
        sys.stderr.write(stderr)

    return process.returncode
```

### Confidence: HIGH

Source: [Python subprocess documentation](https://docs.python.org/3.14/library/subprocess.html), [subprocess streaming gist](https://gist.github.com/almoore/c6fd2d041ad4f4bf2719a89c9b454f7e)

---

## Output Handling

### Recommendation: Minimal Transformation with Smart Passthrough

**Default to passthrough. Only transform when necessary.**

```python
import sys

def output_passthrough():
    """Most commands: let output flow directly to terminal."""
    # Don't capture stdout/stderr - subprocess inherits terminal
    subprocess.run(['sl'] + args)

def output_with_exit_code():
    """When we need the exit code but not output."""
    result = subprocess.run(['sl'] + args)
    sys.exit(result.returncode)

def output_captured_and_transformed():
    """When output needs modification."""
    result = subprocess.run(['sl'] + args, capture_output=True, text=True)
    # Transform...
    sys.stdout.write(transformed)
    sys.exit(result.returncode)
```

### Text Mode

Always use `text=True` (or `encoding='utf-8'`) when capturing:

```python
# Good - returns strings
result = subprocess.run(['sl', 'status'], capture_output=True, text=True)
print(result.stdout)  # String

# Also good - explicit encoding
result = subprocess.run(['sl', 'status'], capture_output=True, encoding='utf-8')

# Avoid - returns bytes, must decode
result = subprocess.run(['sl', 'status'], capture_output=True)
print(result.stdout.decode('utf-8'))  # Extra step
```

### Exit Code Propagation

**Critical for scripts that check git exit codes:**

```python
import sys
import subprocess

def main():
    # ... translation logic ...
    result = subprocess.run(['sl'] + translated_args)
    sys.exit(result.returncode)

# Or with execvp (automatic - exit code propagates naturally)
os.execvp('sl', ['sl'] + translated_args)
```

### Stderr Handling

Keep stderr separate unless there's a specific reason to merge:

```python
# Default: separate stderr (recommended)
result = subprocess.run(['sl', 'status'], capture_output=True, text=True)
if result.stderr:
    sys.stderr.write(result.stderr)

# Merged: only when needed for specific parsing
result = subprocess.run(
    ['sl', 'status'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,  # Merge stderr into stdout
    text=True
)
```

### Confidence: HIGH

Source: [Python subprocess documentation](https://docs.python.org/3.14/library/subprocess.html)

---

## Finding the Real Executable

### Recommendation: `shutil.which()` with PATH Filtering

The shim must find `sl` (and possibly the real `git` for fallback) while avoiding itself.

```python
import shutil
import os

def find_sl() -> str:
    """Find sl executable."""
    sl_path = shutil.which('sl')
    if not sl_path:
        raise RuntimeError("Sapling (sl) not found in PATH")
    return sl_path

def find_real_git(script_path: str) -> str | None:
    """
    Find the real git, excluding our shim.

    Args:
        script_path: Absolute path to this script (to exclude from search)
    """
    # Get our directory to exclude
    shim_dir = os.path.dirname(os.path.abspath(script_path))

    # Search PATH manually, skipping our directory
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)

    for dir_path in path_dirs:
        if os.path.abspath(dir_path) == shim_dir:
            continue  # Skip our own directory

        git_path = os.path.join(dir_path, 'git')
        if os.path.isfile(git_path) and os.access(git_path, os.X_OK):
            return git_path

    return None
```

### Confidence: HIGH

Source: [GeeksforGeeks shutil.which documentation](https://www.geeksforgeeks.org/python/shutil-module-in-python/)

---

## Script Structure

### Recommendation: Single-File with Shebang

```python
#!/usr/bin/env python3
"""
gitsl - Git to Sapling command translator.

Place in PATH before real git to intercept git commands.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import NoReturn


# =============================================================================
# COMMAND MAPPING
# =============================================================================

# Direct 1:1 translations (use execvp)
DIRECT_MAP: dict[str, str] = {
    'status': 'status',
    'diff': 'diff',
    'log': 'log',
    'add': 'add',
    'commit': 'commit',
    'blame': 'blame',
    # ...
}

# Commands needing argument transformation
TRANSFORM_MAP: dict[str, callable] = {
    'push': translate_push,
    'pull': translate_pull,
    'checkout': translate_checkout,
    # ...
}


# =============================================================================
# EXECUTION
# =============================================================================

def exec_sl(args: list[str]) -> NoReturn:
    """Replace process with sl."""
    os.execvp('sl', ['sl'] + args)


def run_sl(args: list[str]) -> int:
    """Run sl as subprocess, return exit code."""
    return subprocess.run(['sl'] + args).returncode


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    args = sys.argv[1:]

    if not args:
        exec_sl([])  # Let sl handle no-args

    command = args[0]
    command_args = args[1:]

    if command in DIRECT_MAP:
        exec_sl([DIRECT_MAP[command]] + command_args)
    elif command in TRANSFORM_MAP:
        translated = TRANSFORM_MAP[command](command_args)
        return run_sl(translated)
    else:
        # Unknown command - pass through
        exec_sl(args)


if __name__ == '__main__':
    sys.exit(main())
```

### Shebang

Use `#!/usr/bin/env python3` for portability across systems:

```python
#!/usr/bin/env python3
```

This finds python3 in PATH rather than hardcoding a path like `/usr/bin/python3`.

### Confidence: HIGH

Source: [Python shebang best practices](https://docs.kanaries.net/topics/Python/python-shebang)

---

## Stdlib Modules Summary

| Module | Purpose | Usage |
|--------|---------|-------|
| `sys` | Arguments, exit, streams | `sys.argv`, `sys.exit()`, `sys.stdout`, `sys.stderr` |
| `os` | Process replacement, env, paths | `os.execvp()`, `os.environ`, `os.path.*` |
| `subprocess` | Running commands | `subprocess.run()`, `subprocess.Popen()` |
| `shutil` | Finding executables | `shutil.which()` |
| `shlex` | Shell-style parsing (if needed) | `shlex.split()`, `shlex.quote()` |
| `typing` | Type hints | `NoReturn`, `Optional` |
| `re` | Regex (if pattern matching needed) | Pattern matching in output |

### Modules to AVOID

| Module | Why Avoid |
|--------|-----------|
| `argparse` | Over-engineered for shim use case; fights against passthrough |
| `click`/`typer` | External dependencies |
| `pty` | Complexity overkill; `execvp` handles TTY naturally |

---

## Alternatives Considered

### Alternative 1: argparse with Subparsers

**Considered:** Using argparse with subparsers for each git command.

**Rejected because:**
- Requires defining every possible argument for every command
- Unknown flags cause errors instead of passing through
- Adds overhead without benefit - we're not validating, just routing
- Git's argument style (global flags before command) awkward to model

### Alternative 2: Full PTY Passthrough

**Considered:** Using `pty.spawn()` for full terminal emulation.

```python
import pty
pty.spawn(['sl'] + args)
```

**Rejected because:**
- `os.execvp()` is simpler and sufficient for most cases
- PTY adds complexity without clear benefit
- Terminal behavior preserved naturally with execvp
- Only needed if intercepting/modifying interactive sessions

### Alternative 3: Always Subprocess (no execvp)

**Considered:** Using `subprocess.run()` for everything.

**Rejected because:**
- Extra process overhead for every command
- Must manually handle signals, exit codes
- TTY behavior can be disrupted
- `execvp` is cleaner for pure passthrough

### Alternative 4: External CLI Framework (Click, Typer)

**Considered:** Using Click or Typer for nicer CLI building.

**Rejected because:**
- Zero-dependency constraint
- These frameworks assume you're defining the CLI, not wrapping another
- Over-engineered for shim use case

---

## Git-to-Sapling Command Reference

Based on [Sapling's Git cheat sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/):

### Direct Translations (same semantics)

| Git | Sapling |
|-----|---------|
| `git clone` | `sl clone` |
| `git status` | `sl status` |
| `git diff` | `sl diff` |
| `git log` | `sl log` |
| `git add FILE` | `sl add FILE` |
| `git rm FILE` | `sl rm FILE` |
| `git mv` | `sl mv` |
| `git commit -a` | `sl commit` |
| `git commit --amend` | `sl amend` |
| `git show` | `sl show` |
| `git blame FILE` | `sl blame FILE` |
| `git stash` | `sl shelve` |
| `git stash pop` | `sl unshelve` |
| `git revert COMMIT` | `sl backout COMMIT` |
| `git cherry-pick COMMIT` | `sl graft COMMIT` |
| `git rebase -i` | `sl histedit` |
| `git clean -f` | `sl clean` |
| `git branch` | `sl bookmark` |

### Argument-Transformed Commands

| Git | Sapling | Notes |
|-----|---------|-------|
| `git fetch` | `sl pull` | Different semantics |
| `git pull --rebase` | `sl pull --rebase` | Same |
| `git push HEAD:BRANCH` | `sl push --to BRANCH` | Argument rewrite |
| `git checkout COMMIT` | `sl goto COMMIT` | Command rename |
| `git checkout -- FILE` | `sl revert FILE` | Different command! |
| `git reset --hard` | `sl revert --all` | Different command |
| `git reset --soft HEAD^` | `sl uncommit` | Different command |
| `git branch NAME` | `sl book NAME` | Abbreviation |
| `git branch -d NAME` | `sl book -d NAME` | Same flags |
| `git rm --cached FILE` | `sl forget FILE` | Different command |
| `git rebase main` | `sl rebase -d main` | Flag difference |

### Reference Translations

| Git | Sapling |
|-----|---------|
| `HEAD` | `.` |
| `HEAD^` | `.^` |
| `Y..X` (range) | `X % Y` |

---

## Sources

- [Python subprocess documentation](https://docs.python.org/3.14/library/subprocess.html) - Official subprocess API reference
- [Sapling Git cheat sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Command mapping reference
- [PyMOTW shlex](https://pymotw.com/3/shlex/) - Shell-style parsing
- [Real Python Command Line Arguments](https://realpython.com/python-command-line-arguments/) - Argument parsing approaches
- [Subprocess streaming patterns](https://gist.github.com/almoore/c6fd2d041ad4f4bf2719a89c9b454f7e) - Real-time output handling
- [os.execvp usage](https://iditect.com/faq/python/replace-current-process-with-invocation-of-subprocess-in-python.html) - Process replacement patterns
- [Python shebang best practices](https://docs.kanaries.net/topics/Python/python-shebang) - Executable script setup
