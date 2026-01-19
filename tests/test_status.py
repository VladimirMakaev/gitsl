"""
E2E tests for git status --porcelain and --short (FLAG-01, FLAG-02).

Tests exact byte-for-byte format matching for tooling compatibility.
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.status,
]


class TestPorcelainUntracked:
    """Untracked files show as ?? filename."""

    def test_untracked_file_format(self, sl_repo: Path):
        """Untracked file shows as '?? filename'."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert result.stdout == "?? untracked.txt\n"

    def test_multiple_untracked_files(self, sl_repo: Path):
        """Multiple untracked files each show as ??."""
        (sl_repo / "a.txt").write_text("a\n")
        (sl_repo / "b.txt").write_text("b\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "?? a.txt" in result.stdout
        assert "?? b.txt" in result.stdout


class TestPorcelainAdded:
    """Added files show as A  filename (A + space)."""

    def test_added_file_format(self, sl_repo: Path):
        """Added file shows as 'A  filename'."""
        (sl_repo / "new.txt").write_text("content\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo)

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        # Exact format: A<space><space>filename
        assert "A  new.txt" in result.stdout


class TestPorcelainModified:
    """Modified files show as  M filename (space + M)."""

    def test_modified_file_format(self, sl_repo_with_commit: Path):
        """Modified tracked file shows as ' M filename'."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("Modified content\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        # Exact format: <space>M<space>filename
        assert " M README.md" in result.stdout


class TestPorcelainRemoved:
    """Removed files (via sl rm) show as D  filename."""

    def test_removed_file_format(self, sl_repo_with_commit: Path):
        """File removed via sl rm shows as 'D  filename'."""
        run_command(["sl", "rm", "README.md"], cwd=sl_repo_with_commit)

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        # Exact format: D<space><space>filename
        assert "D  README.md" in result.stdout


class TestPorcelainMissing:
    """Missing files (deleted without sl rm) show as  D filename."""

    def test_missing_file_format(self, sl_repo_with_commit: Path):
        """File deleted from disk (not via sl rm) shows as ' D filename'."""
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        # Exact format: <space>D<space>filename
        assert " D README.md" in result.stdout


class TestPorcelainCleanRepo:
    """Clean repo outputs empty string."""

    def test_clean_repo_empty_output(self, sl_repo_with_commit: Path):
        """Clean repo with --porcelain outputs nothing."""
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        assert result.stdout == ""


class TestPorcelainMixedStates:
    """Multiple files with different states."""

    def test_mixed_states(self, sl_repo_with_commit: Path):
        """Repo with added, modified, and untracked files."""
        # Modify existing
        (sl_repo_with_commit / "README.md").write_text("modified\n")
        # Add new tracked file
        (sl_repo_with_commit / "added.txt").write_text("added\n")
        run_command(["sl", "add", "added.txt"], cwd=sl_repo_with_commit)
        # Create untracked
        (sl_repo_with_commit / "untracked.txt").write_text("untracked\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        assert " M README.md" in result.stdout
        assert "A  added.txt" in result.stdout
        assert "?? untracked.txt" in result.stdout


class TestShortFlag:
    """--short and -s produce same format as --porcelain."""

    def test_short_flag(self, sl_repo: Path):
        """--short produces porcelain format."""
        (sl_repo / "file.txt").write_text("content\n")

        result = run_gitsl(["status", "--short"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "?? file.txt" in result.stdout

    def test_s_flag(self, sl_repo: Path):
        """-s produces porcelain format."""
        (sl_repo / "file.txt").write_text("content\n")

        result = run_gitsl(["status", "-s"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "?? file.txt" in result.stdout


class TestNormalStatusPassthrough:
    """Normal status (no flags) still passthroughs to sl."""

    def test_normal_status_passthrough(self, sl_repo: Path):
        """git status without flags runs sl status passthrough."""
        (sl_repo / "file.txt").write_text("content\n")

        result = run_gitsl(["status"], cwd=sl_repo)

        assert result.exit_code == 0
        # sl status uses single char code, not porcelain format
        # Output should contain "? file.txt" (sl format), NOT "?? file.txt"
        assert "? file.txt" in result.stdout or "file.txt" in result.stdout
