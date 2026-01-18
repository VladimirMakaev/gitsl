# Phase 6: Status Output Emulation - Research

**Researched:** 2026-01-18
**Domain:** Git porcelain/short status format emulation from Sapling output
**Confidence:** HIGH

## Summary

Phase 6 implements output transformation for `git status --porcelain` and `git status --short` flags. The core challenge is translating Sapling's single-character status codes to git's two-character XY format, where X represents index (staged) status and Y represents working tree status.

The key insight is that Sapling has no staging area concept - all pending changes are effectively "staged" and will be included in the next commit. Therefore:
- Sapling `A` (added) maps to git `A ` (staged addition)
- Sapling `R` (removed) maps to git `D ` (staged deletion)
- Sapling `M` (modified) maps to git ` M` (modified in working tree, not staged) - this preserves the expectation that tools may call `git add` before commit
- Sapling `?` (unknown) maps to git `??` (untracked)
- Sapling `!` (missing) maps to git ` D` (deleted in working tree, not staged)

Renames are the most complex case: Sapling shows renames as two separate lines (`A newname` + `R oldname`) while git shows them as single lines (`R  oldname -> newname`). For MVP, treating renames as add+delete is acceptable since tools parsing porcelain typically handle both representations.

**Primary recommendation:** Create an output transformer in `cmd_status.py` that captures `sl status` output, parses each line, and reformats to git porcelain format. Use `capture_output=True` pattern from `cmd_rev_parse.py`.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Run `sl status` with output capture | Already used in cmd_rev_parse.py |
| sys | stdlib | Write to stdout/stderr | Already in use |
| re | stdlib | Parse status lines (optional) | Simpler than manual parsing for edge cases |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints | Already in use |

**Installation:**
```bash
# No new dependencies - all patterns established in Phase 4
```

## Architecture Patterns

### Current Project Structure
```
gitsl/
├── gitsl.py           # Entry point with dispatch
├── common.py          # ParsedCommand, run_sl(), debug helpers
├── cmd_status.py      # Handler for 'git status' - NEEDS MODIFICATION
├── cmd_rev_parse.py   # Example of capture_output pattern
└── tests/
    ├── conftest.py    # Fixtures: sl_repo, sl_repo_with_commit
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # compare_exact(), assert_commands_equal()
    └── test_cmd_*.py
```

### Pattern 1: Output Transformation Handler
**What:** Handler that captures sl output and transforms before printing
**When to use:** For --porcelain and --short flags

**Example:**
```python
# cmd_status.py - enhanced version
"""Handler for 'git status' command."""

import subprocess
import sys
from common import ParsedCommand, run_sl

# Status code translation: sl -> git porcelain XY format
SL_TO_GIT_STATUS = {
    'M': ' M',  # Modified (working tree, not staged in git terms)
    'A': 'A ',  # Added (staged in git terms)
    'R': 'D ',  # Removed (staged deletion in git terms)
    '?': '??',  # Unknown/untracked
    '!': ' D',  # Missing (deleted in working tree, not staged)
    'C': '  ',  # Clean (not typically shown, but for completeness)
    'I': '!!',  # Ignored
}


def transform_to_porcelain(sl_output: str) -> str:
    """
    Transform sl status output to git porcelain format.

    sl format: "X filename" (1 char + space + filename)
    git format: "XY filename" (2 chars + space + filename)
    """
    lines = []
    for line in sl_output.splitlines():
        if not line or len(line) < 2:
            continue

        sl_code = line[0]
        # Skip copy source lines (start with 2 spaces from -C flag)
        if sl_code == ' ' and len(line) > 1 and line[1] == ' ':
            continue

        filename = line[2:]  # Skip "X " prefix
        git_code = SL_TO_GIT_STATUS.get(sl_code, '??')
        lines.append(f"{git_code} {filename}")

    return '\n'.join(lines) + ('\n' if lines else '')


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git status' command.

    Special handling for --porcelain and --short flags.
    """
    # Check for porcelain/short flags
    needs_transform = '--porcelain' in parsed.args or '--short' in parsed.args or '-s' in parsed.args

    if needs_transform:
        # Remove git-specific flags before calling sl
        sl_args = [a for a in parsed.args
                   if a not in ('--porcelain', '--short', '-s')]

        result = subprocess.run(
            ['sl', 'status'] + sl_args,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            transformed = transform_to_porcelain(result.stdout)
            sys.stdout.write(transformed)
        else:
            sys.stderr.write(result.stderr)

        return result.returncode

    # Default: passthrough to sl status
    return run_sl(['status'] + parsed.args)
```

### Pattern 2: Golden Master Test Pattern
**What:** Test that compares git output vs gitsl output byte-for-byte
**When to use:** For exact format matching tests

**Example:**
```python
# test_status_porcelain.py
def test_porcelain_modified_file(sl_repo_with_changes):
    """porcelain output for modified file matches git format."""
    # Create equivalent scenario in both git and sl repos
    git_result = run_git(['status', '--porcelain'], cwd=git_repo)
    gitsl_result = run_gitsl(['status', '--porcelain'], cwd=sl_repo)

    # Compare format (XY codes and structure), not exact content
    # since different repos have different files
    assert_output_format_match(git_result.stdout, gitsl_result.stdout)
```

