"""
E2E tests for git init command (CMD-06).

These tests verify:
- git init translates to sl init
- Creates a Sapling repository (.sl or .hg directory depending on Sapling version)
- Exit codes propagate correctly
"""

import shutil
from pathlib import Path

from typing import Optional

import pytest

from conftest import run_gitsl


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.init,
]


def get_sapling_repo_dir(path: Path) -> Optional[Path]:
    """
    Find the Sapling repository directory.

    Sapling can create either .sl (OSS versions with git-compatible storage)
    or .hg (traditional Mercurial-style) depending on version and install method.

    Returns:
        Path to .sl or .hg if found, None otherwise
    """
    sl_dir = path / ".sl"
    if sl_dir.exists():
        return sl_dir
    hg_dir = path / ".hg"
    if hg_dir.exists():
        return hg_dir
    return None


class TestInitBasic:
    """Basic init command functionality."""

    def test_init_creates_repo(self, tmp_path: Path):
        """sl init creates a repository and returns 0."""
        # Use tmp_path directly (NOT git_repo fixture) since init creates the repo
        result = run_gitsl(["init"], cwd=tmp_path)
        assert result.exit_code == 0

    def test_init_creates_repo_directory(self, tmp_path: Path):
        """sl init creates .sl or .hg directory."""
        run_gitsl(["init"], cwd=tmp_path)
        repo_dir = get_sapling_repo_dir(tmp_path)
        assert repo_dir is not None, f"Expected .sl or .hg directory in {tmp_path}, found: {list(tmp_path.iterdir())}"
        assert repo_dir.is_dir()
