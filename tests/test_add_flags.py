"""
E2E tests for git add flags (ADD-01 through ADD-05).

Tests add flag translation to Sapling equivalents.
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.add_flags,
]


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def sl_repo_with_ignored(sl_repo: Path) -> Path:
    """Sapling repo with ignored file setup."""
    (sl_repo / ".gitignore").write_text("*.ignored\n")
    run_command(["sl", "add", ".gitignore"], cwd=sl_repo)
    run_command(["sl", "commit", "-m", "Add gitignore"], cwd=sl_repo)

    # Create ignored file
    (sl_repo / "test.ignored").write_text("ignored content\n")

    return sl_repo


# ============================================================
# ADD-01: -A/--all -> addremove verification
# ============================================================


class TestAddAllVerification:
    """ADD-01: Verify -A/--all to addremove translation."""

    def test_add_A_stages_new_files(self, sl_repo: Path):
        """-A stages new files via addremove."""
        (sl_repo / "new1.txt").write_text("new1\n")
        (sl_repo / "new2.txt").write_text("new2\n")

        result = run_gitsl(["add", "-A"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A new1.txt" in status.stdout
        assert "A new2.txt" in status.stdout

    def test_add_all_marks_deleted(self, sl_repo_with_commit: Path):
        """--all marks deleted files for removal."""
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["add", "--all"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout

    def test_add_A_with_pathspec(self, sl_repo: Path):
        """-A with pathspec limits scope."""
        subdir = sl_repo / "subdir"
        subdir.mkdir()
        (subdir / "sub.txt").write_text("sub\n")
        (sl_repo / "root.txt").write_text("root\n")

        result = run_gitsl(["add", "-A", "subdir/"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A subdir/sub.txt" in status.stdout
        # Root file should still be untracked
        assert "? root.txt" in status.stdout


# ============================================================
# ADD-02: -u/--update verification
# ============================================================


class TestAddUpdateVerification:
    """ADD-02: Verify -u/--update emulation."""

    def test_add_u_ignores_untracked(self, sl_repo_with_commit: Path):
        """-u does NOT stage untracked files."""
        (sl_repo_with_commit / "untracked.txt").write_text("untracked\n")
        (sl_repo_with_commit / "README.md").write_text("modified\n")

        result = run_gitsl(["add", "-u"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "? untracked.txt" in status.stdout

    def test_add_update_marks_deleted(self, sl_repo_with_commit: Path):
        """--update marks deleted tracked files for removal."""
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["add", "--update"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout

    def test_add_u_with_pathspec(self, sl_repo_with_commit: Path):
        """-u with pathspec respects path filter."""
        # Create and commit a file in subdir
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        subfile = subdir / "tracked.txt"
        subfile.write_text("sub content\n")
        run_command(["sl", "add", "subdir/tracked.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir file"], cwd=sl_repo_with_commit)

        # Delete both files
        (sl_repo_with_commit / "README.md").unlink()
        subfile.unlink()

        # Run -u only on subdir
        result = run_gitsl(["add", "-u", "subdir/"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R subdir/tracked.txt" in status.stdout
        assert "! README.md" in status.stdout  # Still deleted, not removed


# ============================================================
# ADD-03: --dry-run/-n preview
# ============================================================


class TestAddDryRun:
    """ADD-03: --dry-run/-n shows what would be added."""

    def test_dry_run_short_flag(self, sl_repo: Path):
        """-n shows preview without adding."""
        (sl_repo / "newfile.txt").write_text("content\n")

        result = run_gitsl(["add", "-n", "newfile.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # File should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "? newfile.txt" in status.stdout

    def test_dry_run_long_flag(self, sl_repo: Path):
        """--dry-run shows preview without adding."""
        (sl_repo / "newfile.txt").write_text("content\n")

        result = run_gitsl(["add", "--dry-run", "newfile.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # File should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "? newfile.txt" in status.stdout

    def test_dry_run_with_all(self, sl_repo: Path):
        """-n works with -A."""
        (sl_repo / "new1.txt").write_text("new1\n")
        (sl_repo / "new2.txt").write_text("new2\n")

        result = run_gitsl(["add", "-A", "-n"], cwd=sl_repo)
        assert result.exit_code == 0

        # Files should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "? new1.txt" in status.stdout
        assert "? new2.txt" in status.stdout

    def test_dry_run_with_update(self, sl_repo_with_commit: Path):
        """-n works with -u."""
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["add", "-u", "-n"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # File should still be missing, not removed
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "! README.md" in status.stdout


# ============================================================
# ADD-04: -f/--force warning
# ============================================================


class TestAddForce:
    """ADD-04: -f/--force prints warning (not supported)."""

    def test_force_short_flag_warning(self, sl_repo_with_ignored: Path):
        """-f prints warning about limitation."""
        result = run_gitsl(["add", "-f", "test.ignored"], cwd=sl_repo_with_ignored)

        # Should have warning in stderr
        assert "warning" in result.stderr.lower() or "not" in result.stderr.lower()

    def test_force_long_flag_warning(self, sl_repo_with_ignored: Path):
        """--force prints warning about limitation."""
        result = run_gitsl(["add", "--force", "test.ignored"], cwd=sl_repo_with_ignored)

        # Should have warning in stderr
        assert "warning" in result.stderr.lower() or "not" in result.stderr.lower()


# ============================================================
# ADD-05: -v/--verbose shows files
# ============================================================


class TestAddVerbose:
    """ADD-05: -v/--verbose shows files as they are added."""

    def test_verbose_short_flag(self, sl_repo: Path):
        """-v adds files successfully."""
        (sl_repo / "newfile.txt").write_text("content\n")

        result = run_gitsl(["add", "-v", "newfile.txt"], cwd=sl_repo)

        assert result.exit_code == 0
        # Verify file was actually added
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A newfile.txt" in status.stdout

    def test_verbose_long_flag(self, sl_repo: Path):
        """--verbose adds files successfully."""
        (sl_repo / "newfile.txt").write_text("content\n")

        result = run_gitsl(["add", "--verbose", "newfile.txt"], cwd=sl_repo)

        assert result.exit_code == 0
        # Verify file was actually added
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A newfile.txt" in status.stdout

    def test_verbose_multiple_files(self, sl_repo: Path):
        """-v shows all files being added."""
        (sl_repo / "file1.txt").write_text("content1\n")
        (sl_repo / "file2.txt").write_text("content2\n")

        result = run_gitsl(["add", "-v", "file1.txt", "file2.txt"], cwd=sl_repo)

        assert result.exit_code == 0
        # Verify files were actually added
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A file1.txt" in status.stdout
        assert "A file2.txt" in status.stdout

    def test_verbose_with_dry_run(self, sl_repo: Path):
        """-v with -n shows what would be added."""
        (sl_repo / "newfile.txt").write_text("content\n")

        result = run_gitsl(["add", "-v", "-n", "newfile.txt"], cwd=sl_repo)

        assert result.exit_code == 0
        # File should still be untracked
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "? newfile.txt" in status.stdout
