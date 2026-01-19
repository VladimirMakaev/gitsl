"""E2E tests for git clean command (CLEAN-01, CLEAN-02, CLEAN-03)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clean,
]


class TestCleanForce:
    """CLEAN-01: git clean -f translates to sl purge."""

    def test_clean_removes_untracked(self, sl_repo_with_commit: Path):
        """git clean -f removes untracked files."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        result = run_gitsl(["clean", "-f"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked.exists()

    def test_clean_requires_force(self, sl_repo_with_commit: Path):
        """git clean without -f or -n fails with error."""
        result = run_gitsl(["clean"], cwd=sl_repo_with_commit)
        assert result.exit_code == 128
        assert "refusing to clean" in result.stderr


class TestCleanForceDir:
    """CLEAN-02: git clean -fd translates to sl purge (dirs included)."""

    def test_clean_removes_untracked_dir(self, sl_repo_with_commit: Path):
        """git clean -fd removes untracked directories."""
        # Create untracked directory with file
        untracked_dir = sl_repo_with_commit / "untracked_dir"
        untracked_dir.mkdir()
        (untracked_dir / "file.txt").write_text("content\n")

        result = run_gitsl(["clean", "-fd"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not untracked_dir.exists()


class TestCleanDryRun:
    """CLEAN-03: git clean -n translates to sl purge --print (dry run)."""

    def test_clean_dry_run_shows_files(self, sl_repo_with_commit: Path):
        """git clean -n shows files without removing."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        result = run_gitsl(["clean", "-n"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "untracked.txt" in result.stdout
        # File should still exist
        assert untracked.exists()
