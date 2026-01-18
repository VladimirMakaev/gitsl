"""
E2E tests for git diff command (CMD-05).

These tests verify:
- git diff translates to sl diff
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
