"""E2E tests for git mv command (MV-01, MV-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.mv,
]


class TestMvBasic:
    """MV-01: git mv <src> <dst> translates to sl rename <src> <dst>."""

    def test_mv_rename_file(self, sl_repo_with_commit: Path):
        """git mv renames a file."""
        result = run_gitsl(["mv", "README.md", "RENAMED.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify rename occurred
        assert not (sl_repo_with_commit / "README.md").exists()
        assert (sl_repo_with_commit / "RENAMED.md").exists()


class TestMvForce:
    """MV-02: git mv -f translates to sl rename -f."""

    def test_mv_force_overwrite(self, sl_repo_with_commit: Path):
        """git mv -f can overwrite existing file."""
        # Create destination file
        dest = sl_repo_with_commit / "dest.md"
        dest.write_text("destination\n")
        run_command(["sl", "add", "dest.md"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add dest"], cwd=sl_repo_with_commit)

        result = run_gitsl(["mv", "-f", "README.md", "dest.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
