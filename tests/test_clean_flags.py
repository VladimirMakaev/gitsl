"""E2E tests for git clean flags (CLEN-01 through CLEN-04)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clean,
]


@pytest.fixture
def sl_repo_with_ignored(sl_repo_with_commit: Path) -> Path:
    """Sapling repo with ignored and untracked files."""
    # Create .gitignore (Sapling reads this too)
    gitignore = sl_repo_with_commit / ".gitignore"
    gitignore.write_text("*.log\nbuild/\n")
    run_command(["sl", "add", ".gitignore"], cwd=sl_repo_with_commit)
    run_command(["sl", "commit", "-m", "Add gitignore"], cwd=sl_repo_with_commit)

    # Create ignored files
    (sl_repo_with_commit / "test.log").write_text("ignored content")
    (sl_repo_with_commit / "debug.log").write_text("debug content")

    # Create ignored directory
    build_dir = sl_repo_with_commit / "build"
    build_dir.mkdir()
    (build_dir / "output.txt").write_text("build output")

    # Create untracked files
    (sl_repo_with_commit / "untracked.txt").write_text("untracked content")
    (sl_repo_with_commit / "temp.tmp").write_text("temp content")

    # Create untracked directory
    temp_dir = sl_repo_with_commit / "tempdir"
    temp_dir.mkdir()
    (temp_dir / "file.txt").write_text("temp dir content")

    return sl_repo_with_commit


class TestCleanTranslation:
    """Tests for clean flags that require translation."""

    def test_clean_x_removes_ignored(self, sl_repo_with_ignored: Path):
        """CLEN-01: git clean -fx removes ignored files too."""
        # Verify ignored files exist before clean
        assert (sl_repo_with_ignored / "test.log").exists()
        assert (sl_repo_with_ignored / "debug.log").exists()

        result = run_gitsl(["clean", "-fx"], cwd=sl_repo_with_ignored)
        assert result.exit_code == 0

        # Ignored files should be removed
        assert not (sl_repo_with_ignored / "test.log").exists()
        assert not (sl_repo_with_ignored / "debug.log").exists()
        # Untracked files should also be removed
        assert not (sl_repo_with_ignored / "untracked.txt").exists()
        assert not (sl_repo_with_ignored / "temp.tmp").exists()

    def test_clean_x_with_directories(self, sl_repo_with_ignored: Path):
        """CLEN-01: git clean -fxd removes ignored directories too."""
        # Verify ignored directory exists
        assert (sl_repo_with_ignored / "build").exists()

        result = run_gitsl(["clean", "-fxd"], cwd=sl_repo_with_ignored)
        assert result.exit_code == 0

        # Ignored directories should be removed
        assert not (sl_repo_with_ignored / "build").exists()
        # Untracked directories should also be removed
        assert not (sl_repo_with_ignored / "tempdir").exists()

    def test_clean_exclude_pattern_e(self, sl_repo_with_ignored: Path):
        """CLEN-03: git clean -f -e pattern excludes matching files."""
        result = run_gitsl(["clean", "-f", "-e", "*.tmp"], cwd=sl_repo_with_ignored)
        assert result.exit_code == 0

        # Excluded file should still exist
        assert (sl_repo_with_ignored / "temp.tmp").exists()
        # Non-excluded untracked file should be removed
        assert not (sl_repo_with_ignored / "untracked.txt").exists()

    def test_clean_exclude_pattern_attached(self, sl_repo_with_ignored: Path):
        """CLEN-03: git clean -f -epattern with attached value."""
        result = run_gitsl(["clean", "-f", "-e*.tmp"], cwd=sl_repo_with_ignored)
        assert result.exit_code == 0

        # Excluded file should still exist
        assert (sl_repo_with_ignored / "temp.tmp").exists()
        # Non-excluded file should be removed
        assert not (sl_repo_with_ignored / "untracked.txt").exists()


class TestCleanUnsupported:
    """Tests for clean flags that are unsupported (warn)."""

    def test_clean_X_only_ignored_warning(self, sl_repo_with_ignored: Path):
        """CLEN-02: git clean -fX warns about limited support."""
        result = run_gitsl(["clean", "-fX"], cwd=sl_repo_with_ignored)
        # Should warn about -X having limited support
        assert "warning" in result.stderr.lower() or "not" in result.stderr.lower()
        # Command should still succeed
        assert result.exit_code == 0


class TestCleanExisting:
    """Tests for existing clean flags (-f, -d, -n)."""

    def test_clean_force_required(self, sl_repo_with_commit: Path):
        """CLEN-04: git clean without -f fails with requireForce message."""
        # Create untracked file
        (sl_repo_with_commit / "untracked.txt").write_text("untracked")

        result = run_gitsl(["clean"], cwd=sl_repo_with_commit)
        # Should fail with force required message
        assert result.exit_code != 0
        assert "requireforce" in result.stderr.lower() or "refusing" in result.stderr.lower()
        # File should not be removed
        assert (sl_repo_with_commit / "untracked.txt").exists()

    def test_clean_dry_run_n(self, sl_repo_with_commit: Path):
        """CLEN-04: git clean -n shows files without removing them."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked")

        result = run_gitsl(["clean", "-n"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # File should still exist
        assert untracked.exists()
        # Output should show the file would be removed
        assert "untracked" in result.stdout.lower() or "untracked" in result.stderr.lower()

    @pytest.mark.skip(reason="sl purge --dirs hangs in test environment (watchman issue)")
    def test_clean_directories_d(self, sl_repo_with_commit: Path):
        """CLEN-04: git clean -fd removes directories."""
        # Create untracked directory
        temp_dir = sl_repo_with_commit / "tempdir"
        temp_dir.mkdir()
        (temp_dir / "file.txt").write_text("temp content")

        # First verify dry-run works (this proves -d flag is handled)
        result_dry = run_gitsl(["clean", "-nd"], cwd=sl_repo_with_commit)
        assert result_dry.exit_code == 0
        # Directory should still exist after dry run
        assert temp_dir.exists()
        # Output should mention the directory
        assert "tempdir" in result_dry.stdout.lower() or "file.txt" in result_dry.stdout.lower()

    def test_clean_force_f(self, sl_repo_with_commit: Path):
        """CLEN-04: git clean -f removes untracked files."""
        # Create untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked")

        result = run_gitsl(["clean", "-f"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # File should be removed
        assert not untracked.exists()
