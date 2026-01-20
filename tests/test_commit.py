"""
E2E tests for git commit command (CMD-03).

Tests:
- git commit -m creates commit with message
- Commit with nothing staged returns non-zero
- Add -> commit workflow results in clean status
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.commit,
]


class TestCommitBasic:
    """CMD-03: git commit -m translates to sl commit -m."""

    def test_commit_with_message_succeeds(self, sl_repo: Path):
        """git commit -m creates a commit with the message."""
        # Create and add a file
        (sl_repo / "test.txt").write_text("test\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        # Commit via gitsl
        result = run_gitsl(["commit", "-m", "Test commit"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify commit exists with correct message
        log = run_command(["sl", "log", "--limit", "1"], cwd=sl_repo)
        assert "Test commit" in log.stdout

    def test_commit_nothing_staged_returns_nonzero(self, sl_repo_with_commit: Path):
        """git commit with nothing to commit returns non-zero."""
        result = run_gitsl(["commit", "-m", "Empty"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0


class TestWorkflow:
    """Integration: add -> commit -> status shows clean."""

    def test_add_commit_workflow(self, sl_repo: Path):
        """Full add -> commit workflow results in clean status."""
        # Create file
        (sl_repo / "file.txt").write_text("content\n")

        # Add via gitsl
        add_result = run_gitsl(["add", "file.txt"], cwd=sl_repo)
        assert add_result.exit_code == 0

        # Commit via gitsl
        commit_result = run_gitsl(["commit", "-m", "Add file"], cwd=sl_repo)
        assert commit_result.exit_code == 0

        # Status should be clean
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert status.stdout.strip() == ""


class TestCommitSafety:
    """SAFE-01: git commit -a should not add untracked files."""

    def test_commit_a_does_not_add_untracked(self, sl_repo_with_commit: Path):
        """git commit -a ignores untracked files (removes flag)."""
        # Create untracked file
        (sl_repo_with_commit / "untracked.txt").write_text("new content\n")

        # Modify tracked file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified content\n")

        # Add the modified file (so we have something to commit)
        run_command(["sl", "add", "README.md"], cwd=sl_repo_with_commit)

        # Commit with -a - should NOT add untracked.txt
        result = run_gitsl(["commit", "-a", "-m", "Test commit"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Untracked file should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "untracked.txt" in status.stdout, \
            "untracked.txt was added by commit -a (should remain untracked)"

    def test_commit_all_flag_removed(self, sl_repo_with_commit: Path):
        """git commit --all (long form) also ignores untracked files."""
        (sl_repo_with_commit / "untracked2.txt").write_text("new\n")
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")
        run_command(["sl", "add", "README.md"], cwd=sl_repo_with_commit)

        result = run_gitsl(["commit", "--all", "-m", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "untracked2.txt" in status.stdout