### Anti-Patterns to Avoid

- **Reimplementing git's full porcelain logic:** Focus only on codes that sl produces. Don't try to handle merge conflicts, submodules, etc.

- **Assuming porcelain v2 is needed:** v1 is the default and what tools expect. Don't implement v2 unless explicitly required.

- **Breaking passthrough for normal status:** Only intercept when --porcelain or --short is present. Normal `git status` should still passthrough.

## Git Status Format Specification

### Short/Porcelain Format Structure
```
XY PATH
XY ORIG_PATH -> PATH   (for renames/copies)
```

Where:
- X = status in index (staged changes)
- Y = status in working tree (unstaged changes)
- Fields separated by single space
- Paths are relative to repo root (for --porcelain)

### Status Code Table

| X | Y | Meaning |
|---|---|---------|
| ` ` | `M` | Modified in working tree, not staged |
| `M` | ` ` | Modified and staged, working tree clean |
| `M` | `M` | Modified staged AND modified again in working tree |
| `A` | ` ` | New file, staged |
| `A` | `M` | New file staged, then modified in working tree |
| `D` | ` ` | Deleted and staged |
| ` ` | `D` | Deleted in working tree, not staged |
| `R` | ` ` | Renamed and staged |
| `?` | `?` | Untracked |
| `!` | `!` | Ignored |

### Sapling to Git Mapping

| sl Code | Meaning | Git XY | Rationale |
|---------|---------|--------|-----------|
| `M` | Modified | ` M` | sl has no staging, treat as unstaged modification |
| `A` | Added | `A ` | Added files in sl are "pending", similar to staged |
| `R` | Removed | `D ` | Removed files in sl are "pending deletion", similar to staged |
| `?` | Unknown | `??` | Direct mapping for untracked |
| `!` | Missing | ` D` | File deleted but not via sl rm - unstaged deletion |
| `C` | Clean | (not shown) | Clean files don't appear in status |
| `I` | Ignored | `!!` | Only shown with --ignored flag |

### Rename Handling

**Git format:** `R  original.txt -> renamed.txt`
**Sapling format:**
```
A renamed.txt
R original.txt
```

For MVP, we emit two separate lines matching sl's output structure:
- `A  renamed.txt` (treated as new file)
- `D  original.txt` (treated as deletion)

This is semantically correct and tools typically handle both representations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Full git status emulation | All possible XY combinations | Only codes sl produces | sl doesn't have staging area |
| Complex argument parsing | Custom flag parser | Simple `in` checks | Only need --porcelain, --short, -s |
| Rename detection | Cross-referencing add/remove | Separate A/D lines | Simpler, still correct |
| Output coloring | ANSI escape codes | Let terminal handle | --porcelain is always uncolored |

**Key insight:** Since Sapling has no staging area, many git status combinations (like `MM`, `AM`, `AD`) are impossible to produce. We only need to handle the single-character codes Sapling actually outputs.

## Common Pitfalls

### Pitfall 1: Forgetting the Space Between XY and Filename
**What goes wrong:** Output like `M filename` instead of ` M filename`
**Why it happens:** Git uses 2-char XY code, easy to output 1 char
**How to avoid:** Always output exactly 2 characters plus space: `f"{git_code} {filename}"`
**Warning signs:** Byte-for-byte comparison fails, tools parsing porcelain break

### Pitfall 2: Wrong Mapping for Modified Files
**What goes wrong:** Using `M ` instead of ` M` for modified files
**Why it happens:** Thinking sl's modified = git's staged modified
**How to avoid:** Remember sl has no staging - modified means working tree change only
**Warning signs:** Tools like get-shit-done skip `git add` step incorrectly

### Pitfall 3: Breaking Passthrough for Normal Status
**What goes wrong:** All status commands go through transformation
**Why it happens:** Checking for flags incorrectly, not returning early
**How to avoid:** Only transform when `--porcelain`, `--short`, or `-s` present
**Warning signs:** Normal `git status` output looks different than expected

### Pitfall 4: Missing Newline at End
**What goes wrong:** No trailing newline after last line
**Why it happens:** Using `print()` without newline or `join()` without final newline
**How to avoid:** Explicitly add newline: `'\n'.join(lines) + '\n'`
**Warning signs:** Some tools wait for newline, appear to hang

### Pitfall 5: Not Handling Empty Status
**What goes wrong:** Output contains extraneous newline or characters
**Why it happens:** Unconditionally adding newlines/prefixes
**How to avoid:** Check for empty lines list before outputting
**Warning signs:** Clean repo outputs something instead of nothing

## Code Examples

