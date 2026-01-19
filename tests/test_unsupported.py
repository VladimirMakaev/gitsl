"""
E2E tests for unsupported command handling (UNSUP-01, UNSUP-02).
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.unsupported,
]


class TestUnsupportedCommands:
    """Tests for unsupported command handling."""

    def test_push_exits_zero(self, sl_repo: Path):
        """UNSUP-02: Unsupported commands exit with code 0."""
        result = run_gitsl(["push"], cwd=sl_repo)
        assert result.exit_code == 0

    def test_push_message_on_stderr(self, sl_repo: Path):
        """UNSUP-01: Unsupported commands print original command to stderr."""
        result = run_gitsl(["push"], cwd=sl_repo)
        assert "gitsl: unsupported command: git push" in result.stderr

    def test_push_with_args_includes_full_command(self, sl_repo: Path):
        """Message includes all arguments."""
        result = run_gitsl(["push", "origin", "main"], cwd=sl_repo)
        assert "git push origin main" in result.stderr

    def test_push_stdout_empty(self, sl_repo: Path):
        """Unsupported commands don't pollute stdout."""
        result = run_gitsl(["push"], cwd=sl_repo)
        assert result.stdout == ""

    def test_rebase_unsupported(self, sl_repo: Path):
        """Another unsupported command works the same way."""
        result = run_gitsl(["rebase", "main"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "git rebase main" in result.stderr
        assert result.stdout == ""

    def test_fetch_unsupported(self, sl_repo: Path):
        """fetch is also unsupported."""
        result = run_gitsl(["fetch", "--all"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "git fetch --all" in result.stderr

    def test_checkout_unsupported(self, sl_repo: Path):
        """checkout is unsupported."""
        result = run_gitsl(["checkout", "-b", "feature"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "git checkout -b feature" in result.stderr
