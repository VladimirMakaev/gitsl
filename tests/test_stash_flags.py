"""
E2E tests for git stash flags (STSH-01 through STSH-10).

Tests:
- STSH-01: -u/--include-untracked includes untracked files
- STSH-02: -m/--message sets custom message
- STSH-03: stash show --stat displays statistics
- STSH-04: stash@{n} reference syntax
- STSH-05: -p/--patch interactive mode
- STSH-06: -k/--keep-index warning
- STSH-07: -a/--all includes all files
- STSH-08: -q/--quiet suppresses output
- STSH-09: stash push <pathspec> selective stashing
- STSH-10: stash branch <name> creates branch
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.stash_flags,
]


# ============================================================
# STSH-01: -u/--include-untracked
# ============================================================


class TestStashIncludeUntracked:
    """STSH-01: -u/--include-untracked includes untracked files."""

    def test_stash_u_includes_untracked(self, sl_repo_with_commit: Path):
        """git stash -u includes untracked files in stash."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        # Modify tracked file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        # Stash with -u
        result = run_gitsl(["stash", "-u"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Both files should be gone
        assert not untracked.exists()
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status.stdout
        assert "? untracked.txt" not in status.stdout

    def test_stash_include_untracked_long(self, sl_repo_with_commit: Path):
        """git stash --include-untracked works same as -u."""
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        result = run_gitsl(["stash", "--include-untracked"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked.exists()


# ============================================================
# STSH-02: -m/--message
# ============================================================


class TestStashMessage:
    """STSH-02: -m/--message sets custom message (extended tests)."""

    def test_stash_message_long_form(self, sl_repo_with_commit: Path):
        """git stash --message works."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["stash", "--message", "long form message"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "long form message" in shelves.stdout


# ============================================================
# STSH-03: stash show --stat
# ============================================================


class TestStashShow:
    """STSH-03: stash show --stat displays shelve diff statistics."""

    def test_stash_show_stat(self, sl_repo_with_commit: Path):
        """git stash show --stat displays file statistics."""
        # Create and stash changes
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified content for show\n")
        run_command(["sl", "shelve", "-m", "test show"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "show", "--stat"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "README.md" in result.stdout

    def test_stash_show_default(self, sl_repo_with_commit: Path):
        """git stash show without flags shows stat (git default)."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "show"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "README.md" in result.stdout

    def test_stash_show_patch(self, sl_repo_with_commit: Path):
        """git stash show -p displays patch."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "show", "-p"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Patch output contains diff markers
        assert "diff" in result.stdout or "@@" in result.stdout


# ============================================================
# STSH-04: stash@{n} reference syntax
# ============================================================


class TestStashReference:
    """STSH-04: stash@{n} reference syntax maps to shelve names."""

    def test_stash_ref_zero(self, sl_repo_with_commit: Path):
        """stash@{0} references most recent stash."""
        readme = sl_repo_with_commit / "README.md"

        # Create first stash
        readme.write_text("first\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)

        # Create second stash
        readme.write_text("second\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        # Show stash@{0} should be most recent (second)
        result = run_gitsl(["stash", "show", "stash@{0}"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_stash_ref_one(self, sl_repo_with_commit: Path):
        """stash@{1} references second most recent stash."""
        readme = sl_repo_with_commit / "README.md"

        # Create two stashes
        readme.write_text("first\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)
        readme.write_text("second\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        # Show stash@{1} should work (first stash)
        result = run_gitsl(["stash", "show", "stash@{1}"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_stash_ref_invalid_index(self, sl_repo_with_commit: Path):
        """stash@{n} with invalid index returns error."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        # stash@{10} doesn't exist
        result = run_gitsl(["stash", "show", "stash@{10}"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "does not exist" in result.stderr

    def test_stash_drop_with_ref(self, sl_repo_with_commit: Path):
        """git stash drop stash@{1} drops specific stash."""
        readme = sl_repo_with_commit / "README.md"

        # Create two stashes
        readme.write_text("first\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)
        readme.write_text("second\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        # Drop stash@{1} (first stash)
        result = run_gitsl(["stash", "drop", "stash@{1}"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # First stash should be gone, second should remain
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "first stash" not in shelves.stdout
        assert "second stash" in shelves.stdout


# ============================================================
# STSH-05: -p/--patch interactive mode
# ============================================================


class TestStashPatch:
    """STSH-05: -p/--patch translates to interactive mode."""

    def test_stash_patch_flag_accepted(self, sl_repo_with_commit: Path):
        """git stash -p flag is accepted (translates to -i)."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        # Note: Interactive mode will fail without TTY, but flag should be accepted
        # We just verify it doesn't error with "unknown flag"
        result = run_gitsl(["stash", "-p"], cwd=sl_repo_with_commit)
        # May fail due to no TTY, but shouldn't be "unknown flag"
        assert "unknown" not in result.stderr.lower()


# ============================================================
# STSH-06: -k/--keep-index warning
# ============================================================


class TestStashKeepIndex:
    """STSH-06: -k/--keep-index prints warning about no staging area."""

    def test_stash_keep_index_warning(self, sl_repo_with_commit: Path):
        """git stash -k prints warning."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["stash", "-k"], cwd=sl_repo_with_commit)
        # Should still work (stash the changes)
        assert result.exit_code == 0
        # But print warning
        assert "keep-index" in result.stderr.lower() or "staging" in result.stderr.lower()

    def test_stash_keep_index_long_warning(self, sl_repo_with_commit: Path):
        """git stash --keep-index prints warning."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["stash", "--keep-index"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "staging" in result.stderr.lower()


# ============================================================
# STSH-07: -a/--all includes ignored files
# ============================================================


class TestStashAll:
    """STSH-07: -a/--all stashes all files including ignored."""

    def test_stash_all_includes_untracked(self, sl_repo_with_commit: Path):
        """git stash -a includes untracked files."""
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked\n")

        result = run_gitsl(["stash", "-a"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked.exists()


# ============================================================
# STSH-08: -q/--quiet suppresses output
# ============================================================


class TestStashQuiet:
    """STSH-08: -q/--quiet suppresses output."""

    def test_stash_quiet(self, sl_repo_with_commit: Path):
        """git stash -q suppresses output."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["stash", "-q"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Output should be minimal or empty
        assert result.stdout.strip() == "" or len(result.stdout) < 50


# ============================================================
# STSH-09: stash push <pathspec>
# ============================================================


class TestStashPathspec:
    """STSH-09: stash push <pathspec> supports selective file stashing."""

    def test_stash_push_specific_file(self, sl_repo_with_commit: Path):
        """git stash push <file> stashes only that file."""
        # Modify two files
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")
        other = sl_repo_with_commit / "other.txt"
        other.write_text("other content\n")
        run_command(["sl", "add", "other.txt"], cwd=sl_repo_with_commit)

        # Stash only README.md
        result = run_gitsl(["stash", "push", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # README should be reverted, other.txt should still be added
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status.stdout
        assert "other.txt" in status.stdout


# ============================================================
# STSH-10: stash branch <name>
# ============================================================


class TestStashBranch:
    """STSH-10: stash branch <name> creates branch from stash."""

    def test_stash_branch_creates_branch(self, sl_repo_with_commit: Path):
        """git stash branch <name> creates branch and applies stash."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("stashed content\n")
        run_command(["sl", "shelve", "-m", "for branch"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "branch", "from-stash"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Branch should exist
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "from-stash" in bookmarks.stdout

        # Changes should be applied
        assert readme.read_text() == "stashed content\n"

        # Stash should be dropped
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "for branch" not in shelves.stdout

    def test_stash_branch_with_ref(self, sl_repo_with_commit: Path):
        """git stash branch <name> stash@{n} uses specific stash."""
        readme = sl_repo_with_commit / "README.md"

        # Create two stashes
        readme.write_text("first\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)
        readme.write_text("second\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        # Create branch from older stash
        result = run_gitsl(["stash", "branch", "from-first", "stash@{1}"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Branch should exist
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "from-first" in bookmarks.stdout

    def test_stash_branch_no_name_error(self, sl_repo_with_commit: Path):
        """git stash branch without name returns error."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "requires" in result.stderr.lower() or "name" in result.stderr.lower()
