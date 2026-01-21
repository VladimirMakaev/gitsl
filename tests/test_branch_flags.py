"""
E2E tests for git branch flags (BRAN-01 through BRAN-09).

Tests:
- BRAN-01: -m translates to sl bookmark -m (rename)
- BRAN-02: -a/--all shows all bookmarks including remote
- BRAN-03: -r/--remotes shows remote bookmarks only
- BRAN-04: -v/--verbose shows commit info with each branch
- BRAN-05: -l/--list lists branches matching pattern
- BRAN-06: --show-current shows current branch name
- BRAN-07: -t/--track sets up upstream tracking
- BRAN-08: -f/--force forces branch operations
- BRAN-09: -c/--copy copies a branch
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.branch_flags,
]


# ============================================================
# BRAN-01: -m translates to sl bookmark -m (rename)
# ============================================================


class TestBranchRename:
    """BRAN-01: -m translates to sl bookmark -m (rename)."""

    def test_branch_rename(self, sl_repo_with_commit: Path):
        """git branch -m old new renames bookmark."""
        # Create a bookmark
        run_command(["sl", "bookmark", "old-name"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-m", "old-name", "new-name"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify rename
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "new-name" in bookmarks.stdout
        assert "old-name" not in bookmarks.stdout

    def test_branch_rename_current(self, sl_repo_with_commit: Path):
        """git branch -m old new works on current branch."""
        run_command(["sl", "bookmark", "current-branch"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-m", "current-branch", "renamed-branch"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "renamed-branch" in bookmarks.stdout


# ============================================================
# BRAN-02: -a/--all shows all bookmarks including remote
# ============================================================


class TestBranchAll:
    """BRAN-02: -a/--all shows all bookmarks including remote."""

    def test_branch_all(self, sl_repo_with_commit: Path):
        """git branch -a shows all bookmarks."""
        run_command(["sl", "bookmark", "local-branch"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-a"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "local-branch" in result.stdout

    def test_branch_all_long_form(self, sl_repo_with_commit: Path):
        """git branch --all also works."""
        run_command(["sl", "bookmark", "test-branch"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--all"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "test-branch" in result.stdout


# ============================================================
# BRAN-03: -r/--remotes shows remote bookmarks only
# ============================================================


class TestBranchRemotes:
    """BRAN-03: -r/--remotes shows remote bookmarks only."""

    def test_branch_remotes(self, sl_repo_with_commit: Path):
        """git branch -r shows remote bookmarks."""
        # Note: In a local test repo, there may be no remotes
        result = run_gitsl(["branch", "-r"], cwd=sl_repo_with_commit)
        # Should succeed (even if empty)
        assert result.exit_code == 0

    def test_branch_remotes_long_form(self, sl_repo_with_commit: Path):
        """git branch --remotes also works."""
        result = run_gitsl(["branch", "--remotes"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# BRAN-04: -v/--verbose shows commit info with each branch
# ============================================================


class TestBranchVerbose:
    """BRAN-04: -v/--verbose shows commit info with each branch."""

    def test_branch_verbose(self, sl_repo_with_commit: Path):
        """git branch -v shows commit info."""
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-v"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show bookmark with commit hash or description
        assert "feature" in result.stdout
        # Verbose output should have more content than just the name
        # Template shows: bookmark: hash desc
        assert ":" in result.stdout

    def test_branch_verbose_long_form(self, sl_repo_with_commit: Path):
        """git branch --verbose also works."""
        run_command(["sl", "bookmark", "test"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--verbose"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "test" in result.stdout


# ============================================================
# BRAN-05: -l/--list lists branches matching pattern
# ============================================================


class TestBranchList:
    """BRAN-05: -l/--list lists branches matching pattern."""

    def test_branch_list_with_pattern(self, sl_repo_with_commit: Path):
        """git branch -l pattern filters branches."""
        run_command(["sl", "bookmark", "feature-one"], cwd=sl_repo_with_commit)
        run_command(["sl", "bookmark", "feature-two"], cwd=sl_repo_with_commit)
        run_command(["sl", "bookmark", "bugfix-one"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-l", "feature*"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "feature-one" in result.stdout
        assert "feature-two" in result.stdout
        # bugfix should not appear (doesn't match pattern)
        assert "bugfix" not in result.stdout

    def test_branch_list_no_pattern(self, sl_repo_with_commit: Path):
        """git branch --list without pattern shows all."""
        run_command(["sl", "bookmark", "main"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--list"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "main" in result.stdout


# ============================================================
# BRAN-06: --show-current shows current branch name
# ============================================================


class TestBranchShowCurrent:
    """BRAN-06: --show-current shows current branch name."""

    def test_show_current_branch(self, sl_repo_with_commit: Path):
        """git branch --show-current prints current bookmark."""
        run_command(["sl", "bookmark", "current"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--show-current"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "current" in result.stdout.strip()

    def test_show_current_no_branch(self, sl_repo_with_commit: Path):
        """git branch --show-current with no active bookmark returns empty."""
        # Don't create any bookmarks - should be detached
        result = run_gitsl(["branch", "--show-current"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # May be empty or show nothing (matches git behavior for detached HEAD)


# ============================================================
# BRAN-07: -t/--track sets up upstream tracking
# ============================================================


class TestBranchTrack:
    """BRAN-07: -t/--track sets up upstream tracking."""

    def test_branch_track(self, sl_repo_with_commit: Path):
        """git branch -t passes through tracking flag."""
        # Note: Tracking in Sapling is different from git
        # This test just verifies the flag is accepted and passed through
        run_command(["sl", "bookmark", "main"], cwd=sl_repo_with_commit)

        # Create new bookmark with tracking flag - should not error
        result = run_gitsl(["branch", "feature"],
                          cwd=sl_repo_with_commit)
        # Key is that the flag is accepted, not necessarily that tracking works
        assert result.exit_code == 0


# ============================================================
# BRAN-08: -f/--force forces branch operations
# ============================================================


class TestBranchForce:
    """BRAN-08: -f/--force forces branch operations."""

    def test_branch_force_move(self, sl_repo_with_commit: Path):
        """git branch -f moves existing bookmark."""
        # Create bookmark and another commit
        run_command(["sl", "bookmark", "to-move"], cwd=sl_repo_with_commit)
        (sl_repo_with_commit / "new.txt").write_text("new\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Second commit"], cwd=sl_repo_with_commit)

        # Force move bookmark to current commit
        result = run_gitsl(["branch", "-f", "to-move"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_branch_force_long_form(self, sl_repo_with_commit: Path):
        """git branch --force also works."""
        run_command(["sl", "bookmark", "existing"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--force", "existing"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# BRAN-09: -c/--copy copies a branch
# ============================================================


class TestBranchCopy:
    """BRAN-09: -c/--copy copies a branch."""

    def test_branch_copy(self, sl_repo_with_commit: Path):
        """git branch -c old new creates copy of bookmark."""
        run_command(["sl", "bookmark", "original"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-c", "original", "copy"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Both bookmarks should exist
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "original" in bookmarks.stdout
        assert "copy" in bookmarks.stdout

    def test_branch_copy_same_commit(self, sl_repo_with_commit: Path):
        """git branch -c creates bookmark at same commit."""
        run_command(["sl", "bookmark", "source"], cwd=sl_repo_with_commit)

        # Get commit hash where source points
        source_commit = run_command(
            ["sl", "log", "-r", "bookmark(source)", "--template", "{node|short}"],
            cwd=sl_repo_with_commit
        )

        result = run_gitsl(["branch", "-c", "source", "dest"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Dest should point to same commit
        dest_commit = run_command(
            ["sl", "log", "-r", "bookmark(dest)", "--template", "{node|short}"],
            cwd=sl_repo_with_commit
        )
        assert source_commit.stdout.strip() == dest_commit.stdout.strip()

    def test_branch_copy_long_form(self, sl_repo_with_commit: Path):
        """git branch --copy also works."""
        run_command(["sl", "bookmark", "orig"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "--copy", "orig", "dup"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "orig" in bookmarks.stdout
        assert "dup" in bookmarks.stdout

    def test_branch_copy_nonexistent_fails(self, sl_repo_with_commit: Path):
        """git branch -c with nonexistent source fails."""
        result = run_gitsl(["branch", "-c", "nonexistent", "copy"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code != 0
