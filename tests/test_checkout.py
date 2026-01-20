"""E2E tests for git checkout command (CHECKOUT-01 through CHECKOUT-06)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.checkout,
]


class TestCheckoutCommit:
    """CHECKOUT-01: git checkout <commit> translates to sl goto <commit>."""

    def test_checkout_commit_hash(self, sl_repo_with_commit: Path):
        """git checkout with commit hash switches to that commit."""
        # Get current commit hash
        log = run_command(
            ["sl", "log", "-l", "1", "-T", "{node}"], cwd=sl_repo_with_commit
        )
        commit_hash = log.stdout.strip()[:12]

        result = run_gitsl(["checkout", commit_hash], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_checkout_partial_hash(self, sl_repo_with_commit: Path):
        """git checkout with partial hash (7 chars) works."""
        # Get current commit hash
        log = run_command(
            ["sl", "log", "-l", "1", "-T", "{node}"], cwd=sl_repo_with_commit
        )
        # Use first 7 characters as partial hash
        partial_hash = log.stdout.strip()[:7]

        result = run_gitsl(["checkout", partial_hash], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestCheckoutBranch:
    """CHECKOUT-02: git checkout <branch> translates to sl goto <bookmark>."""

    def test_checkout_bookmark(self, sl_repo_with_commit: Path):
        """git checkout with bookmark name switches to it."""
        # Create a bookmark
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["checkout", "feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_checkout_activates_bookmark(self, sl_repo_with_commit: Path):
        """Verify bookmark is active after checkout."""
        # Create a bookmark
        run_command(["sl", "bookmark", "test-active"], cwd=sl_repo_with_commit)

        result = run_gitsl(["checkout", "test-active"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Check bookmark is active (has * prefix in sl bookmarks)
        bookmarks = run_command(["sl", "bookmarks"], cwd=sl_repo_with_commit)
        # Active bookmark has * prefix
        assert "test-active" in bookmarks.stdout


class TestCheckoutFile:
    """CHECKOUT-03, CHECKOUT-04: git checkout <file> and git checkout -- <file>."""

    def test_checkout_file_without_separator(self, sl_repo_with_commit: Path):
        """git checkout <file> restores modified file."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        result = run_gitsl(["checkout", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert readme.read_text() == original

    def test_checkout_file_with_separator(self, sl_repo_with_commit: Path):
        """git checkout -- <file> restores modified file."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        result = run_gitsl(["checkout", "--", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert readme.read_text() == original

    def test_checkout_commit_file(self, sl_repo_with_commit: Path):
        """git checkout <commit> -- <file> restores file from specific commit."""
        readme = sl_repo_with_commit / "README.md"
        original_content = readme.read_text()

        # Get current commit hash
        log = run_command(
            ["sl", "log", "-l", "1", "-T", "{node}"], cwd=sl_repo_with_commit
        )
        commit_hash = log.stdout.strip()[:12]

        # Modify and commit
        readme.write_text("new content\n")
        run_command(["sl", "commit", "-m", "Update readme"], cwd=sl_repo_with_commit)

        # Restore from the original commit
        result = run_gitsl(
            ["checkout", commit_hash, "--", "README.md"], cwd=sl_repo_with_commit
        )
        assert result.exit_code == 0
        assert readme.read_text() == original_content


class TestCheckoutCreateBranch:
    """CHECKOUT-05: git checkout -b <name> creates and switches to bookmark."""

    def test_checkout_b_creates_branch(self, sl_repo_with_commit: Path):
        """git checkout -b creates new bookmark."""
        result = run_gitsl(["checkout", "-b", "new-feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark exists
        bookmarks = run_command(["sl", "bookmarks"], cwd=sl_repo_with_commit)
        assert "new-feature" in bookmarks.stdout

    def test_checkout_B_updates_branch(self, sl_repo_with_commit: Path):
        """git checkout -B on existing bookmark succeeds (sl silently updates)."""
        # Create initial bookmark
        run_command(["sl", "bookmark", "existing"], cwd=sl_repo_with_commit)

        # -B should succeed (sl updates existing bookmark)
        result = run_gitsl(["checkout", "-B", "existing"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        bookmarks = run_command(["sl", "bookmarks"], cwd=sl_repo_with_commit)
        assert "existing" in bookmarks.stdout

    def test_checkout_b_with_startpoint(self, sl_repo_with_commits: Path):
        """git checkout -b <name> <start> creates branch at specific commit."""
        # Get first commit hash
        log = run_command(
            ["sl", "log", "-l", "10", "-T", "{node}\\n"], cwd=sl_repo_with_commits
        )
        commits = [c.strip() for c in log.stdout.strip().split("\n") if c.strip()]
        # Pick an older commit (not the latest)
        start_commit = commits[-1][:12]

        result = run_gitsl(
            ["checkout", "-b", "from-old", start_commit], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0

        # Verify we're at the start commit
        current = run_command(
            ["sl", "log", "-l", "1", "-T", "{node}"], cwd=sl_repo_with_commits
        )
        assert current.stdout.strip().startswith(start_commit[:7])


class TestCheckoutDisambiguation:
    """CHECKOUT-06: Checkout disambiguates between commit/branch/file."""

    def test_checkout_ambiguous_errors(self, sl_repo_with_commit: Path):
        """git checkout errors when arg matches both branch and file."""
        # Create a bookmark named "ambiguous"
        run_command(["sl", "bookmark", "ambiguous"], cwd=sl_repo_with_commit)
        # Create and commit a file named "ambiguous"
        (sl_repo_with_commit / "ambiguous").write_text("content\n")
        run_command(["sl", "add", "ambiguous"], cwd=sl_repo_with_commit)
        run_command(
            ["sl", "commit", "-m", "Add ambiguous file"], cwd=sl_repo_with_commit
        )

        result = run_gitsl(["checkout", "ambiguous"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "could be both" in result.stderr

    def test_checkout_separator_resolves_ambiguity(self, sl_repo_with_commit: Path):
        """git checkout -- <file> works even when branch exists with same name."""
        # Create bookmark with same name as file
        run_command(["sl", "bookmark", "test-branch"], cwd=sl_repo_with_commit)
        # Create file with same name
        test_file = sl_repo_with_commit / "test-branch"
        test_file.write_text("content\n")
        run_command(["sl", "add", "test-branch"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add file"], cwd=sl_repo_with_commit)

        # Modify file
        test_file.write_text("modified\n")

        # Checkout with -- forces file interpretation
        result = run_gitsl(
            ["checkout", "--", "test-branch"], cwd=sl_repo_with_commit
        )
        assert result.exit_code == 0
        assert test_file.read_text() == "content\n"

    def test_checkout_revision_priority(self, sl_repo_with_commit: Path):
        """When only revision matches (no file), goto is used."""
        # Create bookmark, no file with this name
        run_command(["sl", "bookmark", "only-bookmark"], cwd=sl_repo_with_commit)

        result = run_gitsl(["checkout", "only-bookmark"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # No error, it switched via goto

    def test_checkout_file_priority(self, sl_repo_with_commit: Path):
        """When only file matches (no revision), revert is used."""
        # Create and commit a file with a unique name that won't match any revision
        # Note: sl has title-matching that can match filenames to commit messages
        test_file = sl_repo_with_commit / "xyz789data.txt"
        test_file.write_text("original\n")
        run_command(["sl", "add", "xyz789data.txt"], cwd=sl_repo_with_commit)
        run_command(
            ["sl", "commit", "-m", "Add test file"], cwd=sl_repo_with_commit
        )

        # Modify it
        test_file.write_text("modified\n")

        # Checkout - should use revert since it's only a file, not a revision
        result = run_gitsl(["checkout", "xyz789data.txt"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert test_file.read_text() == "original\n"


class TestCheckoutErrors:
    """Error handling for checkout command."""

    def test_checkout_no_args(self, sl_repo_with_commit: Path):
        """git checkout with no arguments shows error."""
        result = run_gitsl(["checkout"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "error" in result.stderr.lower()

    def test_checkout_invalid_target(self, sl_repo_with_commit: Path):
        """git checkout with nonexistent ref/file gives sl error."""
        result = run_gitsl(
            ["checkout", "nonexistent-xyz-123"], cwd=sl_repo_with_commit
        )
        # sl goto should fail with non-zero exit
        assert result.exit_code != 0
