"""E2E tests for git clone command (CLONE-01, CLONE-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clone,
]


class TestCloneUrl:
    """CLONE-01: git clone <url> translates to sl clone <url>."""

    def test_clone_local_repo(self, sl_repo_with_commit: Path, tmp_path: Path):
        """git clone can clone a local Sapling repository."""
        dest = tmp_path / "cloned"
        result = run_gitsl(["clone", str(sl_repo_with_commit), str(dest)], cwd=tmp_path)
        assert result.exit_code == 0
        assert dest.exists()
        assert (dest / ".sl").exists() or (dest / ".hg").exists()


class TestCloneDir:
    """CLONE-02: git clone <url> <dir> translates to sl clone <url> <dir>."""

    def test_clone_with_destination_name(self, sl_repo_with_commit: Path, tmp_path: Path):
        """git clone can specify destination directory name."""
        result = run_gitsl(["clone", str(sl_repo_with_commit), "my-clone"], cwd=tmp_path)
        assert result.exit_code == 0
        assert (tmp_path / "my-clone").exists()
