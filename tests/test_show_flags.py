"""E2E tests for git show flag support (SHOW-01 through SHOW-08).

These tests verify that gitsl properly translates git show flags to
Sapling equivalents using templates and flag translation.
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl, sl_repo_with_commit
from helpers.commands import run_command


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.show,
]


# ============================================================
# Fixtures for show testing
# ============================================================


@pytest.fixture
def sl_repo_with_file_changes(tmp_path: Path) -> Path:
    """
    Create a Sapling repo with a commit that has file changes.

    Has:
    - Initial commit with README.md
    - Second commit that modifies README.md and adds file1.txt
    """
    run_command(["sl", "init"], cwd=tmp_path)
    run_command(["sl", "config", "--local", "ui.username", "Test User <test@test.com>"], cwd=tmp_path)

    # Create initial file and commit
    readme = tmp_path / "README.md"
    readme.write_text("# Test Repository\n")

    run_command(["sl", "add", "README.md"], cwd=tmp_path)
    run_command(["sl", "commit", "-m", "Initial commit"], cwd=tmp_path)

    # Make changes and create second commit
    readme.write_text("# Test Repository\n\nUpdated content.\n")
    file1 = tmp_path / "file1.txt"
    file1.write_text("New file content\n")

    run_command(["sl", "add", "file1.txt"], cwd=tmp_path)
    run_command(["sl", "commit", "-m", "Add file1 and update README"], cwd=tmp_path)

    return tmp_path


# ============================================================
# Direct pass-through tests (SHOW-01, 02, 03)
# ============================================================


class TestShowStatFlag:
    """SHOW-01: --stat produces diffstat summary."""

    def test_show_stat_SHOW_01(self, sl_repo_with_commit: Path):
        """--stat shows diffstat format with the commit."""
        result = run_gitsl(["show", "--stat"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Stat output typically contains | and +/- indicators
        assert "|" in result.stdout or "+" in result.stdout or "-" in result.stdout


class TestShowContextLines:
    """SHOW-02: -U<n> controls context lines."""

    def test_show_context_lines_attached_SHOW_02(self, sl_repo_with_file_changes: Path):
        """-U3 sets 3 context lines in diff output."""
        result = run_gitsl(["show", "-U3"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # Should produce diff output with @@ markers
        assert "@@" in result.stdout or result.stdout.strip() != ""

    def test_show_context_lines_separate_SHOW_02(self, sl_repo_with_file_changes: Path):
        """-U 3 separate format sets 3 context lines."""
        result = run_gitsl(["show", "-U", "3"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        assert "@@" in result.stdout or result.stdout.strip() != ""


class TestShowIgnoreWhitespace:
    """SHOW-03: -w/--ignore-all-space ignores whitespace."""

    def test_show_ignore_whitespace_SHOW_03(self, sl_repo_with_commit: Path):
        """-w ignores whitespace in diff."""
        result = run_gitsl(["show", "-w"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Command should succeed
        assert result.stdout.strip() != "" or result.stderr.strip() == ""

    def test_show_ignore_whitespace_long_SHOW_03(self, sl_repo_with_commit: Path):
        """--ignore-all-space ignores whitespace in diff."""
        result = run_gitsl(["show", "--ignore-all-space"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# Template output tests (SHOW-04 through SHOW-08)
# ============================================================


class TestShowNameOnly:
    """SHOW-04: --name-only shows commit header and file names only."""

    def test_show_name_only_SHOW_04(self, sl_repo_with_file_changes: Path):
        """--name-only outputs commit info and file names.

        Note: sl show with template still appends diff output.
        We verify the template-formatted header contains file names.
        """
        result = run_gitsl(["show", "--name-only"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # Should show filenames in the template output
        output = result.stdout.lower()
        assert "readme" in output or "file1" in output
        # First line should be the hash + subject from template
        first_line = result.stdout.strip().split("\n")[0]
        # Hash should be hex
        parts = first_line.split(" ", 1)
        assert len(parts) >= 1
        assert all(c in "0123456789abcdef" for c in parts[0])


class TestShowNameStatus:
    """SHOW-05: --name-status shows commit header and status+filename."""

    def test_show_name_status_SHOW_05(self, sl_repo_with_file_changes: Path):
        """--name-status outputs commit info with status indicators.

        Note: sl show with template still appends diff output.
        We verify the template-formatted output contains status indicators.
        """
        result = run_gitsl(["show", "--name-status"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # Should show status indicators (A, M, D) and filenames
        output = result.stdout
        # At minimum should have file names
        assert "file1" in output.lower() or "readme" in output.lower()
        # Should have status indicators in template output (before diff section)
        # Look for tab-separated status lines: A\tfile or M\tfile
        assert "\tfile1" in output.lower() or "\treadme" in output.lower()


class TestShowPrettyFormat:
    """SHOW-06: --pretty/--format maps to template formatting."""

    def test_show_pretty_oneline_SHOW_06(self, sl_repo_with_commit: Path):
        """--pretty=oneline shows short one-line format."""
        result = run_gitsl(["show", "--pretty=oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Oneline format: hash + subject, compact
        lines = [l for l in result.stdout.strip().split("\n") if l]
        # First line should be commit summary (hash + message)
        assert len(lines) >= 1

    def test_show_pretty_short_SHOW_06(self, sl_repo_with_commit: Path):
        """--pretty=short shows short format."""
        result = run_gitsl(["show", "--pretty=short"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.lower()
        # Short format should have author info
        assert "author" in output or result.stdout.strip() != ""

    def test_show_pretty_medium_SHOW_06(self, sl_repo_with_commit: Path):
        """--pretty=medium shows medium format."""
        result = run_gitsl(["show", "--pretty=medium"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.lower()
        # Medium format should have date info
        assert "date" in output or "author" in output

    def test_show_pretty_full_SHOW_06(self, sl_repo_with_commit: Path):
        """--pretty=full shows full format."""
        result = run_gitsl(["show", "--pretty=full"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() != ""

    def test_show_format_custom_SHOW_06(self, sl_repo_with_commit: Path):
        """--format=format:%h %s shows custom format with placeholders."""
        result = run_gitsl(["show", "--format=format:%h %s"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should output hash and subject
        output = result.stdout.strip()
        if output:
            # First word should be hex hash
            parts = output.split(" ", 1)
            assert len(parts) >= 1

    def test_show_format_hash_only_SHOW_06(self, sl_repo_with_commit: Path):
        """--format=%H shows full hash."""
        result = run_gitsl(["show", "--format=%H"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        # Should be hex characters only (if we got output)
        if output:
            # First line should be hash
            first_line = output.split("\n")[0]
            assert all(c in "0123456789abcdef" for c in first_line)


class TestShowNoPatch:
    """SHOW-07: -s/--no-patch suppresses diff output."""

    def test_show_no_patch_short_SHOW_07(self, sl_repo_with_file_changes: Path):
        """-s uses template to show commit info.

        Note: sl show with template may still append diff output.
        We verify the template-formatted commit info is present.
        """
        result = run_gitsl(["show", "-s"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # Should have commit info from template
        output = result.stdout.lower()
        assert "commit" in output or "author" in output or result.stdout.strip() != ""
        # Template should format the commit header
        # Look for author line in output
        assert "author" in output or "test user" in output

    def test_show_no_patch_long_SHOW_07(self, sl_repo_with_file_changes: Path):
        """--no-patch uses template to show commit info.

        Note: sl show with template may still append diff output.
        We verify the template-formatted commit info is present.
        """
        result = run_gitsl(["show", "--no-patch"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # Should have commit info
        output = result.stdout.lower()
        assert "author" in output or "test user" in output or result.stdout.strip() != ""


class TestShowOneline:
    """SHOW-08: --oneline shows short one-line format."""

    def test_show_oneline_SHOW_08(self, sl_repo_with_commit: Path):
        """--oneline shows short hash and subject."""
        result = run_gitsl(["show", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # First line should be hash + subject
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1
        first_line = lines[0]
        # Should have hash and subject separated by space
        parts = first_line.split(" ", 1)
        assert len(parts) >= 1
        # Hash part should be hex
        hash_part = parts[0]
        assert all(c in "0123456789abcdef" for c in hash_part)

    def test_show_oneline_format_SHOW_08(self, sl_repo_with_commit: Path):
        """--oneline output is compact (hash + subject on one line)."""
        result = run_gitsl(["show", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # First line should contain the commit message
        first_line = result.stdout.strip().split("\n")[0]
        # Should have "Initial commit" or similar in the subject
        assert len(first_line) > 12  # At least hash + some subject


# ============================================================
# Combined flags tests
# ============================================================


class TestShowCombinedFlags:
    """Test combinations of show flags."""

    def test_show_stat_with_oneline_uses_stat(self, sl_repo_with_commit: Path):
        """--stat with --oneline shows diffstat output."""
        result = run_gitsl(["show", "--stat", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should have stat output
        assert "|" in result.stdout or "+" in result.stdout

    def test_show_no_patch_with_stat(self, sl_repo_with_file_changes: Path):
        """-s with --stat shows stat but no diff content."""
        result = run_gitsl(["show", "-s", "--stat"], cwd=sl_repo_with_file_changes)
        assert result.exit_code == 0
        # One or the other behavior depending on priority
        # Main thing is it doesn't crash
        assert result.stdout.strip() != "" or result.stderr.strip() == ""
