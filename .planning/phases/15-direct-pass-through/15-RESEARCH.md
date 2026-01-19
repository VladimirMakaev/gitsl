# Phase 15: Direct Pass-through Commands - Research

**Researched:** 2026-01-19
**Domain:** Git-to-Sapling command translation for show, blame, rm, mv, clone, grep
**Confidence:** HIGH

## Summary

Phase 15 implements six git commands that translate directly to Sapling equivalents with minimal transformation. These commands follow the established `cmd_*.py` pattern from earlier phases. All six commands have direct Sapling counterparts with compatible semantics:

- `git show` -> `sl show` (identical command name)
- `git blame` -> `sl annotate` (command name change, sl has `blame` as alias)
- `git rm` -> `sl remove` (command name change, sl has `rm` as alias)
- `git mv` -> `sl rename` (command name change, sl has `mv` as alias)
- `git clone` -> `sl clone` (identical command name)
- `git grep` -> `sl grep` (identical command name)

The existing infrastructure from Phase 3 and Phase 4 provides all necessary patterns. Most flags pass through directly. Some git flags (like `git rm -r`) require special handling because Sapling behaves differently (recursive by default).

**Primary recommendation:** Create six new handler files (`cmd_show.py`, `cmd_blame.py`, `cmd_rm.py`, `cmd_mv.py`, `cmd_clone.py`, `cmd_grep.py`) following the established `cmd_diff.py` pattern for simple passthrough commands. Update `gitsl.py` dispatch to route to these handlers.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already established in common.py |
| sys | stdlib | Exit codes, stdout writing | Already in use |
| typing | stdlib | Type hints | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| dataclasses | stdlib | ParsedCommand | Already defined in common.py |
| common.run_sl | local | Subprocess passthrough | All simple handlers |

**Installation:**
```bash
# No new dependencies - all patterns established in Phase 3
```

## Architecture Patterns

### Current Project Structure
```
gitsl/
├── gitsl.py           # Entry point with dispatch
├── common.py          # ParsedCommand, run_sl(), debug helpers
├── cmd_status.py      # Handler for 'git status'
├── cmd_log.py         # Handler for 'git log'
├── cmd_diff.py        # Handler for 'git diff'
├── cmd_init.py        # Handler for 'git init'
├── cmd_rev_parse.py   # Handler for 'git rev-parse'
├── cmd_add.py         # Handler for 'git add'
├── cmd_commit.py      # Handler for 'git commit'
└── tests/
    ├── conftest.py    # Fixtures: git_repo, sl_repo, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # Comparison helpers
    └── test_*.py      # E2E tests
```

### Pattern 1: Simple Command Name Translation
**What:** Commands where git and sl use same command name
**When to use:** For show, clone, grep
**Example:**
```python
# cmd_show.py
"""Handler for 'git show' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git show' command.

    Translates to 'sl show' and passes through all arguments.
    """
    return run_sl(["show"] + parsed.args)
```

### Pattern 2: Command Name Mapping
**What:** Commands where git and sl use different command names
**When to use:** For blame->annotate, rm->remove, mv->rename
**Example:**
```python
# cmd_blame.py
"""Handler for 'git blame' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git blame' command.

    Translates to 'sl annotate' and passes through arguments.
    Note: sl has 'blame' as an alias for 'annotate'.
    """
    return run_sl(["annotate"] + parsed.args)
```

### Pattern 3: Flag Filtering
**What:** Commands that need to filter or ignore certain git flags
**When to use:** For rm -r (Sapling is recursive by default)
**Example:**
```python
# cmd_rm.py
"""Handler for 'git rm' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rm' command.

    Translations:
    - git rm <files>  -> sl remove <files>
    - git rm -f       -> sl remove -f
    - git rm -r       -> sl remove (recursive by default)
    """
    # Filter out -r flag - sl remove is recursive by default
    filtered_args = [a for a in parsed.args if a not in ('-r', '--recursive')]
    return run_sl(["remove"] + filtered_args)
```

