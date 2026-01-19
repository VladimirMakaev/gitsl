"""E2E tests for git show command (SHOW-01, SHOW-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.show,
]


class TestShowBasic:
    """SHOW-01: git show translates to sl show."""

    def test_show_current_commit(self, sl_repo_with_commit: Path):
        """git show displays current commit."""
        result = run_gitsl(["show"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show commit info or diff output
        assert len(result.stdout) > 0


class TestShowCommit:
    """SHOW-02: git show <commit> shows specified commit."""

    def test_show_with_stat_flag(self, sl_repo_with_commit: Path):
        """git show --stat displays file statistics."""
        result = run_gitsl(["show", "--stat"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
