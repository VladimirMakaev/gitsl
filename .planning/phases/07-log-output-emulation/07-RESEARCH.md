# Phase 7: Log Output Emulation - Research

**Researched:** 2026-01-18
**Domain:** Git log flag translation and output format emulation
**Confidence:** HIGH

## Summary

Phase 7 extends cmd_log.py to handle two git log flags: `--oneline` for compact output format and `-N` for limiting commit count. The current implementation passes through all arguments to `sl log` directly, which works for basic usage but fails for these git-specific flags.

The `--oneline` flag requires output transformation using Sapling's template system (`-T '{node|short} {desc|firstline}\n'`). The `-N` flag (and variants `-n N`, `--max-count=N`) requires translation to Sapling's `-l N` flag. When combined, both transformations must work together.

Key insight: The roadmap explicitly permits "semantic" matching for `--oneline` format, meaning hash length differences (git=7 chars, sl=12 chars) are acceptable. This simplifies implementation since we can use sl's native `{node|short}` without truncation.

**Primary recommendation:** Modify cmd_log.py to parse `--oneline` and `-N`/`-n`/`--max-count` flags, translate them to sl equivalents (`-T template` and `-l N`), and pass remaining arguments through unchanged.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already established in common.py |
| sys | stdlib | Exit codes | Already in use |
| re | stdlib | Pattern matching for -N flags | Precise number extraction |
| typing | stdlib | Type hints | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| dataclasses | stdlib | ParsedCommand | Already defined in common.py |

**Installation:**
```bash
# No new dependencies - all patterns established in Phase 3-4
```

## Architecture Patterns

### Current cmd_log.py
```python
"""Handler for 'git log' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translates to 'sl log' and passes through all arguments.
    """
    return run_sl(["log"] + parsed.args)
```

### Pattern 1: Flag Detection and Translation
**What:** Parse incoming git flags, translate to sl equivalents, build new arg list
**When to use:** For --oneline and -N flag translation

**Example:**
```python
# Source: Established pattern from cmd_add.py for flag translation
def handle(parsed: ParsedCommand) -> int:
    """Handle git log with flag translation."""
    sl_args = ["log"]
    remaining_args = []

    # Process each argument
    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        if arg == "--oneline":
            # Translate to sl template
            sl_args.extend(["-T", "{node|short} {desc|firstline}\\n"])
        elif arg.startswith("-") and arg[1:].isdigit():
            # Handle -N format (e.g., -5)
            limit = arg[1:]
            sl_args.extend(["-l", limit])
        else:
            remaining_args.append(arg)

        i += 1

    return run_sl(sl_args + remaining_args)
```

### Pattern 2: Multiple -N Flag Formats
**What:** Git accepts multiple formats for commit limit
**When to use:** Must handle all these variations

| Git Format | Example | Translation |
|------------|---------|-------------|
| `-N` | `-5` | `-l 5` |
| `-n N` | `-n 5` | `-l 5` |
| `-nN` | `-n5` | `-l 5` |
| `--max-count=N` | `--max-count=5` | `-l 5` |

**Regex approach:**
```python
import re

# Match -N where N is one or more digits
if re.match(r'^-(\d+)$', arg):
    limit = arg[1:]  # Extract digits after -
    sl_args.extend(["-l", limit])

# Match -n followed by space or attached number
elif arg == "-n":
    # Next arg should be the number
    limit = parsed.args[i + 1]
    sl_args.extend(["-l", limit])
    i += 1  # Skip next arg

elif arg.startswith("-n") and arg[2:].isdigit():
    # -n5 format
    limit = arg[2:]
    sl_args.extend(["-l", limit])

elif arg.startswith("--max-count="):
    limit = arg.split("=")[1]
    sl_args.extend(["-l", limit])
```

### Pattern 3: Combined Flags
**What:** User can combine --oneline with -N in any order
**When to use:** Both flags present in same command

```bash
# All these should work:
git log --oneline -5
git log -5 --oneline
git log --oneline -n 5
git log -n5 --oneline
```

**Implementation:** Process all flags in order, accumulate sl_args, then combine.

### Anti-Patterns to Avoid

- **Hardcoding hash length:** Don't truncate sl's 12-char hash to match git's 7-char. Roadmap says semantic match is acceptable.

- **Breaking passthrough:** When neither --oneline nor -N is present, command should work exactly as before (full passthrough).

- **Order sensitivity:** Don't assume flags come in specific order. `--oneline -5` and `-5 --oneline` must both work.

- **Forgetting edge cases:** Empty log (no commits), single commit, limit > available commits.

## Git Log Flag Analysis

### --oneline Flag

**Git behavior (verified locally):**
```
$ git log --oneline
36b99d3 Second commit
57a57eb Initial commit
```

Format: `<7-char-hash><space><first-line-of-message>`

