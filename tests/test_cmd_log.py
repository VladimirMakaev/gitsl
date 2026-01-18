"""
E2E tests for git log command (CMD-04).

These tests verify:
- git log translates to sl log
- Exit codes propagate correctly
- Output is passed through
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestLogBasic:
    """Basic log command functionality."""

    def test_log_succeeds_in_repo_with_commit(self, git_repo_with_commit: Path):
        """sl log on repo with commit returns 0."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        assert result.exit_code == 0

    def test_log_shows_output(self, git_repo_with_commit: Path):
        """sl log produces some output."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        # Log should show something (commit info in stdout or stderr)
        assert result.stdout != "" or result.stderr != ""


class TestLogExitCodes:
    """Exit code propagation for log command."""

    def test_log_fails_in_non_repo(self, tmp_path: Path):
        """sl log in non-repo directory returns non-zero."""
        # tmp_path is NOT a repo, so sl log should fail
        result = run_gitsl(["log"], cwd=tmp_path)
        assert result.exit_code != 0


class TestLogOneline:
    """FLAG-04: git log --oneline emulates git oneline format."""

    def test_oneline_returns_hash_and_subject(self, sl_repo_with_commit: Path):
        """--oneline shows hash and subject."""
        result = run_gitsl(["log", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1

        # Each line should be: <hash> <subject>
        for line in lines:
            parts = line.split(" ", 1)
            assert len(parts) == 2, f"Expected 'hash subject', got: {line}"
            hash_part, subject = parts
            # Hash should be hex characters (sl uses 12 chars)
            assert all(c in "0123456789abcdef" for c in hash_part)
            # Subject should be non-empty
            assert len(subject) > 0


class TestLogLimit:
    """FLAG-05: git log -N translates to sl log -l N."""

    def test_limit_with_dash_n(self, sl_repo_with_commits: Path):
        """-3 limits to 3 commits."""
        result = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_dash_n_space(self, sl_repo_with_commits: Path):
        """-n 3 limits to 3 commits."""
        result = run_gitsl(["log", "-n", "3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_dash_n_attached(self, sl_repo_with_commits: Path):
        """-n3 limits to 3 commits."""
        result = run_gitsl(["log", "-n3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_max_count(self, sl_repo_with_commits: Path):
        """--max-count=3 limits to 3 commits."""
        result = run_gitsl(["log", "--max-count=3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3


class TestLogCombined:
    """Combined --oneline and -N flags."""

    def test_oneline_with_limit_either_order(self, sl_repo_with_commits: Path):
        """--oneline -3 and -3 --oneline produce same result."""
        result1 = run_gitsl(["log", "--oneline", "-3"], cwd=sl_repo_with_commits)
        result2 = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout

    def test_limit_greater_than_available(self, sl_repo_with_commits: Path):
        """-100 on 10-commit repo shows all 10."""
        result = run_gitsl(["log", "-100", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 10
