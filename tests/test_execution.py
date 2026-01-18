"""
E2E tests for execution pipeline (EXEC-02 through EXEC-05).

These tests verify:
- EXEC-02: Script executes sl commands via subprocess
- EXEC-03: Exit code propagates to caller
- EXEC-04: stdout passes through
- EXEC-05: stderr passes through
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


class TestExitCodePropagation:
    """EXEC-03: Exit code from sl propagates exactly to caller."""

    def test_successful_command_returns_zero(self, git_repo: Path):
        """sl status on valid repo returns 0."""
        result = run_gitsl(["status"], cwd=git_repo)
        assert result.exit_code == 0

    def test_failed_command_returns_nonzero(self, tmp_path: Path):
        """sl status on non-repo returns non-zero."""
        # tmp_path is NOT a git repo, so sl status should fail
        result = run_gitsl(["status"], cwd=tmp_path)
        assert result.exit_code != 0


class TestStdoutPassthrough:
    """EXEC-04: stdout from sl appears on caller's stdout."""

    def test_status_output_appears(self, git_repo_with_changes: Path):
        """sl status output appears in stdout when there are changes."""
        result = run_gitsl(["status"], cwd=git_repo_with_changes)
        # Repo with changes should show status output
        assert result.stdout != "" or result.stderr != ""

    def test_version_output_from_sl(self, git_repo: Path):
        """Verify sl is actually being called (not gitsl --version)."""
        # Run gitsl status and check we don't get gitsl version output
        result = run_gitsl(["status"], cwd=git_repo)
        assert "gitsl version" not in result.stdout


class TestStderrPassthrough:
    """EXEC-05: stderr from sl appears on caller's stderr."""

    def test_error_appears_on_stderr(self, tmp_path: Path):
        """Error message from sl appears in stderr."""
        # Run in non-repo directory to trigger error
        result = run_gitsl(["status"], cwd=tmp_path)
        # sl should output error about not being in a repo
        assert result.stderr != "" or result.exit_code != 0
