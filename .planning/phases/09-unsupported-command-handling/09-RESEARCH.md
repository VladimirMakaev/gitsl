# Phase 9: Unsupported Command Handling - Research

**Researched:** 2026-01-18
**Domain:** CLI error handling, graceful degradation, git command shim patterns
**Confidence:** HIGH

## Summary

Phase 9 transforms the existing stub fallback in gitsl.py into a proper unsupported command handler. The current code (lines 81-82) already prints a debug-style message to stderr and returns 0, but needs refinement to meet UNSUP-01 and UNSUP-02 requirements.

The key insight is that gitsl is designed for a specific use case (get-shit-done integration), so unsupported commands should:
1. Not crash the calling tool (exit 0)
2. Inform the user what command was attempted (print to stderr)
3. Leave stdout empty (so parsing tools don't get confused)

**Primary recommendation:** Replace the `[STUB]` message with a clear "unsupported command" message that includes the original git command, writes to stderr, and exits 0.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sys | stdlib | stderr output, exit code | Python's standard I/O module |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shlex | stdlib | Command reconstruction | Safely quote command for display |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Print raw args | shlex.join() | shlex handles quoting correctly |
| Separate unsupported handler module | Inline in gitsl.py | Phase 3 architecture allows inline for fallback since it's not a command handler |

**Installation:**
```bash
# No installation needed - all stdlib already imported
```

## Architecture Patterns

### Recommended Project Structure

No new files needed. Unsupported command handling fits within the existing entry point fallback:

```
gitsl/
├── gitsl.py           # Contains fallback for unsupported commands
├── common.py          # No changes needed
└── cmd_*.py           # Existing command handlers
```

### Pattern 1: Fallback with Informative Error

**What:** When a command is not in the handler registry, print informative message to stderr and exit 0
**When to use:** Always for unsupported commands

**Example:**
```python
# gitsl.py fallback section

# Fallback for unsupported commands
original_command = f"git {parsed.command}" + (f" {shlex.join(parsed.args)}" if parsed.args else "")
print(f"gitsl: unsupported command: {original_command}", file=sys.stderr)
return 0
```

### Pattern 2: Reconstruct Original Command

**What:** Build the full command string that the user (or calling tool) attempted
**When to use:** For error messages

**Example:**
```python
# Reconstruct what user ran
if parsed.args:
    full_command = f"git {parsed.command} {shlex.join(parsed.args)}"
else:
    full_command = f"git {parsed.command}"
```

### Anti-Patterns to Avoid

- **Exit non-zero on unsupported commands:** This would cause get-shit-done to think the git command failed, which breaks the integration use case.

- **Print to stdout:** Calling tools may parse stdout. Error/info messages should go to stderr.

- **Silent failure:** While exit 0 is correct, users should know why no action occurred.

- **Print "STUB" or debug-style messages:** The current `[STUB] Would process:` message looks like debug output, not a user-facing error message.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Command quoting for display | Manual string concatenation | shlex.join() | Handles spaces and special chars |
| Output to stderr | Redirect print | `print(..., file=sys.stderr)` | Python standard pattern |

**Key insight:** The fallback is simple enough that no new modules or complex logic is needed. The change is primarily about message format and semantics.

## Common Pitfalls

### Pitfall 1: Returning Non-Zero Exit Code

**What goes wrong:** Calling tool (get-shit-done) treats the command as failed
**Why it happens:** Instinct to return 1 for "error" conditions
**How to avoid:** Requirement UNSUP-02 explicitly requires exit 0
**Warning signs:** `echo $?` returns non-zero after unsupported commands

### Pitfall 2: Writing to Stdout

**What goes wrong:** Calling tool may parse stdout and get garbage
**Why it happens:** Using print() without file=sys.stderr
**How to avoid:** Always use `print(..., file=sys.stderr)` for error/info messages
**Warning signs:** `git push 2>/dev/null` still shows output

### Pitfall 3: Unclear Message Format

**What goes wrong:** User doesn't understand what happened
**Why it happens:** Terse or technical error message
**How to avoid:** Include "gitsl:" prefix, "unsupported command:", and the full original command
**Warning signs:** User asks "what does this error mean?"

### Pitfall 4: Missing Command Arguments in Message

**What goes wrong:** User can't tell exactly which command was unsupported
**Why it happens:** Only printing `parsed.command` without `parsed.args`
**How to avoid:** Reconstruct full command with shlex.join()
**Warning signs:** Message shows "git push" when user ran "git push origin main"

## Code Examples

Verified patterns from the existing codebase:

### Current Fallback (To Be Replaced)
```python
# Source: gitsl.py lines 81-82
# Current stub behavior

# Fallback for unimplemented commands
print(f"[STUB] Would process: git {parsed.command}", file=sys.stderr)
return 0
```

### Recommended Replacement
```python
# gitsl.py fallback section
# Meets UNSUP-01 (print original command to stderr) and UNSUP-02 (exit 0)

import shlex

# ... in main(), after all command handlers ...

# Unsupported command handling (UNSUP-01, UNSUP-02)
if parsed.args:
    original_command = f"git {parsed.command} {shlex.join(parsed.args)}"
else:
    original_command = f"git {parsed.command}"

print(f"gitsl: unsupported command: {original_command}", file=sys.stderr)
return 0
```

### Message Format Options

Three reasonable formats for the error message:

```python
# Option 1: Minimal but clear (RECOMMENDED)
f"gitsl: unsupported command: {original_command}"
# Example: gitsl: unsupported command: git push origin main

# Option 2: More verbose
f"gitsl: '{original_command}' is not supported"
# Example: gitsl: 'git push origin main' is not supported

# Option 3: With action suggestion
f"gitsl: unsupported command: {original_command} (try running directly)"
# Example: gitsl: unsupported command: git push origin main (try running directly)
```

**Recommendation:** Option 1 is clearest. It follows the standard CLI pattern of `tool: error type: details`.

### Test Pattern for Unsupported Commands
```python
# tests/test_unsupported.py
# Follows existing test patterns from conftest.py

def test_push_unsupported_exits_zero(sl_repo: Path):
    """UNSUP-02: Unsupported commands exit with code 0."""
    result = run_gitsl(["push"], cwd=sl_repo)
    assert result.exit_code == 0

def test_push_unsupported_message_on_stderr(sl_repo: Path):
    """UNSUP-01: Unsupported commands print original command to stderr."""
    result = run_gitsl(["push", "origin", "main"], cwd=sl_repo)
    assert "git push origin main" in result.stderr
    assert "unsupported" in result.stderr

def test_push_unsupported_stdout_empty(sl_repo: Path):
    """Unsupported commands don't pollute stdout."""
    result = run_gitsl(["push"], cwd=sl_repo)
    assert result.stdout == ""
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| [STUB] debug message | Proper error message | This phase | User-facing clarity |
| Print raw args | shlex.join() reconstruction | Python 3.8+ | Handles edge cases |

**Deprecated/outdated:**
- The `[STUB]` prefix is a placeholder from Phase 3 that should now be replaced

## Open Questions

Things that couldn't be fully resolved:

1. **Message format preference**
   - What we know: Message should include "gitsl", "unsupported", and the command
   - What's unclear: Exact wording preference
   - Recommendation: Use `gitsl: unsupported command: {command}` format

2. **List of known unsupported commands**
   - What we know: push, pull, checkout, branch, fetch, rebase are unsupported
   - What's unclear: Whether to explicitly list them or treat any unknown command as unsupported
   - Recommendation: Treat any command not in handlers as unsupported (current approach is correct)

## Sources

### Primary (HIGH confidence)
- `/Users/vmakaev/NonWork/gitsl/gitsl.py` - Current fallback implementation (lines 81-82)
- `/Users/vmakaev/NonWork/gitsl/.planning/REQUIREMENTS.md` - UNSUP-01, UNSUP-02 requirements
- `/Users/vmakaev/NonWork/gitsl/.planning/PROJECT.md` - Project context and use case

### Secondary (MEDIUM confidence)
- `/Users/vmakaev/NonWork/gitsl/tests/conftest.py` - Test patterns
- `/Users/vmakaev/NonWork/gitsl/common.py` - Existing utilities (shlex already imported for debug)

### Tertiary (LOW confidence)
- None - this phase is straightforward with clear requirements

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies, using existing imports
- Architecture: HIGH - Follows existing pattern, minimal change
- Pitfalls: HIGH - Well-understood edge cases
- Implementation: HIGH - Clear requirements, existing code to modify

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable requirements, no external dependencies)
