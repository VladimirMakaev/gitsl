"""
E2E tests for error conditions: sl failures, invalid arguments, missing sl binary.

Tests error handling and propagation:
- sl returning non-zero exit codes
- stderr propagation from sl
- Invalid/unknown commands
- Missing sl binary scenarios
"""

import os
import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


pytestmark = pytest.mark.always


class TestSlErrors:
    """Test handling of sl command failures."""

    @pytest.fixture
    def mock_sl_env(self):
        """Environment with mock sl prepended to PATH."""
        mock_dir = Path(__file__).parent / "mocks"
        new_path = str(mock_dir) + os.pathsep + os.environ.get("PATH", "")
        return {"PATH": new_path}

    def test_sl_returns_nonzero(self, tmp_path: Path, mock_sl_env):
        """Mock sl exits with error, verify gitsl propagates exit code."""
        # Configure mock to exit with code 42
        env = mock_sl_env.copy()
        env["MOCK_SL_EXIT"] = "42"

        # Initialize a git repo so gitsl doesn't fail before calling sl
        run_command(["git", "init"], cwd=tmp_path)
        run_command(["git", "config", "user.email", "test@test.com"], cwd=tmp_path)
        run_command(["git", "config", "user.name", "Test User"], cwd=tmp_path)

        # Run gitsl with mock sl
        result = run_gitsl(["status"], cwd=tmp_path, env=env)

        # gitsl should propagate the exit code from sl
        assert result.exit_code == 42

    def test_sl_stderr_propagates(self, tmp_path: Path, mock_sl_env):
        """Mock sl outputs to stderr, verify gitsl passes through."""
        # Configure mock to output to stderr
        env = mock_sl_env.copy()
        env["MOCK_SL_STDERR"] = "error: something went wrong"
        env["MOCK_SL_EXIT"] = "1"

        # Initialize a git repo
        run_command(["git", "init"], cwd=tmp_path)
        run_command(["git", "config", "user.email", "test@test.com"], cwd=tmp_path)
        run_command(["git", "config", "user.name", "Test User"], cwd=tmp_path)

        # Run gitsl with mock sl
        result = run_gitsl(["status"], cwd=tmp_path, env=env)

        # stderr should be passed through
        assert "something went wrong" in result.stderr

    def test_sl_stdout_propagates(self, tmp_path: Path, mock_sl_env):
        """Mock sl outputs to stdout, verify gitsl passes through."""
        # Configure mock to output to stdout
        env = mock_sl_env.copy()
        env["MOCK_SL_STDOUT"] = "mock output message"
        env["MOCK_SL_EXIT"] = "0"

        # Initialize a git repo
        run_command(["git", "init"], cwd=tmp_path)
        run_command(["git", "config", "user.email", "test@test.com"], cwd=tmp_path)
        run_command(["git", "config", "user.name", "Test User"], cwd=tmp_path)

        # Run gitsl with mock sl
        result = run_gitsl(["status"], cwd=tmp_path, env=env)

        # stdout should be passed through
        assert "mock output message" in result.stdout


class TestInvalidArgs:
    """Test handling of invalid arguments."""

    def test_unknown_command_handled(self, tmp_path: Path):
        """Unknown git command produces unsupported message."""
        result = run_gitsl(["unknowncommand"], cwd=tmp_path)

        # UNSUP-02: unsupported commands exit 0
        assert result.exit_code == 0
        # Should have unsupported message in stderr
        assert "unsupported" in result.stderr.lower()

    def test_no_command_shows_usage(self, tmp_path: Path):
        """Running gitsl with no command shows usage."""
        result = run_gitsl([], cwd=tmp_path)

        # Should fail and show usage
        assert result.exit_code == 1
        assert "usage" in result.stderr.lower()

    def test_help_flag(self, tmp_path: Path):
        """Running gitsl with --help shows help."""
        result = run_gitsl(["--help"], cwd=tmp_path)

        assert result.exit_code == 0
        assert "usage" in result.stdout.lower()
        assert "gitsl" in result.stdout.lower()

    def test_version_flag(self, tmp_path: Path):
        """Running gitsl with --version shows version."""
        result = run_gitsl(["--version"], cwd=tmp_path)

        assert result.exit_code == 0
        assert "gitsl version" in result.stdout.lower()


class TestMissingSl:
    """Test behavior when sl binary is not available.

    Note: These tests modify PATH to simulate missing sl.
    They may be skipped in some CI environments.
    """

    @pytest.fixture
    def empty_path_env(self, tmp_path: Path):
        """Environment with minimal PATH (no sl available).

        Creates a minimal environment where sl cannot be found,
        but Python and basic commands still work.
        """
        # Create a temporary bin directory with just python symlink
        bin_dir = tmp_path / "minimal_bin"
        bin_dir.mkdir()

        # On macOS/Linux, we need at least /usr/bin for basic commands
        # But we exclude the path where sl is installed
        import sys
        python_path = Path(sys.executable).resolve()

        # Create a PATH that has Python but not sl
        # We'll include system paths but filter out sl
        minimal_paths = []

        # Always include Python's directory
        minimal_paths.append(str(python_path.parent))

        # Include /usr/bin for basic system commands if it exists
        if Path("/usr/bin").exists():
            minimal_paths.append("/usr/bin")

        # Build PATH, explicitly excluding any directory containing sl
        sl_path = shutil.which("sl")
        if sl_path:
            sl_dir = str(Path(sl_path).parent)
            minimal_paths = [p for p in minimal_paths if p != sl_dir]

        return {"PATH": os.pathsep.join(minimal_paths)}

    @pytest.mark.skipif(
        shutil.which("sl") is None,
        reason="Need sl installed to test missing sl behavior"
    )
    def test_gitsl_command_in_git_repo_without_sl(self, tmp_path: Path, empty_path_env):
        """gitsl in git repo without sl should fail gracefully for sl-dependent commands."""
        # Initialize as a git repo
        run_command(["git", "init"], cwd=tmp_path)
        run_command(["git", "config", "user.email", "test@test.com"], cwd=tmp_path)
        run_command(["git", "config", "user.name", "Test User"], cwd=tmp_path)

        # Run gitsl status (requires sl)
        result = run_gitsl(["status"], cwd=tmp_path, env=empty_path_env)

        # Should fail because sl is not found
        # The exact error depends on implementation - sl binary not found
        assert result.exit_code != 0 or "sl" in result.stderr.lower()
