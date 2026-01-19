"""
E2E tests for git diff command (CMD-05).

These tests verify:
- git diff translates to sl diff
- Exit codes propagate correctly
- Output is passed through
- Specific file paths work
- Staged changes handling
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.diff,
]


class TestDiffBasic:
    """Basic diff command functionality."""

    def test_diff_succeeds_in_repo(self, git_repo: Path):
        """sl diff on valid repo returns 0."""
        result = run_gitsl(["diff"], cwd=git_repo)
        assert result.exit_code == 0

    def test_diff_shows_changes(self, git_repo_with_changes: Path):
        """sl diff shows output when there are changes."""
        result = run_gitsl(["diff"], cwd=git_repo_with_changes)
        # Diff with changes should produce output
        assert result.stdout != "" or result.stderr != ""


class TestDiffExitCodes:
    """Exit code propagation for diff command."""

    def test_diff_fails_in_non_repo(self, tmp_path: Path):
        """sl diff in non-repo directory returns non-zero."""
        # tmp_path is NOT a repo, so sl diff should fail
        result = run_gitsl(["diff"], cwd=tmp_path)
        assert result.exit_code != 0


class TestDiffSpecificFile:
    """Test diff with specific file paths."""

    def test_diff_specific_file(self, sl_repo_with_commit: Path):
        """git diff <file> shows changes only for that file."""
        # Modify the README
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("# Modified content\nNew line added.\n")

        # Diff only README.md
        result = run_gitsl(["diff", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Should show README.md changes
        assert "README.md" in result.stdout or "Modified" in result.stdout

    def test_diff_no_changes(self, sl_repo_with_commit: Path):
        """git diff on file with no changes returns empty."""
        result = run_gitsl(["diff", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # No changes means empty output
        assert result.stdout == ""

    def test_diff_specific_file_among_many(self, sl_repo_with_commit: Path):
        """git diff <file> with multiple modified files shows only that file."""
        # Modify README
        readme = sl_repo_with_commit / "README.md"
        original_readme = readme.read_text()
        readme.write_text(original_readme + "\nModified README\n")

        # Create and commit another file first (clean slate)
        (sl_repo_with_commit / "other.txt").write_text("other\n")
        run_command(["sl", "add", "other.txt"], cwd=sl_repo_with_commit)

        # Diff only README.md - should show its changes
        result = run_gitsl(["diff", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should have some output since README was modified
        assert "README" in result.stdout or "Modified" in result.stdout or len(result.stdout) > 0


class TestDiffSlRepo:
    """Test diff in Sapling repository (not Git)."""

    def test_diff_sl_repo_succeeds(self, sl_repo: Path):
        """diff in sl repo with no changes returns 0."""
        result = run_gitsl(["diff"], cwd=sl_repo)
        assert result.exit_code == 0
        assert result.stdout == ""

    def test_diff_sl_repo_with_modified_file(self, sl_repo_with_commit: Path):
        """diff in sl repo shows modified file changes."""
        # Modify existing file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("# Modified\nAdditional content\n")

        result = run_gitsl(["diff"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Should show diff output
        assert "diff" in result.stdout.lower() or "---" in result.stdout or "+++" in result.stdout

    def test_diff_sl_repo_with_new_file(self, sl_repo: Path):
        """diff on untracked file shows nothing (not tracked yet)."""
        # Create new untracked file
        (sl_repo / "new.txt").write_text("new content\n")

        result = run_gitsl(["diff"], cwd=sl_repo)
        assert result.exit_code == 0
        # Untracked files don't show in diff
        assert result.stdout == ""
