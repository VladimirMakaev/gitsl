# Phase 17: Branch and Restore - Research

**Researched:** 2026-01-20
**Domain:** Git-to-Sapling command translation for branch management and file restoration
**Confidence:** HIGH

## Summary

Phase 17 implements two git commands that map to different Sapling equivalents:

- `git branch` -> `sl bookmark` (conceptual model difference: bookmarks are optional in Sapling, branches are fundamental in git)
- `git restore` -> `sl revert` (different command name, compatible behavior for working tree restoration)

The key challenge is the **bookmark model mismatch** between git and Sapling. In git, branches are fundamental and required for development workflow. In Sapling, bookmarks are "completely optional and generally not even used" - commits are visible via smartlog and accessible by hash without labels. This means `git branch` users expect certain behaviors that may not have exact Sapling equivalents.

Another critical difference: Sapling's `-D` flag for bookmark deletion is **destructive** - it strips/hides the associated commits. Git's `-D` only force-deletes the label. The gitsl translation must map both `git branch -d` and `git branch -D` to `sl bookmark -d` to preserve commits.

**Primary recommendation:** Create two handler files (`cmd_branch.py`, `cmd_restore.py`) that translate commands appropriately. The branch handler must use `sl bookmark -d` for both `-d` and `-D` flags to avoid accidentally destroying commits.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess | stdlib | Execute sl commands | Already established in common.py |
| sys | stdlib | Exit codes, stderr writing | Already in use |
| typing | stdlib | Type hints | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| dataclasses | stdlib | ParsedCommand | Already defined in common.py |
| common.run_sl | local | Subprocess passthrough | All handlers |

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
├── cmd_*.py           # Existing handlers (17 total after Phase 16)
└── tests/
    ├── conftest.py    # Fixtures: git_repo, sl_repo, etc.
    ├── helpers/
    │   ├── commands.py     # run_command(), CommandResult
    │   └── comparison.py   # Comparison helpers
    └── test_*.py      # E2E tests
```

### Pattern 1: Direct Command Name Translation
**What:** Map git command to Sapling equivalent with same semantics
**When to use:** For git restore -> sl revert (same purpose, different name)
**Example:**
```python
# cmd_restore.py
"""Handler for 'git restore' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git restore' command.

    Translations:
    - git restore <file>  -> sl revert <file>
    - git restore .       -> sl revert .
    - git restore --all   -> sl revert --all
    """
    # Direct passthrough with command name change
    return run_sl(["revert"] + list(parsed.args))
```

### Pattern 2: Subcommand-Based Dispatch
**What:** Different sl commands based on arguments present
**When to use:** For git branch (list vs create vs delete)
**Example:**
```python
# cmd_branch.py
"""Handler for 'git branch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git branch' command.

    Translations:
    - git branch              -> sl bookmark (list)
    - git branch <name>       -> sl bookmark <name> (create)
    - git branch -d <name>    -> sl bookmark -d <name> (delete)
    - git branch -D <name>    -> sl bookmark -d <name> (force delete, same as -d)
    """
    args = list(parsed.args)

    # Handle force delete: -D -> -d (avoid Sapling's destructive -D)
    if '-D' in args:
        args = ['-d' if a == '-D' else a for a in args]

    return run_sl(["bookmark"] + args)
```

### Pattern 3: Safety Translation (Avoiding Destructive Operations)
**What:** Translate git flags to safer Sapling equivalents
**When to use:** For git branch -D (which in git only removes label, but in Sapling strips commits)
**Example:**
```python
# CRITICAL: git branch -D just force-deletes the branch label
# Sapling bookmark -D strips/hides the associated commits!
# We MUST use -d for both to preserve commits.

if '-D' in args:
    args = ['-d' if a == '-D' else a for a in args]
```

### Anti-Patterns to Avoid
- **Passing -D to sl bookmark:** This strips commits, which is NOT what git branch -D does
- **Using sl revert --all for git restore .:** Both work, but "." is more precise and matches git's behavior
- **Assuming git branch output format:** sl bookmark output differs; for v1.2, passthrough is acceptable

## Command Mappings Analysis

### BRANCH-01: git branch (list) -> sl bookmark

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git branch` | `sl bookmark` | YES |
| Output format | One per line, * marks current | Similar, * marks active | Mostly compatible |
| Current marker | Asterisk (*) green | Asterisk (*) | YES |
| Exit code | 0 on success | 0 on success | YES |

