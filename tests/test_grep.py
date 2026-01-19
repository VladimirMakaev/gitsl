"""E2E tests for git grep command (GREP-01, GREP-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.grep,
]


class TestGrepBasic:
    """GREP-01: git grep <pattern> translates to sl grep <pattern>."""

    def test_grep_finds_pattern(self, sl_repo_with_commit: Path):
        """git grep finds pattern in tracked files."""
        result = run_gitsl(["grep", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # README.md contains "# Test Repository"
        assert "README" in result.stdout or "Test" in result.stdout

    def test_grep_no_match_returns_nonzero(self, sl_repo_with_commit: Path):
        """git grep with no matches returns non-zero."""
        result = run_gitsl(["grep", "nonexistent_pattern_xyz"], cwd=sl_repo_with_commit)
        # sl grep returns 1 when no matches (same as git grep)
        assert result.exit_code != 0 or result.stdout == ""


class TestGrepFlags:
    """GREP-02: git grep passes through common flags."""

    def test_grep_line_numbers(self, sl_repo_with_commit: Path):
        """git grep -n shows line numbers."""
        result = run_gitsl(["grep", "-n", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Output should contain line number (e.g., "README.md:1:...")
        assert ":" in result.stdout

    def test_grep_case_insensitive(self, sl_repo_with_commit: Path):
        """git grep -i performs case-insensitive search."""
        result = run_gitsl(["grep", "-i", "test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_files_only(self, sl_repo_with_commit: Path):
        """git grep -l shows only file names."""
        result = run_gitsl(["grep", "-l", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "README" in result.stdout
