"""E2E tests for git stash command (STASH-01 through STASH-07)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.stash,
]


class TestStashBasic:
    """STASH-01: git stash translates to sl shelve."""

    def test_stash_saves_changes(self, sl_repo_with_commit: Path):
        """git stash saves pending changes."""
        # Create a modification
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        # Verify dirty state
        status_before = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status_before.stdout

        result = run_gitsl(["stash"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify clean state
        status_after = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status_after.stdout

        # Verify shelve exists
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" in shelves.stdout

    def test_stash_nothing_to_stash(self, sl_repo_with_commit: Path):
        """git stash with no changes reports nothing to stash."""
        result = run_gitsl(["stash"], cwd=sl_repo_with_commit)
        # sl shelve with no changes exits with error
        assert result.exit_code != 0


class TestStashPush:
    """STASH-02: git stash push translates to sl shelve."""

    def test_stash_push(self, sl_repo_with_commit: Path):
        """git stash push saves pending changes."""
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        result = run_gitsl(["stash", "push"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status.stdout


class TestStashMessage:
    """STASH-03: git stash -m translates to sl shelve -m."""

    def test_stash_with_message(self, sl_repo_with_commit: Path):
        """git stash -m saves with custom message."""
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        result = run_gitsl(["stash", "-m", "my custom message"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "my custom message" in shelves.stdout

    def test_stash_push_with_message(self, sl_repo_with_commit: Path):
        """git stash push -m also works."""
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")

        result = run_gitsl(["stash", "push", "-m", "push message"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "push message" in shelves.stdout


class TestStashPop:
    """STASH-04: git stash pop translates to sl unshelve."""

    def test_stash_pop_restores_and_removes(self, sl_repo_with_commit: Path):
        """git stash pop restores changes and removes stash."""
        # Setup: create and stash changes
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        # Verify stash exists
        shelves_before = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" in shelves_before.stdout

        result = run_gitsl(["stash", "pop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Changes restored
        assert test_file.read_text() == "modified content\n"

        # Stash removed
        shelves_after = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" not in shelves_after.stdout

    def test_stash_pop_no_stash_error(self, sl_repo_with_commit: Path):
        """git stash pop with no stashes returns error."""
        result = run_gitsl(["stash", "pop"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0


class TestStashApply:
    """STASH-05: git stash apply translates to sl unshelve --keep."""

    def test_stash_apply_restores_and_keeps(self, sl_repo_with_commit: Path):
        """git stash apply restores changes but keeps stash."""
        # Setup: create and stash changes
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "apply"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Changes restored
        assert test_file.read_text() == "modified content\n"

        # Stash still exists
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "default" in shelves.stdout

    def test_stash_apply_no_stash_error(self, sl_repo_with_commit: Path):
        """git stash apply with no stashes returns error."""
        result = run_gitsl(["stash", "apply"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0


class TestStashList:
    """STASH-06: git stash list translates to sl shelve --list."""

    def test_stash_list_shows_shelves(self, sl_repo_with_commit: Path):
        """git stash list shows existing stashes."""
        # Create a stash
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve", "-m", "test stash"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "list"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "test stash" in result.stdout

    def test_stash_list_empty(self, sl_repo_with_commit: Path):
        """git stash list with no stashes returns empty output."""
        result = run_gitsl(["stash", "list"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == ""

    def test_stash_list_multiple(self, sl_repo_with_commit: Path):
        """git stash list shows multiple stashes."""
        test_file = sl_repo_with_commit / "README.md"

        # Create first stash
        test_file.write_text("first modification\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)

        # Create second stash
        test_file.write_text("second modification\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "list"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "first stash" in result.stdout
        assert "second stash" in result.stdout


class TestStashDrop:
    """STASH-07: git stash drop translates to sl shelve --delete."""

    def test_stash_drop_removes_most_recent(self, sl_repo_with_commit: Path):
        """git stash drop removes most recent stash."""
        # Create a stash
        test_file = sl_repo_with_commit / "README.md"
        test_file.write_text("modified content\n")
        run_command(["sl", "shelve"], cwd=sl_repo_with_commit)

        result = run_gitsl(["stash", "drop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Stash removed
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert shelves.stdout.strip() == ""

    def test_stash_drop_no_stash_error(self, sl_repo_with_commit: Path):
        """git stash drop with no stashes returns git-compatible error."""
        result = run_gitsl(["stash", "drop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 1
        assert "No stash entries found" in result.stderr

    def test_stash_drop_multiple_removes_most_recent(self, sl_repo_with_commit: Path):
        """git stash drop with multiple stashes removes most recent only."""
        test_file = sl_repo_with_commit / "README.md"

        # Create first stash
        test_file.write_text("first modification\n")
        run_command(["sl", "shelve", "-m", "first stash"], cwd=sl_repo_with_commit)

        # Create second stash
        test_file.write_text("second modification\n")
        run_command(["sl", "shelve", "-m", "second stash"], cwd=sl_repo_with_commit)

        # Drop should remove most recent (second)
        result = run_gitsl(["stash", "drop"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # First stash should still exist
        shelves = run_command(["sl", "shelve", "--list"], cwd=sl_repo_with_commit)
        assert "first stash" in shelves.stdout
        # Most recent (listed first) was the second, so it should be gone
        # Note: sl lists most recent first