### Complete Status Code Mapping
```python
# Source: Direct CLI testing comparing git and sl outputs

SL_TO_GIT_STATUS = {
    'M': ' M',  # Modified in working tree (not staged - sl has no staging)
    'A': 'A ',  # Added (will be committed - equivalent to staged in git)
    'R': 'D ',  # Removed (will be deleted - equivalent to staged deletion)
    '?': '??',  # Unknown/untracked
    '!': ' D',  # Missing (deleted from disk, but not via sl rm)
    'I': '!!',  # Ignored (only with --ignored flag)
}
```

### Parsing sl Status Line
```python
def parse_sl_status_line(line: str) -> tuple:
    """
    Parse a single sl status line.

    Args:
        line: Single line from sl status output, e.g., "M filename.txt"

    Returns:
        Tuple of (status_code, filename) or (None, None) if invalid

    Format: "X filename" where X is single char status
    """
    if not line or len(line) < 3:  # Minimum: "X f"
        return None, None

    if line[1] != ' ':  # Second char must be space
        return None, None

    status_code = line[0]
    filename = line[2:]

    return status_code, filename
```

### Full Transform Function
```python
def transform_to_porcelain(sl_output: str) -> str:
    """
    Transform sl status output to git porcelain v1 format.

    sl format:  "X filename" (1 char + space + filename)
    git format: "XY filename" (2 chars + space + filename)

    Args:
        sl_output: Complete output from 'sl status' command

    Returns:
        Git-compatible porcelain format output
    """
    lines = []

    for line in sl_output.splitlines():
        status_code, filename = parse_sl_status_line(line)

        if status_code is None:
            continue

        # Map sl status to git XY code
        git_code = SL_TO_GIT_STATUS.get(status_code, '??')

        # Format: XY<space>filename
        lines.append(f"{git_code} {filename}")

    # Return with trailing newline if there's content
    if lines:
        return '\n'.join(lines) + '\n'
    return ''
```

### Test Pattern for Exact Match
```python
def test_porcelain_untracked_file():
    """
    Untracked file shows as '?? filename'.

    E2E test that verifies exact byte-for-byte format match.
    """
    # Setup: sl repo with untracked file
    result = run_gitsl(['status', '--porcelain'], cwd=sl_repo_with_untracked)

    # Verify format: exactly "?? filename\n"
    assert result.stdout == "?? untracked.txt\n"
    assert result.exit_code == 0
```

## Test Scenarios Required

Based on phase requirements, these scenarios must be tested:

### Scenario 1: New/Added File
```
sl: A new_file.txt
git: A  new_file.txt
```

### Scenario 2: Modified File
```
sl: M existing.txt
git:  M existing.txt
```

### Scenario 3: Deleted File (via sl rm)
```
sl: R deleted.txt
git: D  deleted.txt
```

### Scenario 4: Renamed File
```
sl: A renamed.txt
    R original.txt
git: A  renamed.txt
     D  original.txt
```
(Note: Not attempting to reconstruct git's `R  original -> renamed` format)

### Scenario 5: Untracked File
```
sl: ? untracked.txt
git: ?? untracked.txt
```

### Scenario 6: Missing File (deleted without sl rm)
```
sl: ! missing.txt
git:  D missing.txt
```

### Scenario 7: Mixed States
Multiple files with different states - verify all are transformed correctly.

### Scenario 8: Empty Status (Clean Repo)
Both sl and git output should be empty string.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Simple passthrough | Output transformation | Phase 6 | Enables tooling compatibility |

**This is new functionality** - no prior implementation exists in gitsl.

## Open Questions

1. **Rename Detection Enhancement**
   - What we know: sl shows renames as A+R, git shows as single R line
   - What's unclear: Whether tools require the git R format specifically
   - Recommendation: Start with A+D mapping, enhance if needed based on real-world testing

2. **-v Flag Handling**
   - What we know: git status -v shows diff content with status
   - What's unclear: Whether this is needed for get-shit-done
   - Recommendation: Out of scope for Phase 6, passthrough to sl

3. **Branch Header (-b flag)**
   - What we know: git status -sb shows branch info: `## branch...tracking`
   - What's unclear: Whether get-shit-done uses this
   - Recommendation: Out of scope for Phase 6 MVP

## Sources

### Primary (HIGH confidence)
- [Git status documentation](https://git-scm.com/docs/git-status) - Official porcelain format spec
- Direct CLI testing - Compared actual git and sl outputs on local system
- Existing codebase - cmd_rev_parse.py pattern for capture_output

### Secondary (MEDIUM confidence)
- [Git status short vs porcelain comparison](https://www.stefanjudis.com/today-i-learned/the-short-version-of-git-status-and-the-close-but-different-porcelain-mode/) - Differences between formats
- .planning/research/FEATURES.md - Prior research on status translation

### Tertiary (LOW confidence)
- None - all findings verified with direct CLI testing

## Metadata

**Confidence breakdown:**
- Status code mapping: HIGH - Verified with actual CLI output comparisons
- Output format: HIGH - Byte-for-byte verified with cat -A
- Architecture: HIGH - Follows established capture_output pattern from cmd_rev_parse.py
- Test patterns: HIGH - Uses existing test infrastructure

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable formats, no external API changes expected)
