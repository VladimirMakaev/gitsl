"""
E2E tests for git add command (CMD-02, CMD-08).

Tests:
- git add <files> stages files via sl add
- git add -A stages all changes via sl addremove
- git add --all works same as -A
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestAddBasic:
    """CMD-02: git add <files> translates to sl add <files>."""

    def test_add_new_file_succeeds(self, sl_repo: Path):
        """git add stages a new file."""
        new_file = sl_repo / "test.txt"
        new_file.write_text("test content\n")

        result = run_gitsl(["add", "test.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl status
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A test.txt" in status.stdout

    def test_add_multiple_files(self, sl_repo: Path):
        """git add can stage multiple files at once."""
        (sl_repo / "a.txt").write_text("a\n")
        (sl_repo / "b.txt").write_text("b\n")

        result = run_gitsl(["add", "a.txt", "b.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A a.txt" in status.stdout
        assert "A b.txt" in status.stdout


class TestAddAll:
    """CMD-08: git add -A translates to sl addremove."""

    def test_add_all_short_flag(self, sl_repo: Path):
        """git add -A stages new files."""
        (sl_repo / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "-A"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A new.txt" in status.stdout

    def test_add_all_long_flag(self, sl_repo: Path):
        """git add --all works the same as -A."""
        (sl_repo / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "--all"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A new.txt" in status.stdout

    def test_add_all_with_deleted_file(self, sl_repo_with_commit: Path):
        """git add -A marks deleted files for removal."""
        # Delete an existing tracked file
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["add", "-A"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout or "! README.md" in status.stdout