**Verified via CLI:**
```
$ sl bookmark
 * test-branch               570a0b5cefcf
```

The output includes commit hashes which git branch does not show by default, but this is acceptable for v1.2.

### BRANCH-02: git branch <name> -> sl bookmark <name>

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Create | `git branch <name>` | `sl bookmark <name>` | YES |
| At current | Creates at HEAD | Creates at current commit | YES |
| Exit code | 0 on success | 0 on success | YES |
| Duplicate name | Error | Error | YES |

**Implementation:** Direct passthrough after command name change.

### BRANCH-03: git branch -d <name> -> sl bookmark -d <name>

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Delete | `git branch -d <name>` | `sl bookmark -d <name>` | YES |
| Merged check | Requires merged or HEAD | No merge check | Different behavior |
| Exit code | Error if unmerged | 0 on success | sl is more permissive |

**Note:** git branch -d has safety checks that sl bookmark -d does not. For v1.2, passthrough is acceptable.

### BRANCH-04: git branch -D <name> -> sl bookmark -d <name>

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Delete | `git branch -D <name>` | `sl bookmark -d <name>` | MUST TRANSLATE |
| Force | Ignores merge status | N/A | |
| Commits | Preserved | **-D strips commits!** | CRITICAL |

**CRITICAL SAFETY ISSUE:**
- git branch -D: Force deletes label, commits preserved
- sl bookmark -D: Deletes label AND strips/hides commits

**Solution:** Map both `-d` and `-D` to `sl bookmark -d` to preserve commits.

### RESTORE-01: git restore <file> -> sl revert <file>

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git restore <file>` | `sl revert <file>` | YES |
| Effect | Discard working tree changes | Discard working tree changes | YES |
| Source | HEAD (default) | Current commit | YES |
| Exit code | 0 on success | 0 on success | YES |

**Verified via CLI:**
```
$ echo "modified" >> test.txt && sl status
M test.txt
$ sl revert test.txt && sl status
(no output - file reverted)
```

### RESTORE-02: git restore . -> sl revert .

| Aspect | git | sl | Compatible? |
|--------|-----|-----|-------------|
| Command | `git restore .` | `sl revert .` | YES |
| Effect | Discard all changes | Discard all changes | YES |
| Added files | Untracked after restore | Forgotten (becomes ?) | YES |
| Exit code | 0 on success | 0 on success | YES |

**Verified via CLI:**
```
$ echo "modified" >> test.txt && echo "new" > new.txt && sl add new.txt && sl status
M test.txt
A new.txt
$ sl revert .
forgetting new.txt
reverting test.txt
$ sl status
? new.txt
```

Note: `sl revert .` also forgets added files, matching git restore behavior.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Branch listing format | Output reformatting | sl bookmark passthrough | Format differences acceptable for v1.2 |
| Merge check for -d | Custom merge detection | Direct passthrough | sl's permissiveness is acceptable |
| File backup on revert | Custom backup logic | sl revert handles backups | Already implemented in sl |
| Command dispatch | Manual if/elif in main | Separate cmd_*.py files | ARCH-03 compliance |

**Key insight:** Both branch and restore are straightforward translations with one critical safety fix (-D to -d).

## Common Pitfalls

### Pitfall 1: Passing -D to sl bookmark
**What goes wrong:** User loses commits when force-deleting a branch
**Why it happens:** git branch -D just removes label; sl bookmark -D strips commits
**How to avoid:** ALWAYS translate -D to -d for sl bookmark
**Warning signs:** "hiding commit" or "1 commit hidden" messages
**Exit code:** Success, but destructive

### Pitfall 2: Expecting git branch output format
**What goes wrong:** Scripts parsing git branch output may break
**Why it happens:** sl bookmark includes commit hashes
**How to avoid:** Document output format differences; accept for v1.2
**Warning signs:** Test failures on output comparison

### Pitfall 3: Assuming restore handles staged changes
**What goes wrong:** User expects git restore to unstage; it doesn't by default
**Why it happens:** git restore operates on working tree by default, not index
**How to avoid:** Phase 17 only covers working tree restore (RESTORE-01, RESTORE-02)
**Warning signs:** N/A - consistent with requirements

### Pitfall 4: Testing branch operations without commits
**What goes wrong:** Bookmarks require at least one commit in Sapling
**Why it happens:** Empty repo has no commits to attach bookmark to
**How to avoid:** Use sl_repo_with_commit fixture for all branch tests
**Warning signs:** Error creating bookmark

### Pitfall 5: Confusing revert vs backout
**What goes wrong:** User expects revert to undo a commit
**Why it happens:** git revert undoes commits; sl revert restores files
**How to avoid:** gitsl git restore -> sl revert (correct); git revert is separate command
**Warning signs:** None for this phase - restore is correct translation

## Code Examples

### cmd_branch.py
```python
"""Handler for 'git branch' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git branch' command.

    Translations:
    - git branch              -> sl bookmark (list)
    - git branch <name>       -> sl bookmark <name> (create)
    - git branch -d <name>    -> sl bookmark -d <name> (delete)
    - git branch -D <name>    -> sl bookmark -d <name> (safe delete)

    SAFETY: git branch -D just removes the label. sl bookmark -D strips
    commits. We ALWAYS use -d to preserve commits.
    """
    args = list(parsed.args)

    # CRITICAL: Translate -D to -d to avoid destroying commits
    # git -D: force delete label, commits preserved
    # sl -D: delete label AND strip commits (destructive!)
    args = ['-d' if a == '-D' else a for a in args]

    return run_sl(["bookmark"] + args)
