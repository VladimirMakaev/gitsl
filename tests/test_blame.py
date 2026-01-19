"""E2E tests for git blame command (BLAME-01, BLAME-02)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.blame,
]


class TestBlameBasic:
    """BLAME-01: git blame <file> translates to sl annotate <file>."""

    def test_blame_file(self, sl_repo_with_commit: Path):
        """git blame shows per-line annotations."""
        result = run_gitsl(["blame", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show annotated content
        assert len(result.stdout) > 0


class TestBlameFlags:
    """BLAME-02: git blame passes through common flags."""

    def test_blame_ignore_whitespace(self, sl_repo_with_commit: Path):
        """git blame -w ignores whitespace changes."""
        result = run_gitsl(["blame", "-w", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
