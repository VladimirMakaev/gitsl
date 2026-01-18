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