**Sapling equivalent (verified locally):**
```bash
sl log -T '{node|short} {desc|firstline}\n'
```

Output:
```
9147bf4b02f1 Second commit
bffd9b7632a6 Initial commit
```

Format: `<12-char-hash><space><first-line-of-message>`

**Difference:** Hash length only. Per ROADMAP: "semantic: hash length may differ" is acceptable.

### -N Flag

**Git behavior (verified locally):**
```
# All equivalent:
git log -5
git log -n 5
git log -n5
git log --max-count=5
```

**Sapling equivalent (verified locally):**
```bash
# All equivalent:
sl log -l 5
sl log -l5
sl log --limit 5
```

**Note:** sl uses `-l` (limit), not `-n`. Direct passthrough of `-5` or `-n 5` will fail.

### Combined Flags

**Git behavior (verified locally):**
```
git log --oneline -5
git log -5 --oneline
```

Both produce same output (5 commits in oneline format).

**Sapling equivalent:**
```bash
sl log -T '{node|short} {desc|firstline}\n' -l 5
```

Order of `-T` and `-l` flags does not matter.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Output format parsing | Regex on git output | sl template system | sl's `-T` is exact and reliable |
| Flag parsing library | Custom argparse | Simple iteration | Git flags have known patterns, complexity not needed |
| Hash truncation | Custom string slicing | sl's `{node\|short}` | Built-in, handles edge cases |

**Key insight:** Sapling's template system is powerful enough to produce git-like output directly. Don't parse and transform output - generate correct format from the start.

## Common Pitfalls

### Pitfall 1: Forgetting the Newline in Template
**What goes wrong:** Output runs together without line breaks
**Why it happens:** Template needs explicit `\n`
**How to avoid:** Always include `\n` at end of template: `'{node|short} {desc|firstline}\n'`
**Warning signs:** All commits on single line

### Pitfall 2: Missing -n N Case (Space Between)
**What goes wrong:** `-n 5` fails or produces wrong output
**Why it happens:** Only handling `-n5` (attached) format
**How to avoid:** Check if arg == "-n", then consume next arg as number
**Warning signs:** `-n 5` works differently than `-n5`

### Pitfall 3: Breaking Existing Passthrough
**What goes wrong:** Basic `git log` (no flags) stops working
**Why it happens:** Flag detection code consumes all args or breaks flow
**How to avoid:** Only intercept known flags, pass everything else unchanged
**Warning signs:** `git log` produces no output or errors

### Pitfall 4: Escaping Template String
**What goes wrong:** Shell or Python consumes template characters
**Why it happens:** `{` and `}` may need escaping depending on context
**How to avoid:** Use raw strings or proper escaping. In Python list args, no shell involved.
**Warning signs:** Template literal appears in output or error about invalid template

### Pitfall 5: Not Handling Empty Repo
**What goes wrong:** Test fails on repo with no commits
**Why it happens:** `git log --oneline` on empty repo exits with code 128
**How to avoid:** Test both success and error cases
**Warning signs:** Tests fail on fresh repos

## Code Examples

### Complete Handler: cmd_log.py (Updated)

```python
"""Handler for 'git log' command."""

import re
from common import ParsedCommand, run_sl


# Template for --oneline format
# Uses sl's {node|short} (12 chars) - semantic match per ROADMAP
ONELINE_TEMPLATE = "{node|short} {desc|firstline}\\n"


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translations:
    - git log --oneline -> sl log -T '<template>'
    - git log -N -> sl log -l N
    - git log -n N -> sl log -l N
    - git log -nN -> sl log -l N
    - git log --max-count=N -> sl log -l N

    All other arguments pass through unchanged.
    """
    sl_args = ["log"]
    remaining_args = []
    use_oneline = False
    limit = None

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # --oneline flag
        if arg == "--oneline":
            use_oneline = True

        # -N format (e.g., -5, -10)
        elif re.match(r'^-(\d+)$', arg):
            limit = arg[1:]

        # -n N format (space between)
        elif arg == "-n":
            if i + 1 < len(parsed.args):
                limit = parsed.args[i + 1]
                i += 1

        # -nN format (attached number)
        elif arg.startswith("-n") and len(arg) > 2 and arg[2:].isdigit():
            limit = arg[2:]

        # --max-count=N format
        elif arg.startswith("--max-count="):
            limit = arg.split("=", 1)[1]

        # Everything else passes through
        else:
            remaining_args.append(arg)

        i += 1

    # Build sl command
    if use_oneline:
        sl_args.extend(["-T", ONELINE_TEMPLATE])

    if limit is not None:
        sl_args.extend(["-l", limit])

    sl_args.extend(remaining_args)

    return run_sl(sl_args)
```

### E2E Test Examples

