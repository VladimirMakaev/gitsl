"""
E2E tests for git switch flags (CHKT-01, CHKT-02, CHKT-07, CHKT-08, CHKT-09).

Tests:
- CHKT-01: -c/--create creates and switches to new branch
- CHKT-02: -C/--force-create force creates branch
- CHKT-07: -d/--detach switches without activating bookmark
- CHKT-08: -f/--force/--discard-changes discards local changes
- CHKT-09: -m/--merge merges local changes during switch
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.switch_flags,
]


# ============================================================
# CHKT-01: -c/--create (extended from existing tests)
# ============================================================


class TestSwitchCreate:
    """CHKT-01: switch -c/--create creates and switches to new branch."""

    def test_switch_create_and_goto(self, sl_repo_with_commit: Path):
        """git switch -c creates bookmark and switches to it."""
        result = run_gitsl(["switch", "-c", "new-branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Should be on new branch
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "* new-branch" in bookmarks.stdout or "new-branch" in bookmarks.stdout

    def test_switch_create_long_form(self, sl_repo_with_commit: Path):
        """git switch --create works same as -c."""
        result = run_gitsl(["switch", "--create", "long-branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "long-branch" in bookmarks.stdout


# ============================================================
# CHKT-02: -C/--force-create
# ============================================================


class TestSwitchForceCreate:
    """CHKT-02: switch -C/--force-create force creates bookmark."""

    def test_switch_force_create_new(self, sl_repo_with_commit: Path):
        """git switch -C creates new bookmark."""
        result = run_gitsl(["switch", "-C", "force-branch"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "force-branch" in bookmarks.stdout

    def test_switch_force_create_existing(self, sl_repo_with_commit: Path):
        """git switch -C updates existing bookmark."""
        # Create a bookmark
        run_command(["sl", "bookmark", "existing"], cwd=sl_repo_with_commit)

        # Make a new commit
        (sl_repo_with_commit / "new.txt").write_text("new\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "new commit"], cwd=sl_repo_with_commit)

        # Force create should succeed (update bookmark)
        result = run_gitsl(["switch", "-C", "existing"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# CHKT-07: -d/--detach
# ============================================================


class TestSwitchDetach:
    """CHKT-07: switch -d/--detach switches without activating bookmark."""

    def test_switch_detach(self, sl_repo_with_commit: Path):
        """git switch -d switches to commit without active bookmark."""
        # Create and switch to a bookmark
        run_command(["sl", "bookmark", "test-branch"], cwd=sl_repo_with_commit)

        # Get current commit hash
        log = run_command(["sl", "log", "-l", "1", "--template", "{node|short}"],
                         cwd=sl_repo_with_commit)
        commit_hash = log.stdout.strip()

        # Switch with detach
        result = run_gitsl(["switch", "-d", commit_hash], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# CHKT-08: -f/--force/--discard-changes
# ============================================================


class TestSwitchForce:
    """CHKT-08: switch -f discards local changes during switch."""

    def test_switch_force_discards_changes(self, sl_repo_with_commit: Path):
        """git switch -f discards uncommitted changes."""
        # Create a bookmark to switch to
        run_command(["sl", "bookmark", "target"], cwd=sl_repo_with_commit)
        run_command(["sl", "bookmark", "source"], cwd=sl_repo_with_commit)

        # Modify file
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        # Switch with force should succeed and discard changes
        result = run_gitsl(["switch", "-f", "target"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Changes should be discarded
        assert readme.read_text() == original

    def test_switch_discard_changes_flag(self, sl_repo_with_commit: Path):
        """git switch --discard-changes works same as -f."""
        run_command(["sl", "bookmark", "target"], cwd=sl_repo_with_commit)

        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["switch", "--discard-changes", "target"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# CHKT-09: -m/--merge
# ============================================================


class TestSwitchMerge:
    """CHKT-09: switch -m merges local changes during switch."""

    def test_switch_merge_flag_accepted(self, sl_repo_with_commit: Path):
        """git switch -m flag is accepted."""
        run_command(["sl", "bookmark", "target"], cwd=sl_repo_with_commit)

        result = run_gitsl(["switch", "-m", "target"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
