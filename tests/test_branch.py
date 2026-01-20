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

    def test_branch_empty_list(self, sl_repo_with_commit: Path):
        """git branch with no bookmarks returns success."""
        result = run_gitsl(["branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestBranchCreate:
    """BRANCH-02: git branch <name> translates to sl bookmark <name>."""

    def test_branch_creates_bookmark(self, sl_repo_with_commit: Path):
        """git branch <name> creates new bookmark."""
        result = run_gitsl(["branch", "new-feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was created
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "new-feature" in bookmarks.stdout

    def test_branch_duplicate_updates_bookmark(self, sl_repo_with_commit: Path):
        """git branch <name> with existing name updates bookmark location.

        Note: sl bookmark silently updates existing bookmarks (moves to current commit),
        unlike git branch which fails. This is expected shim behavior - we pass through
        to sl which has different semantics.
        """
        run_command(["sl", "bookmark", "existing"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "existing"], cwd=sl_repo_with_commit)
        # sl bookmark updates existing bookmarks silently
        assert result.exit_code == 0


class TestBranchDelete:
    """BRANCH-03: git branch -d <name> translates to sl bookmark -d."""

    def test_branch_delete(self, sl_repo_with_commit: Path):
        """git branch -d deletes existing bookmark."""
        run_command(["sl", "bookmark", "to-delete"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-d", "to-delete"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was deleted
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "to-delete" not in bookmarks.stdout

    def test_branch_delete_nonexistent_fails(self, sl_repo_with_commit: Path):
        """git branch -d with nonexistent bookmark fails."""
        result = run_gitsl(["branch", "-d", "nonexistent"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0


class TestBranchForceDelete:
    """BRANCH-04: git branch -D translates to sl bookmark -d (safe)."""

    def test_branch_force_delete(self, sl_repo_with_commit: Path):
        """git branch -D deletes bookmark."""
        run_command(["sl", "bookmark", "force-delete"], cwd=sl_repo_with_commit)

        result = run_gitsl(["branch", "-D", "force-delete"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was deleted
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "force-delete" not in bookmarks.stdout

    def test_branch_force_delete_preserves_commits(self, sl_repo_with_commit: Path):
        """git branch -D removes bookmark but preserves commits.

        CRITICAL: This verifies the -D to -d safety translation.
        sl bookmark -D would strip commits, which is NOT what git branch -D does.
        """
        # Create bookmark and make a commit on it
        run_command(["sl", "bookmark", "test-branch"], cwd=sl_repo_with_commit)
        (sl_repo_with_commit / "extra.txt").write_text("extra content\n")
        run_command(["sl", "add", "extra.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Extra commit"], cwd=sl_repo_with_commit)

        # Get current commit hash
        log_before = run_command(["sl", "log", "-l", "1", "-T", "{node}"],
                                 cwd=sl_repo_with_commit)
        commit_hash = log_before.stdout.strip()

        # Force delete the bookmark
        result = run_gitsl(["branch", "-D", "test-branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # CRITICAL: Verify commit still exists (not stripped)
        log_after = run_command(["sl", "log", "-r", commit_hash[:12], "-T", "{node}"],
                                cwd=sl_repo_with_commit)
        assert commit_hash[:12] in log_after.stdout, \
            "Commit was stripped! -D should translate to -d to preserve commits"