```python
"""E2E tests for git log --oneline and -N flags."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestLogOneline:
    """FLAG-04: git log --oneline emulates git oneline format."""

    def test_oneline_returns_hash_and_subject(self, sl_repo_with_commit: Path):
        """--oneline shows hash and subject."""
        result = run_gitsl(["log", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1

        # Each line should be: <hash> <subject>
        for line in lines:
            parts = line.split(" ", 1)
            assert len(parts) == 2, f"Expected 'hash subject', got: {line}"
            hash_part, subject = parts
            # Hash should be hex characters (sl uses 12 chars)
            assert all(c in "0123456789abcdef" for c in hash_part)


class TestLogLimit:
    """FLAG-05: git log -N translates to sl log -l N."""

    def test_limit_with_dash_n(self, sl_repo_with_commits: Path):
        """-3 limits to 3 commits."""
        result = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3


class TestLogCombined:
    """Combined --oneline and -N flags."""

    def test_oneline_with_limit_either_order(self, sl_repo_with_commits: Path):
        """--oneline -5 and -5 --oneline produce same result."""
        result1 = run_gitsl(["log", "--oneline", "-3"], cwd=sl_repo_with_commits)
        result2 = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout
```

### Fixture for Multiple Commits

```python
# In conftest.py - new fixture
@pytest.fixture
def sl_repo_with_commits(sl_repo: Path) -> Path:
    """
    Sapling repo with 10 commits for testing limit flags.
    """
    for i in range(10):
        file_path = sl_repo / f"file{i}.txt"
        file_path.write_text(f"Content {i}")
        run_command(["sl", "add", str(file_path)], cwd=sl_repo)
        run_command(["sl", "commit", "-m", f"Commit {i}"], cwd=sl_repo)

    return sl_repo
```

## Testing Strategy

### Semantic Matching for --oneline

Per ROADMAP: "Test `--oneline` format matches git (semantic: hash length may differ)"

**Semantic match criteria:**
1. Each line has format: `<hash><space><subject>`
2. Hash is valid hex string (any length)
3. Subject matches commit message first line
4. Correct number of commits shown

**Not compared:**
- Hash length (git=7, sl=12)
- Exact hash values (different VCS)

### Test Fixture Requirements

The tests need:
1. `sl_repo_with_commit` - Already exists in conftest.py
2. `sl_repo_with_commits` - New fixture with 10 commits for limit testing

### Test Matrix

| Test Case | Input | Expected |
|-----------|-------|----------|
| Basic --oneline | `git log --oneline` | Each line: `<hash> <subject>` |
| -N format | `git log -3` | Exactly 3 commits |
| -n N format | `git log -n 3` | Exactly 3 commits |
| -nN format | `git log -n3` | Exactly 3 commits |
| --max-count=N | `git log --max-count=3` | Exactly 3 commits |
| Combined (order 1) | `git log --oneline -3` | 3 commits, oneline format |
| Combined (order 2) | `git log -3 --oneline` | 3 commits, oneline format |
| Limit > available | `git log -100` (only 10 exist) | All 10 commits |
| Passthrough (no flags) | `git log` | Default sl log output |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Full passthrough | Flag translation | Phase 7 | Enables --oneline and -N support |

**Current cmd_log.py:** Simple passthrough to sl log
**Updated cmd_log.py:** Parse known flags, translate, passthrough rest

## Open Questions

1. **Other git log flags**
   - What we know: git log has many more flags (--graph, --pretty, etc.)
   - What's unclear: Which ones might users need?
   - Recommendation: Out of scope for v1. Only implement --oneline and -N per requirements.

2. **Color output**
   - What we know: git log may output colors, sl log may differ
   - What's unclear: Whether this affects tooling
   - Recommendation: Accept sl's default color behavior. Most parsing tools use --no-color anyway.

3. **Revision ranges**
   - What we know: git log accepts revision ranges like `HEAD~3..HEAD`
   - What's unclear: Whether these work the same in sl
   - Recommendation: Passthrough revision args unchanged. Test if needed later.

## Sources

### Primary (HIGH confidence)
- Local CLI testing: Verified git and sl behavior with actual commands
- Existing codebase: cmd_add.py flag translation pattern, cmd_rev_parse.py output handling
- `sl help log` output: Template syntax `-T '{node|short} {desc|firstline}\n'`
- `sl help templates` output: Filter documentation (`|short`, `|firstline`)

### Secondary (MEDIUM confidence)
- ROADMAP.md: Success criteria specifying "semantic: hash length may differ"
- REQUIREMENTS.md: FLAG-04 and FLAG-05 specifications

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 3-4, no new dependencies
- Architecture: HIGH - Follows established flag translation pattern from cmd_add.py
- Pitfalls: HIGH - Based on actual CLI testing and template verification

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable patterns, no external API changes expected)
