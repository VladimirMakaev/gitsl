"""E2E tests for git switch command (SWITCH-01, SWITCH-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.switch,
]


class TestSwitchBranch:
    """SWITCH-01: git switch <branch> translates to sl goto <bookmark>."""

    def test_switch_to_bookmark(self, sl_repo_with_commit: Path):
        """git switch changes to existing bookmark."""
        # Create a bookmark
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["switch", "feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestSwitchCreate:
    """SWITCH-02: git switch -c <name> translates to sl bookmark <name>."""

    def test_switch_create_bookmark(self, sl_repo_with_commit: Path):
        """git switch -c creates new bookmark."""
        result = run_gitsl(["switch", "-c", "new-feature"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify bookmark was created
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "new-feature" in bookmarks.stdout