### Anti-Patterns to Avoid
- **Using `annotate` alias `blame`:** Although sl has `blame` as alias, use canonical `annotate` for clarity
- **Using `rename` alias `mv`:** Use canonical `rename` for clarity in code
- **Using `remove` alias `rm`:** Use canonical `remove` for clarity in code
- **Capturing output when passthrough works:** Only capture if transformation needed

## Command Mappings Analysis

### SHOW-01, SHOW-02: git show -> sl show

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git show` | `sl show` | YES - direct |
| Default | Shows HEAD commit | Shows current commit | YES |
| `git show <commit>` | Shows specified commit | Shows specified commit | YES |
| Common flags | --stat, -p, --format | --stat, -g (git format) | Partial |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via CLI):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| --stat | --stat | Same flag, same behavior |
| -p (patch) | Default behavior | sl show includes diff by default |
| --format | -T/--template | Different syntax |
| -U<n> | -U/--unified | Same behavior |
| -w | -w/--ignore-all-space | Same flag |

**Implementation:** Simple passthrough - `run_sl(["show"] + parsed.args)`

### BLAME-01, BLAME-02: git blame -> sl annotate

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git blame <file>` | `sl annotate <file>` | Name change |
| Output format | rev author date line | changeset user date line | Similar |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via `sl help annotate`):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -L <start>,<end> | Not directly supported | Would need translation |
| -w | -w/--ignore-all-space | Same flag, same behavior |
| -b | -b/--ignore-space-change | Same flag, same behavior |
| -n | -n/--number | Shows revision number (different meaning) |
| -l | -l/--line-number | Same flag, same behavior |

**Important:** git `-L` for line ranges is NOT supported by sl annotate. For v1.2 scope, we pass through common flags (-w, -b) but do not translate -L.

**Implementation:** Command name mapping - `run_sl(["annotate"] + parsed.args)`

### RM-01, RM-02, RM-03: git rm -> sl remove

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git rm <files>` | `sl remove <files>` | Name change |
| -f/--force | -f/--force | Same flag, same behavior |
| -r (recursive) | Default behavior | sl remove is recursive by default |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via `sl help remove`):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -f, --force | -f, --force | Same behavior |
| -r | Not needed | sl remove handles dirs recursively by default |
| --cached | -A (keep in working dir) | Similar but not identical |
| -n, --dry-run | Not supported | Would need custom implementation |

**Implementation:** Filter out `-r` flag, pass rest through.

```python
filtered_args = [a for a in parsed.args if a not in ('-r', '--recursive')]
return run_sl(["remove"] + filtered_args)
```

### MV-01, MV-02: git mv -> sl rename

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git mv <src> <dst>` | `sl rename <src> <dst>` | Name change |
| -f/--force | -f/--force | Same flag |
| -n/--dry-run | -n/--dry-run | Same flag |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via `sl help rename`):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -f, --force | -f, --force | Same behavior |
| -n, --dry-run | -n, --dry-run | Same behavior |
| -k | Not supported | Skip errors |
| -v, --verbose | Not supported | Verbose output |

**Implementation:** Simple command mapping - `run_sl(["rename"] + parsed.args)`

### CLONE-01, CLONE-02: git clone -> sl clone

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git clone <url>` | `sl clone <url>` | YES - direct |
| `git clone <url> <dir>` | `sl clone <url> <dir>` | YES - direct |
| Exit code | 0 on success | 0 on success | YES |

**Flag compatibility (verified via `sl help clone`):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -b <branch> | -u/--updaterev | Check out specific revision |
| --depth | Not supported | Shallow clone not in same way |
| --bare | Not supported | Different concept |

**Implementation:** Simple passthrough - `run_sl(["clone"] + parsed.args)`

### GREP-01, GREP-02: git grep -> sl grep

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git grep <pattern>` | `sl grep <pattern>` | YES - direct |
| Exit code | 0 if matches, 1 if no match | 0 on success | May differ |

