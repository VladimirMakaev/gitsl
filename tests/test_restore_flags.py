"""
E2E tests for git restore flags (CHKT-03, CHKT-04, CHKT-10, CHKT-11).

Tests:
- CHKT-03: --source/-s restores from specific commit
- CHKT-04: --staged/-S prints warning
- CHKT-10: -q/--quiet suppresses output
- CHKT-11: -W/--worktree is accepted (default behavior)
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.restore_flags,
]


# ============================================================
# CHKT-03: --source/-s restores from specific commit
# ============================================================


class TestRestoreSource:
    """CHKT-03: restore --source/-s restores from specific commit."""

    def test_restore_source_short(self, sl_repo_with_commit: Path):
        """git restore -s <commit> <file> restores from specific commit."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()

        # Make changes and commit
        readme.write_text("version 2\n")
        run_command(["sl", "commit", "-m", "version 2"], cwd=sl_repo_with_commit)

        # Restore from parent (previous commit)
        result = run_gitsl(["restore", "-s", ".^", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # File should have original content
        assert readme.read_text() == original

    def test_restore_source_long(self, sl_repo_with_commit: Path):
        """git restore --source=<commit> works."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()

        readme.write_text("version 2\n")
        run_command(["sl", "commit", "-m", "version 2"], cwd=sl_repo_with_commit)

        result = run_gitsl(["restore", "--source=.^", "README.md"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert readme.read_text() == original


# ============================================================
# CHKT-04: --staged/-S prints warning
# ============================================================


class TestRestoreStaged:
    """CHKT-04: restore --staged/-S prints warning about no staging area."""

    def test_restore_staged_warning(self, sl_repo_with_commit: Path):
        """git restore --staged prints warning."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["restore", "--staged", "README.md"],
                          cwd=sl_repo_with_commit)
        # Should still complete
        assert result.exit_code == 0
        # Should print warning about staging
        assert "staged" in result.stderr.lower() or "staging" in result.stderr.lower()

    def test_restore_S_warning(self, sl_repo_with_commit: Path):
        """git restore -S prints warning."""
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified\n")

        result = run_gitsl(["restore", "-S", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "staging" in result.stderr.lower()


# ============================================================
# CHKT-10: -q/--quiet suppresses output
# ============================================================


class TestRestoreQuiet:
    """CHKT-10: restore -q/--quiet suppresses output."""

    def test_restore_quiet(self, sl_repo_with_commit: Path):
        """git restore -q suppresses output."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        result = run_gitsl(["restore", "-q", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == ""
        assert readme.read_text() == original


# ============================================================
# CHKT-11: -W/--worktree is accepted
# ============================================================


class TestRestoreWorktree:
    """CHKT-11: restore -W/--worktree is accepted (default behavior)."""

    def test_restore_worktree_accepted(self, sl_repo_with_commit: Path):
        """git restore -W flag is accepted."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        result = run_gitsl(["restore", "-W", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert readme.read_text() == original

    def test_restore_worktree_long_accepted(self, sl_repo_with_commit: Path):
        """git restore --worktree flag is accepted."""
        readme = sl_repo_with_commit / "README.md"
        original = readme.read_text()
        readme.write_text("modified\n")

        result = run_gitsl(["restore", "--worktree", "README.md"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert readme.read_text() == original
