"""E2E tests for git restore command (RESTORE-01, RESTORE-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.restore,
]


class TestRestoreFile:
    """RESTORE-01: git restore <file> translates to sl revert <file>."""

    def test_restore_discards_changes(self, sl_repo_with_commit: Path):
        """git restore <file> discards working tree changes."""
        readme = sl_repo_with_commit / "README.md"
        original_content = readme.read_text()

        # Modify the file
        readme.write_text("modified content\n")
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status.stdout

        # Restore it
        result = run_gitsl(["restore", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify content restored
        assert readme.read_text() == original_content

    def test_restore_nonexistent_file(self, sl_repo_with_commit: Path):
        """git restore on nonexistent file reports warning but succeeds.

        Note: sl revert prints a warning to stderr but returns exit code 0
        for nonexistent files. This is expected shim behavior.
        """
        result = run_gitsl(["restore", "nonexistent.txt"], cwd=sl_repo_with_commit)
        # sl revert prints warning but still returns 0
        assert result.exit_code == 0
        assert "no such file" in result.stderr


class TestRestoreAll:
    """RESTORE-02: git restore . translates to sl revert ."""

    def test_restore_all_discards_changes(self, sl_repo_with_commit: Path):
        """git restore . discards all working tree changes."""
        readme = sl_repo_with_commit / "README.md"
        original_content = readme.read_text()

        # Modify existing file
        readme.write_text("modified content\n")

        # Create and add new file
        new_file = sl_repo_with_commit / "new.txt"
        new_file.write_text("new content\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo_with_commit)

        # Verify changes exist
        status_before = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status_before.stdout
        assert "A new.txt" in status_before.stdout

        # Restore all
        result = run_gitsl(["restore", "."], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify modified file restored
        assert readme.read_text() == original_content

        # Verify added file is now untracked (forgotten)
        status_after = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" not in status_after.stdout
        assert "A new.txt" not in status_after.stdout
        assert "? new.txt" in status_after.stdout

    def test_restore_all_clean_workdir(self, sl_repo_with_commit: Path):
        """git restore . on clean workdir succeeds."""
        result = run_gitsl(["restore", "."], cwd=sl_repo_with_commit)
        # Should succeed with no changes to revert
        assert result.exit_code == 0
