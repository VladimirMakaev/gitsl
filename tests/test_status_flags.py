"""
E2E tests for git status flags (STAT-01 through STAT-05).

Tests status flag translation to Sapling equivalents.
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.status_flags,
]


# ============================================================
# Fixtures for ignored files
# ============================================================


@pytest.fixture
def sl_repo_with_ignored(sl_repo: Path) -> Path:
    """Sapling repo with an ignored file."""
    # Create .gitignore (sl respects .gitignore)
    (sl_repo / ".gitignore").write_text("*.ignored\n")
    run_command(["sl", "add", ".gitignore"], cwd=sl_repo)
    run_command(["sl", "commit", "-m", "Add gitignore"], cwd=sl_repo)

    # Create ignored file
    (sl_repo / "test.ignored").write_text("ignored content\n")

    return sl_repo


@pytest.fixture
def sl_repo_with_bookmark(sl_repo_with_commit: Path) -> Path:
    """Sapling repo with a named bookmark."""
    run_command(["sl", "bookmark", "feature-branch"], cwd=sl_repo_with_commit)
    return sl_repo_with_commit


# ============================================================
# STAT-01: --ignored shows ignored files
# ============================================================


class TestStatusIgnored:
    """STAT-01: --ignored translates to sl status -i."""

    def test_ignored_flag_shows_ignored_files(self, sl_repo_with_ignored: Path):
        """--ignored includes ignored files in output."""
        result = run_gitsl(["status", "--ignored"], cwd=sl_repo_with_ignored)

        assert result.exit_code == 0
        assert "test.ignored" in result.stdout

    def test_ignored_with_porcelain(self, sl_repo_with_ignored: Path):
        """--ignored with --porcelain shows !! for ignored files."""
        result = run_gitsl(["status", "--ignored", "--porcelain"], cwd=sl_repo_with_ignored)

        assert result.exit_code == 0
        assert "!! test.ignored" in result.stdout

    def test_without_ignored_flag(self, sl_repo_with_ignored: Path):
        """Without --ignored, ignored files are not shown."""
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_ignored)

        assert result.exit_code == 0
        assert "test.ignored" not in result.stdout


# ============================================================
# STAT-02: -b/--branch adds branch info
# ============================================================


class TestStatusBranch:
    """STAT-02: -b/--branch adds branch info to output."""

    def test_branch_flag_with_short(self, sl_repo_with_bookmark: Path):
        """-b with --short shows branch header."""
        result = run_gitsl(["status", "-b", "--short"], cwd=sl_repo_with_bookmark)

        assert result.exit_code == 0
        assert "## feature-branch" in result.stdout

    def test_branch_long_flag(self, sl_repo_with_bookmark: Path):
        """--branch works same as -b."""
        result = run_gitsl(["status", "--branch", "--short"], cwd=sl_repo_with_bookmark)

        assert result.exit_code == 0
        assert "## feature-branch" in result.stdout

    def test_branch_flag_with_porcelain(self, sl_repo_with_bookmark: Path):
        """-b with --porcelain shows branch header."""
        result = run_gitsl(["status", "-b", "--porcelain"], cwd=sl_repo_with_bookmark)

        assert result.exit_code == 0
        assert "## feature-branch" in result.stdout

    def test_sb_combined_flags(self, sl_repo_with_bookmark: Path):
        """-sb (common git shorthand) shows branch and short status."""
        # Note: Combined flags like -sb may need special handling
        # For now, test -s -b separately
        result = run_gitsl(["status", "-s", "-b"], cwd=sl_repo_with_bookmark)

        assert result.exit_code == 0
        assert "## feature-branch" in result.stdout


# ============================================================
# STAT-03: -v/--verbose
# ============================================================


class TestStatusVerbose:
    """STAT-03: -v/--verbose passes through."""

    def test_verbose_flag(self, sl_repo_with_commit: Path):
        """-v flag passes through to sl status."""
        # Modify a file to have something to show
        (sl_repo_with_commit / "README.md").write_text("Modified\n")

        result = run_gitsl(["status", "-v"], cwd=sl_repo_with_commit)

        # Should succeed (may show different format than git)
        assert result.exit_code == 0

    def test_verbose_long_flag(self, sl_repo_with_commit: Path):
        """--verbose flag passes through."""
        (sl_repo_with_commit / "README.md").write_text("Modified\n")

        result = run_gitsl(["status", "--verbose"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0


# ============================================================
# STAT-04: Porcelain status code verification
# ============================================================


class TestPorcelainStatusCodes:
    """STAT-04: Verify --porcelain covers all status codes."""

    def test_all_status_codes_covered(self, sl_repo_with_commit: Path):
        """Verify all sl status codes map to git porcelain codes."""
        # M (modified) -> ' M'
        (sl_repo_with_commit / "README.md").write_text("Modified\n")
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)
        assert " M README.md" in result.stdout

    def test_added_status_code(self, sl_repo: Path):
        """A (added) -> 'A '."""
        (sl_repo / "new.txt").write_text("new\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo)

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert "A  new.txt" in result.stdout

    def test_removed_status_code(self, sl_repo_with_commit: Path):
        """R (removed) -> 'D '."""
        run_command(["sl", "rm", "README.md"], cwd=sl_repo_with_commit)

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)
        assert "D  README.md" in result.stdout

    def test_missing_status_code(self, sl_repo_with_commit: Path):
        """! (missing) -> ' D'."""
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo_with_commit)
        assert " D README.md" in result.stdout

    def test_untracked_status_code(self, sl_repo: Path):
        """? (unknown) -> '??'."""
        (sl_repo / "untracked.txt").write_text("untracked\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert "?? untracked.txt" in result.stdout

    def test_ignored_status_code(self, sl_repo_with_ignored: Path):
        """I (ignored) -> '!!' with --ignored flag."""
        result = run_gitsl(["status", "--porcelain", "--ignored"], cwd=sl_repo_with_ignored)
        assert "!! test.ignored" in result.stdout


# ============================================================
# STAT-05: -u/--untracked-files modes
# ============================================================


class TestStatusUntrackedModes:
    """STAT-05: -u/--untracked-files controls untracked file display."""

    def test_untracked_no_mode(self, sl_repo: Path):
        """-uno suppresses untracked files."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "-uno", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "??" not in result.stdout

    def test_untracked_no_with_space(self, sl_repo: Path):
        """-u no (with space) suppresses untracked files."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "-u", "no", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "??" not in result.stdout

    def test_untracked_files_no_long_form(self, sl_repo: Path):
        """--untracked-files=no suppresses untracked files."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "--untracked-files=no", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "??" not in result.stdout

    def test_untracked_normal_mode(self, sl_repo: Path):
        """-unormal shows untracked files (default behavior)."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "-unormal", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "?? untracked.txt" in result.stdout

    def test_untracked_all_mode(self, sl_repo: Path):
        """-uall shows all untracked files."""
        (sl_repo / "untracked.txt").write_text("content\n")

        result = run_gitsl(["status", "-uall", "--porcelain"], cwd=sl_repo)

        assert result.exit_code == 0
        assert "?? untracked.txt" in result.stdout

    def test_untracked_no_still_shows_tracked_changes(self, sl_repo_with_commit: Path):
        """-uno still shows tracked file changes."""
        # Create untracked file
        (sl_repo_with_commit / "untracked.txt").write_text("untracked\n")
        # Modify tracked file
        (sl_repo_with_commit / "README.md").write_text("Modified\n")

        result = run_gitsl(["status", "-uno", "--porcelain"], cwd=sl_repo_with_commit)

        assert result.exit_code == 0
        assert " M README.md" in result.stdout
        assert "untracked.txt" not in result.stdout
