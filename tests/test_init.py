"""
E2E tests for git init command (CMD-06).

These tests verify:
- git init translates to sl init
- Creates a Sapling repository (.hg directory)
- Exit codes propagate correctly
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.init,
]


class TestInitBasic:
    """Basic init command functionality."""

    def test_init_creates_repo(self, tmp_path: Path):
        """sl init creates a repository and returns 0."""
        # Use tmp_path directly (NOT git_repo fixture) since init creates the repo
        result = run_gitsl(["init"], cwd=tmp_path)
        assert result.exit_code == 0

    def test_init_creates_hg_directory(self, tmp_path: Path):
        """sl init creates .hg directory."""
        run_gitsl(["init"], cwd=tmp_path)
        hg_dir = tmp_path / ".hg"
        assert hg_dir.exists()
        assert hg_dir.is_dir()