**Flag compatibility (verified via `sl help grep`):**
| git flag | sl equivalent | Notes |
|----------|---------------|-------|
| -n, --line-number | -n, --line-number | Same flag |
| -i, --ignore-case | -i, --ignore-case | Same flag |
| -l, --files-with-matches | -l, --files-with-matches | Same flag |
| -A <num> | -A, --after-context | Same flag |
| -B <num> | -B, --before-context | Same flag |
| -C <num> | -C, --context | Same flag |
| -w, --word-regexp | -w, --word-regexp | Same flag |
| -E, --extended-regexp | -E, --extended-regexp | Same flag |
| -F, --fixed-strings | -F, --fixed-strings | Same flag |
| -P, --perl-regexp | -P, --perl-regexp | Same flag |
| -v, --invert-match | -V, --invert-match | Different case! |

**Important:** git uses `-v` for invert-match, sl uses `-V`. This would need translation for full compatibility, but v1.2 scope focuses on -n, -i, -l which pass through directly.

**Implementation:** Simple passthrough - `run_sl(["grep"] + parsed.args)`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Command dispatch | Manual if/elif in main | Separate cmd_*.py files | ARCH-03 compliance |
| Subprocess passthrough | Custom pipe handling | run_sl() from common.py | Already tested |
| Exit code propagation | Custom error handling | Return subprocess returncode | Established pattern |
| Test fixtures | Manual repo setup | sl_repo fixtures from conftest.py | Already available |

**Key insight:** All six commands follow established patterns. No new infrastructure needed.

## Common Pitfalls

### Pitfall 1: Using Command Aliases Instead of Canonical Names
**What goes wrong:** Code becomes harder to understand
**Why it happens:** sl has aliases (blame=annotate, rm=remove, mv=rename)
**How to avoid:** Always use canonical names in code: `annotate`, `remove`, `rename`
**Warning signs:** Code shows `run_sl(["blame"])` instead of `run_sl(["annotate"])`

### Pitfall 2: Forgetting rm -r Flag Handling
**What goes wrong:** sl errors or unexpected behavior
**Why it happens:** git requires -r for recursive, sl doesn't
**How to avoid:** Filter out -r flag in cmd_rm.py handler
**Warning signs:** Tests with `git rm -r dir/` fail

### Pitfall 3: Not Testing in Sapling Repository
**What goes wrong:** Tests pass but actual usage fails
**Why it happens:** Using git_repo fixture instead of sl_repo
**How to avoid:** Use sl_repo_with_commit fixture for E2E tests
**Warning signs:** "not a repository" errors when testing

### Pitfall 4: Assuming All Flags Pass Through
**What goes wrong:** Silent failures or wrong behavior
**Why it happens:** Assuming git and sl have identical flags
**How to avoid:** Check flag compatibility table before passing through
**Warning signs:** `git grep -v pattern` (invert) doesn't work as expected

### Pitfall 5: Testing Clone in Existing Repository
**What goes wrong:** Clone tests fail
**Why it happens:** Clone needs clean directory, not existing repo
**How to avoid:** Use tmp_path directly for clone tests, not sl_repo fixture
**Warning signs:** "destination already exists" errors

## Code Examples

### cmd_show.py
```python
"""Handler for 'git show' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git show' command.

    Translations:
    - git show          -> sl show (current commit)
    - git show <commit> -> sl show <commit>

    Common flags pass through: --stat, -U<n>, -w
    """
    return run_sl(["show"] + parsed.args)
```

### cmd_blame.py
```python
"""Handler for 'git blame' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git blame' command.

    Translations:
    - git blame <file>    -> sl annotate <file>
    - git blame -w <file> -> sl annotate -w <file>

    Note: sl has 'blame' as an alias for 'annotate'.
    """
    return run_sl(["annotate"] + parsed.args)
```

### cmd_rm.py
```python
"""Handler for 'git rm' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rm' command.

    Translations:
    - git rm <files>   -> sl remove <files>
    - git rm -f        -> sl remove -f
    - git rm -r        -> sl remove (recursive by default)
    """
    # Filter out -r/--recursive - sl remove is recursive by default
    filtered_args = [a for a in parsed.args if a not in ('-r', '--recursive')]
    return run_sl(["remove"] + filtered_args)
```

