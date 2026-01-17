# Pitfalls Research: CLI Shim/Command Translation

**Domain:** Git-to-Sapling CLI translation shim
**Researched:** 2026-01-17
**Confidence:** HIGH (verified against Python docs and official sources)

---

## Critical Pitfalls

Mistakes that cause rewrites, data corruption, or complete failure of the shim.

### Pitfall 1: Subprocess Deadlock with Pipe Buffering

**What goes wrong:** Using `wait()` or direct `.stdout.read()` with `stdout=PIPE` causes the program to hang indefinitely.

**Why it happens:** OS pipe buffers have limited capacity (typically 64KB on Linux). When a child process writes more output than the buffer can hold, it blocks waiting for the parent to read. But if the parent is blocked in `wait()` or reading from the wrong stream first, neither can proceed.

**Consequences:**
- Shim hangs forever on any command producing significant output
- `git log`, `git diff`, `git status` on large repos will freeze
- No error message - just unresponsive process

**Prevention:**
```python
# WRONG - will deadlock on large output
proc = subprocess.Popen(["sl", "log"], stdout=PIPE, stderr=PIPE)
proc.wait()  # DEADLOCK
output = proc.stdout.read()

# CORRECT - use communicate() which handles buffering safely
proc = subprocess.Popen(["sl", "log"], stdout=PIPE, stderr=PIPE)
stdout, stderr = proc.communicate()
```

**Detection:** Test with commands that produce more than 64KB output.

**Which phase should address:** Core subprocess handling layer (Phase 1). This is foundational - get it wrong and nothing works.

