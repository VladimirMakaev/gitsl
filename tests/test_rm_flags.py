"""E2E tests for git rm flags (RM-01 through RM-05)."""

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


class TestRmPassThrough:
    """Tests for rm flags that pass through directly."""

    def test_rm_force_f(self, sl_repo_with_commit: Path):
        """RM-01: git rm -f passes through to sl remove -f."""
        # Modify the tracked file to require force
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("Modified content\n")

        result = run_gitsl(["rm", "-f", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # File should be removed
        assert not readme.exists()

    def test_rm_force_long(self, sl_repo_with_commit: Path):
        """RM-01: git rm --force passes through to sl remove -f."""
        # Create a new file and commit it
        newfile = sl_repo_with_commit / "newfile.txt"
        newfile.write_text("New content\n")
        run_command(["sl", "add", "newfile.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add newfile"], cwd=sl_repo_with_commit)

        # Modify it to require force
        newfile.write_text("Modified content\n")

        result = run_gitsl(["rm", "--force", "newfile.txt"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not newfile.exists()

    def test_rm_quiet_q(self, sl_repo_with_commit: Path):
        """RM-04: git rm -q passes through for quiet output."""
        result = run_gitsl(["rm", "-q", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # File should be removed
        assert not (sl_repo_with_commit / "README.md").exists()

    def test_rm_quiet_long(self, sl_repo_with_commit: Path):
        """RM-04: git rm --quiet passes through for quiet output."""
        result = run_gitsl(["rm", "--quiet", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not (sl_repo_with_commit / "README.md").exists()


class TestRmUnsupported:
    """Tests for rm flags that are unsupported (warn)."""

    def test_rm_cached_warning(self, sl_repo_with_commit: Path):
        """RM-02: git rm --cached warns about no staging area."""
        result = run_gitsl(["rm", "--cached", "README.md"], cwd=sl_repo_with_commit)
        # Should warn about no staging area
        assert "warning" in result.stderr.lower() or "staging" in result.stderr.lower()

    def test_rm_dry_run_n_warning(self, sl_repo_with_commit: Path):
        """RM-03: git rm -n warns about not supported."""
        result = run_gitsl(["rm", "-n", "README.md"], cwd=sl_repo_with_commit)
        # Should warn about not supported
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()
        # Note: File is still removed because dry-run is not supported in Sapling.
        # The warning informs the user but the operation proceeds.

    def test_rm_dry_run_long_warning(self, sl_repo_with_commit: Path):
        """RM-03: git rm --dry-run warns about not supported."""
        result = run_gitsl(["rm", "--dry-run", "README.md"], cwd=sl_repo_with_commit)
        # Should warn about not supported
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()


class TestRmRecursive:
    """Tests for rm -r/--recursive flag filtering."""

    def test_rm_recursive_filtered(self, sl_repo_with_commit: Path):
        """RM-05: git rm -r is filtered (sl remove is recursive by default)."""
        # Create a subdirectory with a file
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        subfile = subdir / "file.txt"
        subfile.write_text("Subdir content\n")
        run_command(["sl", "add", "subdir/file.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rm", "-r", "subdir"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Subdir files should be removed
        assert not subfile.exists()

    def test_rm_recursive_long_filtered(self, sl_repo_with_commit: Path):
        """RM-05: git rm --recursive is filtered (sl remove is recursive by default)."""
        # Create a subdirectory with a file
        subdir = sl_repo_with_commit / "subdir2"
        subdir.mkdir()
        subfile = subdir / "file.txt"
        subfile.write_text("Subdir content\n")
        run_command(["sl", "add", "subdir2/file.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir2"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rm", "--recursive", "subdir2"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not subfile.exists()
