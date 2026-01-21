"""E2E tests for git diff flag support (DIFF-01 through DIFF-12).

These tests verify that gitsl properly translates git diff flags to
Sapling equivalents or produces appropriate warnings for unsupported features.
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.diff,
]


# ============================================================
# Fixtures for diff testing
# ============================================================


@pytest.fixture
def sl_repo_with_changes(tmp_path: Path) -> Path:
    """
    Create a Sapling repo with uncommitted changes for diff testing.

    Has:
    - Initial commit with README.md and file1.txt
    - Uncommitted modification to file1.txt
    - New untracked file new_file.txt (not added)
    """
    run_command(["sl", "init"], cwd=tmp_path)
    run_command(["sl", "config", "--local", "ui.username", "Test User <test@test.com>"], cwd=tmp_path)

    # Create initial files and commit
    readme = tmp_path / "README.md"
    readme.write_text("# Test Repository\n")
    file1 = tmp_path / "file1.txt"
    file1.write_text("Original content\nLine 2\nLine 3\n")

    run_command(["sl", "add", "README.md", "file1.txt"], cwd=tmp_path)
    run_command(["sl", "commit", "-m", "Initial commit"], cwd=tmp_path)

    # Make modifications
    file1.write_text("Modified content\nLine 2\nLine 3\nLine 4\n")

    # Add file to track it (so sl diff sees it)
    # Note: sl diff shows uncommitted changes to tracked files

    return tmp_path


@pytest.fixture
def sl_repo_with_whitespace_changes(tmp_path: Path) -> Path:
    """
    Create a Sapling repo with whitespace-only changes.

    Has:
    - Initial commit with file that has normal spacing
    - Uncommitted changes with only whitespace differences
    """
    run_command(["sl", "init"], cwd=tmp_path)
    run_command(["sl", "config", "--local", "ui.username", "Test User <test@test.com>"], cwd=tmp_path)

    # Create file with normal spacing
    file1 = tmp_path / "whitespace.txt"
    file1.write_text("hello world\nfoo bar\n")

    run_command(["sl", "add", "whitespace.txt"], cwd=tmp_path)
    run_command(["sl", "commit", "-m", "Initial commit"], cwd=tmp_path)

    # Change only whitespace (multiple spaces instead of single)
    file1.write_text("hello  world\nfoo   bar\n")

    return tmp_path


# ============================================================
# Direct pass-through tests (DIFF-01, 02, 03)
# ============================================================


class TestDiffStatFlag:
    """DIFF-01: --stat produces diffstat summary."""

    def test_diff_stat_DIFF_01(self, sl_repo_with_changes: Path):
        """--stat shows diffstat format with insertions/deletions."""
        result = run_gitsl(["diff", "--stat"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Stat output typically contains | and +/- indicators
        assert "|" in result.stdout or "+" in result.stdout or "-" in result.stdout


class TestDiffIgnoreWhitespace:
    """DIFF-02 and DIFF-03: Whitespace ignore flags."""

    def test_diff_ignore_all_space_DIFF_02(self, sl_repo_with_whitespace_changes: Path):
        """-w ignores all whitespace changes."""
        result = run_gitsl(["diff", "-w"], cwd=sl_repo_with_whitespace_changes)
        assert result.exit_code == 0
        # With -w, whitespace-only changes should produce minimal or no diff
        # Output should not contain actual diff content (no @@ markers)
        assert "@@" not in result.stdout

    def test_diff_ignore_all_space_long_DIFF_02(self, sl_repo_with_whitespace_changes: Path):
        """--ignore-all-space ignores all whitespace changes."""
        result = run_gitsl(["diff", "--ignore-all-space"], cwd=sl_repo_with_whitespace_changes)
        assert result.exit_code == 0
        assert "@@" not in result.stdout

    def test_diff_ignore_space_change_DIFF_03(self, sl_repo_with_whitespace_changes: Path):
        """-b ignores changes in amount of whitespace."""
        result = run_gitsl(["diff", "-b"], cwd=sl_repo_with_whitespace_changes)
        assert result.exit_code == 0
        # With -b, changes in whitespace amount should be ignored
        assert "@@" not in result.stdout

    def test_diff_ignore_space_change_long_DIFF_03(self, sl_repo_with_whitespace_changes: Path):
        """--ignore-space-change ignores changes in amount of whitespace."""
        result = run_gitsl(["diff", "--ignore-space-change"], cwd=sl_repo_with_whitespace_changes)
        assert result.exit_code == 0
        assert "@@" not in result.stdout


# ============================================================
# Context lines test (DIFF-04)
# ============================================================


class TestDiffUnifiedContext:
    """DIFF-04: -U<n>/--unified=<n> controls context lines."""

    def test_diff_unified_attached_DIFF_04(self, sl_repo_with_changes: Path):
        """-U5 attached format sets 5 context lines."""
        result = run_gitsl(["diff", "-U5"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Should produce diff output
        assert "@@" in result.stdout or result.stdout.strip() != ""

    def test_diff_unified_separate_DIFF_04(self, sl_repo_with_changes: Path):
        """-U 5 separate format sets 5 context lines."""
        result = run_gitsl(["diff", "-U", "5"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "@@" in result.stdout or result.stdout.strip() != ""

    def test_diff_unified_equals_DIFF_04(self, sl_repo_with_changes: Path):
        """--unified=5 equals format sets 5 context lines."""
        result = run_gitsl(["diff", "--unified=5"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "@@" in result.stdout or result.stdout.strip() != ""


# ============================================================
# Name output tests (DIFF-05, 06)
# ============================================================


class TestDiffNameOutput:
    """DIFF-05 and DIFF-06: Name-only and name-status output."""

    def test_diff_name_only_DIFF_05(self, sl_repo_with_changes: Path):
        """--name-only outputs only filenames."""
        result = run_gitsl(["diff", "--name-only"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Should show filename (file1.txt was modified)
        assert "file1.txt" in result.stdout

    def test_diff_name_status_DIFF_06(self, sl_repo_with_changes: Path):
        """--name-status outputs status+filename format."""
        result = run_gitsl(["diff", "--name-status"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Should show status indicator (M for modified) and filename
        output = result.stdout.strip()
        assert "file1" in output
        # Status output format: M file1.txt or similar
        assert any(c in output for c in ["M", "A", "D", "R", "!"])


# ============================================================
# Warning tests (DIFF-07 through DIFF-12)
# ============================================================


class TestDiffStagedWarning:
    """DIFF-07: --staged/--cached warns about no staging area."""

    def test_diff_staged_warning_DIFF_07(self, sl_repo_with_changes: Path):
        """--staged produces warning about no staging area."""
        result = run_gitsl(["diff", "--staged"], cwd=sl_repo_with_changes)
        # Should succeed (warning is not an error)
        assert result.exit_code == 0
        # Warning should be in stderr
        assert "staging area" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_diff_cached_warning_DIFF_07(self, sl_repo_with_changes: Path):
        """--cached produces warning about no staging area."""
        result = run_gitsl(["diff", "--cached"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "staging area" in result.stderr.lower() or "warning" in result.stderr.lower()


class TestDiffRawWarning:
    """DIFF-08: --raw warns about unsupported format."""

    def test_diff_raw_warning_DIFF_08(self, sl_repo_with_changes: Path):
        """--raw produces warning about unsupported format."""
        result = run_gitsl(["diff", "--raw"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Warning about --raw in stderr
        assert "warning" in result.stderr.lower() or "--raw" in result.stderr.lower()


class TestDiffFindRenamesWarning:
    """DIFF-09: -M/--find-renames warns about no rename detection."""

    def test_diff_find_renames_warning_DIFF_09(self, sl_repo_with_changes: Path):
        """-M produces warning about no rename detection."""
        result = run_gitsl(["diff", "-M"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Warning should mention sl mv
        assert "sl mv" in result.stderr or "warning" in result.stderr.lower()

    def test_diff_find_renames_long_warning_DIFF_09(self, sl_repo_with_changes: Path):
        """--find-renames produces warning about no rename detection."""
        result = run_gitsl(["diff", "--find-renames"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "sl mv" in result.stderr or "warning" in result.stderr.lower()

    def test_diff_find_renames_with_threshold_DIFF_09(self, sl_repo_with_changes: Path):
        """-M50 produces warning about no rename detection."""
        result = run_gitsl(["diff", "-M50"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "sl mv" in result.stderr or "warning" in result.stderr.lower()


class TestDiffFindCopiesWarning:
    """DIFF-10: -C/--find-copies warns about no copy detection."""

    def test_diff_find_copies_warning_DIFF_10(self, sl_repo_with_changes: Path):
        """-C produces warning about no copy detection."""
        result = run_gitsl(["diff", "-C"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Warning should mention sl copy
        assert "sl copy" in result.stderr or "warning" in result.stderr.lower()

    def test_diff_find_copies_long_warning_DIFF_10(self, sl_repo_with_changes: Path):
        """--find-copies produces warning about no copy detection."""
        result = run_gitsl(["diff", "--find-copies"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "sl copy" in result.stderr or "warning" in result.stderr.lower()

    def test_diff_find_copies_with_threshold_DIFF_10(self, sl_repo_with_changes: Path):
        """-C50 produces warning about no copy detection."""
        result = run_gitsl(["diff", "-C50"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "sl copy" in result.stderr or "warning" in result.stderr.lower()


class TestDiffWordDiffWarning:
    """DIFF-11: --word-diff warns about unsupported feature."""

    def test_diff_word_diff_warning_DIFF_11(self, sl_repo_with_changes: Path):
        """--word-diff produces warning about unsupported feature."""
        result = run_gitsl(["diff", "--word-diff"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Warning should mention word-diff or external tools
        assert "word-diff" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_diff_word_diff_with_mode_DIFF_11(self, sl_repo_with_changes: Path):
        """--word-diff=color produces warning about unsupported feature."""
        result = run_gitsl(["diff", "--word-diff=color"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "word-diff" in result.stderr.lower() or "warning" in result.stderr.lower()


class TestDiffColorMovedWarning:
    """DIFF-12: --color-moved warns about unsupported feature."""

    def test_diff_color_moved_warning_DIFF_12(self, sl_repo_with_changes: Path):
        """--color-moved produces warning about unsupported feature."""
        result = run_gitsl(["diff", "--color-moved"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        # Warning should mention color-moved
        assert "color-moved" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_diff_color_moved_with_mode_DIFF_12(self, sl_repo_with_changes: Path):
        """--color-moved=blocks produces warning about unsupported feature."""
        result = run_gitsl(["diff", "--color-moved=blocks"], cwd=sl_repo_with_changes)
        assert result.exit_code == 0
        assert "color-moved" in result.stderr.lower() or "warning" in result.stderr.lower()