**Source:** [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence

---

### Pitfall 2: Exit Code Loss

**What goes wrong:** Wrapper exits with code 0 even when the underlying command failed.

**Why it happens:**
- Forgetting to propagate `returncode` from subprocess
- Using `call()` or `run()` without checking return value
- Exception handling that masks the original exit code

**Consequences:**
- CI/CD pipelines pass when they should fail
- Scripts depending on git exit codes break silently
- `git commit` appearing to succeed when it failed

**Prevention:**
```python
# WRONG - swallows exit code
try:
    result = subprocess.run(["sl", "commit"])
except Exception:
    pass  # Loses the exit code

# CORRECT - always propagate
result = subprocess.run(["sl", "commit"])
sys.exit(result.returncode)
```

**Detection:** Test with intentionally failing commands and verify exit codes.

**Which phase should address:** Core subprocess handling (Phase 1). Must be baked into the fundamental execution pattern.

**Source:** General subprocess patterns - HIGH confidence

---

### Pitfall 3: Infinite Recursion via PATH

**What goes wrong:** Shim named `git` calls `git`, which resolves to itself, creating infinite recursion.

**Why it happens:** If the shim is installed in PATH as `git`, and it tries to shell out to the real `git` for unsupported commands, it calls itself.

**Consequences:**
- Stack overflow or fork bomb
- System resource exhaustion
- Appears to hang, then crashes

**Prevention:**
```python
# WRONG - may call self
subprocess.run(["git", "unsupported-command"])

# CORRECT - use absolute path to real command OR delegate to sl
REAL_GIT = "/usr/bin/git"  # Configured at install time
subprocess.run([REAL_GIT, "unsupported-command"])

# BETTER - just use sl for everything, translate or pass through
subprocess.run(["sl"] + translated_args)
```

**Detection:** Test shim installed as `git` in PATH, ensure no recursion.

**Which phase should address:** Architecture design (Phase 1). Decide early: does shim ever call git, or only sl?

**Source:** Common CLI wrapper pattern - HIGH confidence

---

### Pitfall 4: Signal Handling Breaks Ctrl+C

**What goes wrong:** Pressing Ctrl+C during a long operation doesn't cleanly terminate the subprocess.

**Why it happens:**
- SIGINT reaches the wrapper but not the child (or reaches both incorrectly)
- Wrapper exits but child process continues running
- `preexec_fn` signal handling is Unix-only

**Consequences:**
- Orphaned sl processes
- Corrupted repository state if interrupted mid-operation
- User frustration - Ctrl+C doesn't work

**Prevention:**
```python
import signal

# Ensure child receives signals
proc = subprocess.Popen(["sl", "pull"])

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    sys.exit(128 + signal.SIGINT)  # Standard exit code for SIGINT
```

**Detection:** Test Ctrl+C during long operations like `git clone` or `git pull`.

**Which phase should address:** Subprocess execution layer (Phase 1). Cross-platform signal handling is tricky.

**Source:** [SIGINT subprocess handling](https://www.iditect.com/faq/python/making-sure-a-python-script-with-subprocesses-dies-on-sigint.html) - MEDIUM confidence

---

## Argument Parsing Pitfalls

### Pitfall 5: Dash-Prefixed Option Arguments

**What goes wrong:** `git commit -m "-WIP-"` fails because argparse interprets `-WIP-` as an unknown option.

**Why it happens:** Argparse performs preliminary classification of all arguments, marking anything starting with `-` as an option before considering context. This is a known, unfixable architectural issue (closed as "wont fix" in 2021).

**Consequences:**
- Common patterns like negative commit references fail
- Users forced to use `=` syntax: `-m=-WIP-`
- Inconsistent behavior compared to real git

**Prevention:**
```python
# Option 1: Use parse_known_args and handle manually
args, remaining = parser.parse_known_args()

# Option 2: Don't use argparse for git-style parsing
# Roll custom parser or use shlex + manual parsing

# Option 3: Accept = syntax and document
# git commit -m="message starting with dash"
```

**Detection:** Test with messages/refs starting with dashes.

**Which phase should address:** Argument parsing layer (Phase 1). Choose parsing strategy early.

**Source:** [Python argparse issue 9334](https://bugs.python.org/issue9334) - HIGH confidence

---

### Pitfall 6: Subparser Abbreviation Ambiguity

**What goes wrong:** Using argparse subparsers with abbreviated options causes false "ambiguous option" errors.

**Why it happens:** When main parser has `--foo1` and `--foo2`, and subparser has `--foo`, argparse incorrectly reports ambiguity even though the subparser option should take precedence in that context.

**Consequences:**
- Valid commands rejected
- Users can't use option abbreviations they expect from git

**Prevention:**
- Don't use argparse's subparser feature for git-style command dispatch
- Use simpler two-phase parsing: identify subcommand first, then parse its args

```python
# PROBLEMATIC - argparse subparsers
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# BETTER - manual dispatch
command = sys.argv[1] if len(sys.argv) > 1 else "help"
command_args = sys.argv[2:]
handler = COMMAND_MAP.get(command, handle_unknown)
handler(command_args)
```

**Detection:** Test abbreviated options with subcommands.

**Which phase should address:** Command dispatch architecture (Phase 1).

**Source:** [Python argparse issue 14365](https://bugs.python.org/issue14365) - HIGH confidence

---

### Pitfall 7: Scientific Notation as Negative Numbers

**What goes wrong:** Arguments like `-3e12` or `-1e-5` are rejected as unknown options instead of being parsed as values.

**Why it happens:** Argparse's negative number regex only matches simple integers and decimals, not scientific notation.

**Consequences:**
- Edge case, but surprising failures for users passing numeric values

**Prevention:**
- For a git shim, this is unlikely to occur often
- If needed, preprocess arguments to quote scientific notation values

**Detection:** Test with numeric values in scientific notation.

**Which phase should address:** Low priority, but note during argument parsing design.

**Source:** [Python cpython issue 105712](https://github.com/python/cpython/issues/105712) - HIGH confidence

---

### Pitfall 8: Unknown Arguments with Spaces

**What goes wrong:** `--option="value with spaces"` is misinterpreted when passed through.

**Why it happens:** `parse_known_args` can incorrectly classify spaced values as positional arguments.

**Consequences:**
- Arguments split incorrectly
- Commands fail with confusing errors

**Prevention:**
- Preserve original sys.argv for passthrough
- Don't re-quote or re-split already-parsed arguments

```python
# WRONG - loses quoting
args_string = " ".join(sys.argv[1:])
subprocess.run(f"sl {args_string}", shell=True)

# CORRECT - pass argv directly
subprocess.run(["sl"] + sys.argv[1:])
```

**Detection:** Test with arguments containing spaces, quotes, special characters.

**Which phase should address:** Argument passthrough (Phase 1).

**Source:** [Python argparse issue 22433](https://bugs.python.org/issue22433) - HIGH confidence

---

## Subprocess Pitfalls

### Pitfall 9: shell=True Security and Quoting Chaos

**What goes wrong:** Using `shell=True` with user-provided arguments enables injection or breaks on special characters.

**Why it happens:**
- Shell interprets metacharacters: `$`, `;`, `|`, `>`, etc.
- User-provided branch names or file paths with special chars break
- Security: malicious input can execute arbitrary commands

**Consequences:**
- Command injection vulnerabilities
- Branch name `feature;rm -rf /` causes disaster with shell=True
- Inconsistent behavior across shells

**Prevention:**
```python
# NEVER use shell=True with user input
# WRONG
subprocess.run(f"sl log {branch_name}", shell=True)

# CORRECT - pass as list, no shell
subprocess.run(["sl", "log", branch_name])
```

**Detection:** Test with branch/file names containing `;`, `$`, `|`, spaces, quotes.

**Which phase should address:** Core subprocess execution (Phase 1). Never use shell=True.

**Source:** [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence

---

### Pitfall 10: Timeout Without Cleanup

**What goes wrong:** Setting a timeout but not killing the child process on timeout.

**Why it happens:** `TimeoutExpired` is raised, but child continues running in background.

**Consequences:**
- Orphaned processes
- Resource leaks
- Incomplete operations still running

**Prevention:**
```python
proc = subprocess.Popen(["sl", "clone", url])
try:
    proc.communicate(timeout=300)
except subprocess.TimeoutExpired:
    proc.kill()
    proc.communicate()  # Finish cleanup
    raise
```

**Detection:** Test with artificially low timeouts.

**Which phase should address:** Subprocess execution layer (Phase 1).

**Source:** [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence

---

### Pitfall 11: Encoding Mismatches

**What goes wrong:** Output with non-ASCII characters (branch names, commit messages, file paths) gets garbled or crashes.

**Why it happens:**
- Subprocess returns bytes, not strings
- Decoding with wrong encoding (ASCII instead of UTF-8)
- Locale not propagated to child process

**Consequences:**
- UnicodeDecodeError crashes
- Garbled output for international users
- File operations fail on Unicode paths

**Prevention:**
```python
# Specify encoding explicitly
result = subprocess.run(
    ["sl", "log"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"  # Don't crash on bad bytes
)

# Or handle bytes manually
result = subprocess.run(["sl", "log"], capture_output=True)
output = result.stdout.decode("utf-8", errors="replace")
```

**Detection:** Test with non-ASCII branch names, commit messages, file paths.

**Which phase should address:** Output handling (Phase 1).

**Source:** General Python encoding patterns - HIGH confidence

---

## Output Transformation Pitfalls

### Pitfall 12: Color/ANSI Code Handling

**What goes wrong:** Colored output from sl is stripped or corrupted when passed through shim.

**Why it happens:**
- Programs detect `isatty()` and disable colors when piped
- ANSI codes may not survive subprocess piping
- Windows requires special handling for ANSI

**Consequences:**
- Loss of syntax highlighting and visual feedback
- Output looks different through shim vs direct sl

**Prevention:**
```python
# Option 1: Use pty to preserve TTY
import pty
import os

master, slave = pty.openpty()
proc = subprocess.Popen(["sl", "log"], stdout=slave, stderr=slave)

# Option 2: Pass through flags that force color
subprocess.run(["sl", "log", "--color=always"])

# Option 3: Don't capture output if passing through
subprocess.run(["sl", "log"])  # No stdout=PIPE, goes directly to terminal
```

**Detection:** Compare shim output colors vs direct sl invocation.

**Which phase should address:** Output handling (Phase 2). Consider whether to transform or pass through.

**Source:** [Python discuss - subprocess color codes](https://discuss.python.org/t/subprocess-output-with-color-codes/36241) - MEDIUM confidence

---

### Pitfall 13: Git Porcelain vs Human Output Confusion

**What goes wrong:** Parsing human-readable output that changes between versions/locales.

**Why it happens:**
- Human output is not stable: whitespace, wording, order can change
- Localized output (different languages) breaks parsing
- Version updates change formatting

**Consequences:**
- Regex-based parsing breaks mysteriously
- Different behavior on different systems

**Prevention:**
```python
# For git output you need to parse, use porcelain formats
subprocess.run(["git", "status", "--porcelain=v2"])
subprocess.run(["git", "log", "--format=%H %s"])

# For sapling, check equivalent machine-readable options
subprocess.run(["sl", "log", "-T", "{node} {desc}\\n"])
```

**Detection:** Test parsing with different locales (LANG=de_DE, etc.)

**Which phase should address:** Output parsing phase. Only parse when transformation needed.

**Source:** General CLI patterns - HIGH confidence

---

### Pitfall 14: Reference Syntax Translation Errors

**What goes wrong:** Git reference syntax like `HEAD^`, `master..feature`, `@{-1}` translated incorrectly.

**Why it happens:**
- Git uses `HEAD` and `^` for parent; Sapling uses `.` and `^`
- Range syntax differs: Git `Y..X` vs Sapling `X % Y`
- Special refs like `@{-1}` may not have equivalents

**Consequences:**
- Commands silently operate on wrong commits
- Data loss from operations on unintended commits
- Confusing errors

**Prevention:**
```python
# Build explicit translation table
REFERENCE_MAP = {
    "HEAD": ".",
    "HEAD^": ".^",
    "HEAD~1": ".~1",
    # ... comprehensive mapping
}

def translate_ref(git_ref):
    # Handle complex patterns like HEAD~N, master..feature
    # Test extensively
```

**Detection:** Test all git reference formats documented in gitrevisions(7).

**Which phase should address:** Dedicated reference translation phase. High complexity, needs thorough testing.

**Source:** [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - HIGH confidence

---

## Edge Cases

### Pitfall 15: Empty/Missing Arguments

**What goes wrong:** Commands like `git commit -m ""` or `git log --author=` break.

**Why it happens:**
- Empty strings handled inconsistently
- Some parsers skip empty args
- Subprocess list may filter empty strings

**Consequences:**
- Commands interpreted differently than intended
- Empty commit messages when user wanted to abort

**Prevention:**
```python
# Preserve empty strings
args = ["sl", "commit", "-m", ""]  # Empty string preserved
subprocess.run(args)

# Watch for filter() removing empty strings
# WRONG
args = list(filter(None, args))  # Removes empty strings!
```

**Detection:** Test with empty string arguments, empty files, no-op commands.

**Which phase should address:** Argument handling (Phase 1).

---

### Pitfall 16: Environment Variable Propagation

**What goes wrong:** Git environment variables not passed to sl, causing unexpected behavior.

**Why it happens:**
- `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` affect git behavior
- Subprocess may not inherit environment
- Sapling has equivalent variables that need translation

**Consequences:**
- Operations in wrong repository
- Hooks fail
- Editor/pager not invoked

**Prevention:**
```python
# Pass through environment
env = os.environ.copy()

# Consider translating git env vars to sapling equivalents
# or stripping git-specific vars that confuse sl

result = subprocess.run(["sl", "log"], env=env)
```

**Detection:** Test with GIT_DIR set, GIT_WORK_TREE set, inside git hooks.

**Which phase should address:** Environment handling (Phase 1).

**Source:** [Git Environment Variables](https://git-scm.com/book/uz/v2/Git-Internals-Environment-Variables) - HIGH confidence

---

### Pitfall 17: Windows-Specific Batch File Vulnerability

**What goes wrong:** On Windows, even without shell=True, batch files invoke cmd.exe.

**Why it happens:** Windows shell association runs .bat/.cmd files through cmd.exe regardless of how they're invoked.

**Consequences:**
- Shell injection via batch file arguments
- Security vulnerability on Windows

**Prevention:**
```python
# On Windows, if invoking batch files with untrusted args,
# consider shell=True to get proper escaping
# Or avoid batch files entirely
```

**Detection:** Windows-specific testing with special characters in args.

**Which phase should address:** Note for Windows compatibility (if targeted).

**Source:** [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - HIGH confidence

---

### Pitfall 18: Command-Specific Flag Differences

**What goes wrong:** Flag that exists in git has different meaning in sl, or doesn't exist.

**Why it happens:**
- `git fetch` vs `sl pull` (fetch = pull in sapling)
- `git push HEAD:branch` vs `sl push --to branch`
- Short flags may conflict

**Consequences:**
- Silent wrong behavior (flag ignored or means something else)
- Errors that don't explain the translation issue

**Prevention:**
```python
# Maintain per-command translation tables
COMMAND_TRANSLATIONS = {
    "fetch": {
        "sl_command": "pull",
        "flag_map": {
            "--all": None,  # Different in sl
            "-p": "--prune",  # Example mapping
        }
    }
}

# Log/warn when a flag can't be translated
```

**Detection:** Test each supported command with all common flags.

**Which phase should address:** Per-command translation (Phase 2+). Each command needs its own translation logic.

**Source:** [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - HIGH confidence

---

### Pitfall 19: Interactive Command Handling

**What goes wrong:** Commands requiring user input (rebase -i, merge conflicts, credential prompts) fail.

**Why it happens:**
- stdin not connected to terminal
- PTY not established
- Interactive editors don't launch

**Consequences:**
- Interactive rebase impossible
- Credential prompts hang
- Merge conflict resolution broken

**Prevention:**
```python
# For interactive commands, don't capture stdio
# Let them connect directly to terminal
subprocess.run(["sl", "histedit"])  # No capture, direct terminal access

# Or use pty for full terminal emulation
import pty
pty.spawn(["sl", "histedit"])
```

**Detection:** Test interactive commands: histedit, merge with conflicts, clone requiring credentials.

**Which phase should address:** Interactive command handling (Phase 2+). May need special cases.

---

### Pitfall 20: Git Alias Expansion

**What goes wrong:** User has git aliases that the shim doesn't understand.

**Why it happens:**
- Git aliases defined in ~/.gitconfig
- Shim receives alias as command, not expansion
- User expects `git st` to work (alias for status)

**Consequences:**
- "Unknown command: st"
- Users must re-configure aliases

**Prevention:**
- Document that git aliases don't work (simplest)
- Read and parse git config to understand aliases (complex)
- Support common aliases out of box

**Detection:** Test with common aliases configured.

**Which phase should address:** Either document limitation or add alias support (later phase).

---

## Phase-Specific Warning Summary

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Subprocess execution | Deadlock, exit codes, signals | Use communicate(), propagate returncode, handle SIGINT |
| Argument parsing | Dash-prefixed values, spaces | Avoid argparse quirks, preserve original argv |
| Command translation | Flag differences, ref syntax | Per-command tables, comprehensive testing |
| Output handling | Colors, encoding | PTY or force-color, explicit UTF-8 |
| Interactive commands | stdin/PTY issues | Don't capture, use pty.spawn |
| Passthrough/fallback | Infinite recursion | Absolute paths or delegate everything to sl |

---

## Sources

- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) - Official, authoritative
- [Python argparse issue 9334 - Dash-prefixed arguments](https://bugs.python.org/issue9334) - Official Python tracker
- [Python argparse issue 14365 - Subparser ambiguity](https://bugs.python.org/issue14365) - Official Python tracker
- [Python argparse issue 22433 - Spaces in unknown args](https://bugs.python.org/issue22433) - Official Python tracker
- [Python cpython issue 105712 - Scientific notation](https://github.com/python/cpython/issues/105712) - Official CPython repo
- [Python subprocess wait() deadlock issue 1606](https://bugs.python.org/issue1606) - Official Python tracker
- [Sapling Git Cheat Sheet](https://sapling-scm.com/docs/introduction/git-cheat-sheet/) - Official Sapling docs
- [Git Environment Variables](https://git-scm.com/book/uz/v2/Git-Internals-Environment-Variables) - Official Git docs
- [Python discuss - subprocess color codes](https://discuss.python.org/t/subprocess-output-with-color-codes/36241) - Community discussion