### cmd_mv.py
```python
"""Handler for 'git mv' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git mv' command.

    Translations:
    - git mv <src> <dst> -> sl rename <src> <dst>
    - git mv -f          -> sl rename -f
    """
    return run_sl(["rename"] + parsed.args)
```

### cmd_clone.py
```python
"""Handler for 'git clone' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clone' command.

    Translations:
    - git clone <url>       -> sl clone <url>
    - git clone <url> <dir> -> sl clone <url> <dir>
    """
    return run_sl(["clone"] + parsed.args)
```

### cmd_grep.py
```python
"""Handler for 'git grep' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git grep' command.

    Translations:
    - git grep <pattern>     -> sl grep <pattern>
    - git grep -n <pattern>  -> sl grep -n <pattern>
    - git grep -i <pattern>  -> sl grep -i <pattern>
    - git grep -l <pattern>  -> sl grep -l <pattern>
    """
    return run_sl(["grep"] + parsed.args)
```

### Updated gitsl.py Dispatch
```python
# Add imports at top
import cmd_show
import cmd_blame
import cmd_rm
import cmd_mv
import cmd_clone
import cmd_grep

# In main(), add dispatch cases:
if parsed.command == "show":
    return cmd_show.handle(parsed)

if parsed.command == "blame":
    return cmd_blame.handle(parsed)

if parsed.command == "rm":
    return cmd_rm.handle(parsed)

if parsed.command == "mv":
    return cmd_mv.handle(parsed)

if parsed.command == "clone":
    return cmd_clone.handle(parsed)

if parsed.command == "grep":
    return cmd_grep.handle(parsed)
```

## Test Patterns

### E2E Test for show
```python
"""E2E tests for git show command (SHOW-01, SHOW-02)."""

import shutil
from pathlib import Path
import pytest
from conftest import run_gitsl
from helpers.commands import run_command

sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.show,
]


class TestShowBasic:
    """SHOW-01: git show translates to sl show."""

    def test_show_current_commit(self, sl_repo_with_commit: Path):
        """git show displays current commit."""
        result = run_gitsl(["show"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show commit info
        assert "commit" in result.stdout.lower() or result.stdout != ""


class TestShowCommit:
    """SHOW-02: git show <commit> shows specified commit."""

    def test_show_specific_commit(self, sl_repo_with_commit: Path):
        """git show <hash> displays that commit."""
        # Get current commit hash
        hash_result = run_command(["sl", "whereami"], cwd=sl_repo_with_commit)
        commit_hash = hash_result.stdout.strip()[:12]

        result = run_gitsl(["show", commit_hash], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
```

### E2E Test for blame
```python
"""E2E tests for git blame command (BLAME-01, BLAME-02)."""

import shutil
from pathlib import Path
import pytest
from conftest import run_gitsl

sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.blame,
]


class TestBlameBasic:
    """BLAME-01: git blame <file> translates to sl annotate <file>."""

    def test_blame_file(self, sl_repo_with_commit: Path):
        """git blame shows per-line annotations."""
        result = run_gitsl(["blame", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show content with annotations
        assert "README" in result.stdout or result.stdout != ""


class TestBlameFlags:
    """BLAME-02: git blame passes through common flags."""

    def test_blame_ignore_whitespace(self, sl_repo_with_commit: Path):
        """git blame -w ignores whitespace changes."""
        result = run_gitsl(["blame", "-w", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
```

