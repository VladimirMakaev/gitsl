"""E2E tests for git rm command (RM-01, RM-02, RM-03)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.rm,
]


class TestRmBasic:
    """RM-01: git rm <files> translates to sl remove <files>."""

    def test_rm_tracked_file(self, sl_repo_with_commit: Path):
        """git rm removes tracked file."""
        result = run_gitsl(["rm", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify file is marked for removal
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout


class TestRmForce:
    """RM-02: git rm -f translates to sl remove -f."""

    def test_rm_force_modified_file(self, sl_repo_with_commit: Path):
        """git rm -f forces removal of modified file."""
        # Modify the file first
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("Modified content\n")

        result = run_gitsl(["rm", "-f", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestRmRecursive:
    """RM-03: git rm -r translates to sl remove (recursive by default)."""

    def test_rm_recursive_directory(self, sl_repo_with_commit: Path):
        """git rm -r removes directory recursively."""
        # Create a subdirectory with files
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        subfile = subdir / "file.txt"
        subfile.write_text("content\n")
        run_command(["sl", "add", "subdir/file.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rm", "-r", "subdir"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