```

### cmd_restore.py
```python
"""Handler for 'git restore' command."""

from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git restore' command.

    Translations:
    - git restore <file>  -> sl revert <file>
    - git restore .       -> sl revert .

    Note: This handles working tree restoration only.
    git restore --staged is a separate feature (not in Phase 17 scope).
    """
    return run_sl(["revert"] + list(parsed.args))
```

### Updated gitsl.py Dispatch
```python
# Add imports at top
import cmd_branch
import cmd_restore

# In main(), add dispatch cases:
if parsed.command == "branch":
    return cmd_branch.handle(parsed)

if parsed.command == "restore":
    return cmd_restore.handle(parsed)
```

## Test Patterns

### E2E Test for branch
```python
"""E2E tests for git branch command (BRANCH-01 through BRANCH-04)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.branch,
]


class TestBranchList:
    """BRANCH-01: git branch translates to sl bookmark (list)."""

    def test_branch_lists_bookmarks(self, sl_repo_with_commit: Path):
        """git branch lists existing bookmarks."""
        # Create a bookmark first
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "feature" in result.stdout


class TestBranchCreate:
    """BRANCH-02: git branch <name> translates to sl bookmark <name>."""

    def test_branch_creates_bookmark(self, sl_repo_with_commit: Path):
        """git branch <name> creates new bookmark."""
        result = run_gitsl(["branch", "new-feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was created
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "new-feature" in bookmarks.stdout


class TestBranchDelete:
    """BRANCH-03: git branch -d <name> translates to sl bookmark -d."""

    def test_branch_deletes_bookmark(self, sl_repo_with_commit: Path):
        """git branch -d deletes existing bookmark."""
        # Create and then delete
        run_command(["sl", "bookmark", "to-delete"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-d", "to-delete"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was deleted
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "to-delete" not in bookmarks.stdout


class TestBranchForceDelete:
    """BRANCH-04: git branch -D <name> translates to sl bookmark -d (safe)."""

    def test_branch_force_deletes_preserves_commits(self, sl_repo_with_commit: Path):
        """git branch -D removes bookmark but preserves commits."""
        # Create bookmark and add a commit on it
        run_command(["sl", "bookmark", "force-delete-test"], cwd=sl_repo_with_commit)
        (sl_repo_with_commit / "extra.txt").write_text("extra content\n")
        run_command(["sl", "add", "extra.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Extra commit"], cwd=sl_repo_with_commit)

        # Get current commit hash
        log_before = run_command(["sl", "log", "-l", "1", "-T", "{node}"],
                                 cwd=sl_repo_with_commit)
        commit_hash = log_before.stdout.strip()

        result = run_gitsl(["branch", "-D", "force-delete-test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify commit still exists (not stripped)
        log_after = run_command(["sl", "log", "-r", commit_hash[:12], "-T", "{node}"],
                                cwd=sl_repo_with_commit)
        assert commit_hash[:12] in log_after.stdout
```

### E2E Test for restore
```python
"""E2E tests for git restore command (RESTORE-01, RESTORE-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.restore,
]


class TestRestoreFile:
    """RESTORE-01: git restore <file> translates to sl revert <file>."""

    def test_restore_discards_changes(self, sl_repo_with_commit: Path):
        """git restore <file> discards working tree changes."""
        test_file = sl_repo_with_commit / "README.md"
        original_content = test_file.read_text()

        # Modify the file
        test_file.write_text("modified content\n")
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status.stdout

        # Restore it
        result = run_gitsl(["restore", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify content restored
        assert test_file.read_text() == original_content


class TestRestoreAll:
    """RESTORE-02: git restore . translates to sl revert ."""

    def test_restore_all_discards_changes(self, sl_repo_with_commit: Path):
        """git restore . discards all working tree changes."""
        # Modify existing file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified content\n")

        # Create and add new file
        new_file = sl_repo_with_commit / "new.txt"
        new_file.write_text("new content\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo_with_commit)

        # Verify changes exist
        status_before = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status_before.stdout
        assert "A new.txt" in status_before.stdout

        # Restore all
        result = run_gitsl(["restore", "."], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify all changes discarded
        status_after = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status_after.stdout
        assert "A new.txt" not in status_after.stdout
        # new.txt should now be untracked
        assert "? new.txt" in status_after.stdout
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A - new phase | cmd_*.py with flag translation | Building on Phase 16 | Adds safety translation for -D |

**Conceptual Model Difference:**
- Git: Branches are fundamental - you're always "on" a branch
- Sapling: Bookmarks are optional labels - you can work without them

This is documented for user awareness but doesn't change implementation.

## Open Questions

1. **Output format compatibility**
   - What we know: sl bookmark shows commit hashes; git branch does not by default
   - What's unclear: Whether output format parsing would break user scripts
   - Recommendation: Accept for v1.2; document difference

2. **git branch -d merge check**
   - What we know: git branch -d refuses to delete unmerged branches
   - What's unclear: sl bookmark -d has no such check
   - Recommendation: Accept sl's permissiveness for v1.2; safer to delete

3. **git restore --staged**
   - What we know: Not in Phase 17 scope (RESTORE-01, RESTORE-02 are working tree only)
   - What's unclear: Will it be needed in future phases?
   - Recommendation: Document as future enhancement

4. **sl revert creates .orig backups**
   - What we know: sl revert creates .orig backup files by default
   - What's unclear: Whether this is problematic (git restore doesn't)
   - Recommendation: Accept for v1.2; can add --no-backup later if needed

## Sources

### Primary (HIGH confidence)
- [Sapling bookmark documentation](https://sapling-scm.com/docs/commands/bookmark/) - Official command reference
- [Sapling revert documentation](https://sapling-scm.com/docs/commands/revert/) - Official command reference
- [Git branch documentation](https://git-scm.com/docs/git-branch) - Official reference
- [Git restore documentation](https://git-scm.com/docs/git-restore) - Official reference
- [Sapling vs Git differences](https://sapling-scm.com/docs/introduction/differences-git/) - Conceptual model differences
- Direct CLI testing: Verified all command behaviors in test repository

### Secondary (MEDIUM confidence)
- Phase 16 RESEARCH.md - Established patterns for flag translation

### Tertiary (LOW confidence)
- None - all findings verified against actual CLI behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All patterns from Phase 16, no new dependencies
- Architecture: HIGH - Follows established cmd_*.py pattern
- Command mappings: HIGH - Verified via CLI help and direct testing
- Safety translation (-D to -d): HIGH - Tested destructive behavior of sl bookmark -D

**Research date:** 2026-01-20
**Valid until:** 2026-02-20 (30 days - stable patterns, critical safety issue documented)