### E2E Test for rm
```python
"""E2E tests for git rm command (RM-01, RM-02, RM-03)."""

import shutil
from pathlib import Path
import pytest
from conftest import run_gitsl
from helpers.commands import run_command

sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.rm,
]


class TestRmBasic:
    """RM-01: git rm <files> translates to sl remove <files>."""

    def test_rm_tracked_file(self, sl_repo_with_commit: Path):
        """git rm removes tracked file."""
        result = run_gitsl(["rm", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify file is marked for removal
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout


class TestRmForce:
    """RM-02: git rm -f translates to sl remove -f."""

    def test_rm_force(self, sl_repo_with_commit: Path):
        """git rm -f forces removal of modified file."""
        # Modify the file first
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("Modified content\n")

        result = run_gitsl(["rm", "-f", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestRmRecursive:
    """RM-03: git rm -r translates to sl remove (recursive by default)."""

    def test_rm_recursive(self, sl_repo_with_commit: Path):
        """git rm -r removes directory recursively."""
        # Create a subdirectory with files
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        subfile = subdir / "file.txt"
        subfile.write_text("content\n")
        run_command(["sl", "add", "subdir/file.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rm", "-r", "subdir"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
```

### E2E Test for clone
```python
"""E2E tests for git clone command (CLONE-01, CLONE-02)."""

import shutil
from pathlib import Path
import pytest
from conftest import run_gitsl
from helpers.commands import run_command

sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clone,
]


class TestCloneUrl:
    """CLONE-01: git clone <url> translates to sl clone <url>."""

    def test_clone_local_repo(self, sl_repo_with_commit: Path, tmp_path: Path):
        """git clone can clone a local repository."""
        dest = tmp_path / "cloned"
        result = run_gitsl(["clone", str(sl_repo_with_commit), str(dest)], cwd=tmp_path)
        assert result.exit_code == 0
        assert dest.exists()
        assert (dest / ".hg").exists()


class TestCloneDir:
    """CLONE-02: git clone <url> <dir> translates to sl clone <url> <dir>."""

    def test_clone_with_destination(self, sl_repo_with_commit: Path, tmp_path: Path):
        """git clone can specify destination directory."""
        result = run_gitsl(["clone", str(sl_repo_with_commit), "my-clone"], cwd=tmp_path)
        assert result.exit_code == 0
        assert (tmp_path / "my-clone").exists()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A - new phase | cmd_*.py handler pattern | Established Phase 3 | All handlers follow same pattern |

**This phase extends existing patterns.** No new architectural decisions needed.

## Open Questions

1. **git grep -v vs sl grep -V**
   - What we know: git uses lowercase `-v` for invert, sl uses uppercase `-V`
   - What's unclear: Whether to translate this flag automatically
   - Recommendation: Document as known limitation for v1.2, defer flag translation

2. **git blame -L line range**
   - What we know: sl annotate does not support `-L` flag
   - What's unclear: How important this is for users
   - Recommendation: Document as unsupported, pass through and let sl error

3. **Clone remote repository testing**
   - What we know: Local clone works, remote clone needs network
   - What's unclear: How to test remote clone in CI
   - Recommendation: Test local clone only, document that remote works same way

## Sources

### Primary (HIGH confidence)
- Sapling CLI help: `sl help show`, `sl help annotate`, `sl help remove`, `sl help rename`, `sl help clone`, `sl help grep` - Verified all command flags and behavior
- Git manual pages: `git show --help`, `git blame --help`, `git rm --help`, `git mv --help`, `git clone --help`, `git grep --help` - Reference behavior
- Existing codebase: cmd_diff.py, cmd_add.py, cmd_log.py - Pattern templates

### Secondary (MEDIUM confidence)
- [Sapling show documentation](https://sapling-scm.com/docs/commands/show/) - WebFetch verified
- [Sapling annotate documentation](https://sapling-scm.com/docs/commands/annotate/) - WebFetch verified
- [Sapling remove documentation](https://sapling-scm.com/docs/commands/remove/) - WebFetch verified
- [Sapling clone documentation](https://sapling-scm.com/docs/commands/clone/) - WebFetch verified

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 3, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern exactly
- Command mappings: HIGH - Verified via CLI help and direct testing
- Pitfalls: HIGH - Based on actual codebase analysis and flag comparison

**Research date:** 2026-01-19
**Valid until:** 2026-02-19 (30 days - stable patterns, no external API changes expected)
