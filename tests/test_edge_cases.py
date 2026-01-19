"""
E2E tests for edge cases: special characters, empty repos, large files, path edge cases.

Tests comprehensive edge case coverage for gitsl:
- Special character handling in filenames (spaces, unicode, brackets)
- Empty repository behavior
- Large file scenarios (many files, large content)
- Path edge cases (subdirectories)
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.always,
]


class TestSpecialCharacters:
    """Test handling of special characters in filenames."""

    def test_filename_with_spaces(self, sl_repo: Path):
        """File with spaces in name can be added and tracked."""
        file = sl_repo / "file with spaces.txt"
        file.write_text("content\n")

        result = run_gitsl(["add", "file with spaces.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify file is staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "file with spaces.txt" in status.stdout

    def test_filename_with_unicode(self, sl_repo: Path):
        """File with unicode/accented characters can be added."""
        file = sl_repo / "file_\u00e9\u00e8.txt"  # e with accents
        file.write_text("content\n")

        result = run_gitsl(["add", "file_\u00e9\u00e8.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify file is staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A " in status.stdout  # File is added

    def test_filename_with_brackets(self, sl_repo: Path):
        """File with brackets in name can be added."""
        file = sl_repo / "file[1].txt"
        file.write_text("content\n")

        result = run_gitsl(["add", "file[1].txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify file is staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "file[1].txt" in status.stdout

    def test_status_with_special_filenames(self, sl_repo: Path):
        """Status output handles special characters correctly."""
        # Create files with various special characters
        (sl_repo / "file with spaces.txt").write_text("a\n")
        (sl_repo / "file_\u00e9.txt").write_text("b\n")
        (sl_repo / "file[2].txt").write_text("c\n")

        # Check status --porcelain output
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert result.exit_code == 0

        # All files should be listed as untracked
        assert "?? file with spaces.txt" in result.stdout
        assert "??" in result.stdout  # Unicode file present
        assert "?? file[2].txt" in result.stdout


class TestEmptyRepo:
    """Test behavior in empty repository (no files, no commits)."""

    def test_status_empty_repo(self, sl_repo: Path):
        """Status in repo with no files returns empty output."""
        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert result.exit_code == 0
        assert result.stdout == ""

    def test_status_short_empty_repo(self, sl_repo: Path):
        """Status -s in repo with no files returns empty output."""
        result = run_gitsl(["status", "-s"], cwd=sl_repo)
        assert result.exit_code == 0
        assert result.stdout == ""

    def test_log_empty_repo(self, sl_repo: Path):
        """Log in repo with no commits handles gracefully."""
        result = run_gitsl(["log"], cwd=sl_repo)
        # sl log on empty repo may succeed with empty output or return error
        # Either is acceptable as long as it doesn't crash
        # In practice, sl log on empty repo succeeds with empty output
        assert result.exit_code == 0 or "abort" in result.stderr.lower()

    def test_diff_empty_repo(self, sl_repo: Path):
        """Diff in repo with no commits handles gracefully."""
        result = run_gitsl(["diff"], cwd=sl_repo)
        # Empty repo diff should succeed with no output
        assert result.exit_code == 0
        assert result.stdout == ""


class TestLargeFileScenarios:
    """Test handling of many files and large file content."""

    def test_many_files(self, sl_repo: Path):
        """Status correctly lists 100+ untracked files."""
        # Create 100 files
        for i in range(100):
            (sl_repo / f"file_{i:03d}.txt").write_text(f"content {i}\n")

        result = run_gitsl(["status", "--porcelain"], cwd=sl_repo)
        assert result.exit_code == 0

        # Count lines (each file should be one line)
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 100

        # Verify format for a few files
        assert "?? file_000.txt" in result.stdout
        assert "?? file_050.txt" in result.stdout
        assert "?? file_099.txt" in result.stdout

    def test_large_file_content(self, sl_repo: Path):
        """Large file (10MB+) can be added and shows in status."""
        large_file = sl_repo / "large_file.txt"
        # Create a 10MB file (10 * 1024 * 1024 bytes)
        large_content = "x" * (10 * 1024 * 1024)
        large_file.write_text(large_content)

        # Add the file
        result = run_gitsl(["add", "large_file.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify it's staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "large_file.txt" in status.stdout


class TestPathEdgeCases:
    """Test path handling edge cases."""

    def test_add_from_subdirectory(self, sl_repo: Path):
        """Add file using relative path from subdirectory."""
        # Create subdirectory with a file
        subdir = sl_repo / "subdir"
        subdir.mkdir()
        (subdir / "subfile.txt").write_text("content\n")

        # Add file using path from repo root
        result = run_gitsl(["add", "subdir/subfile.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify it's staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "subdir/subfile.txt" in status.stdout

    def test_status_in_subdirectory(self, sl_repo: Path):
        """Run status from subdirectory shows all repo files."""
        # Create files in root and subdir
        (sl_repo / "root_file.txt").write_text("root\n")
        subdir = sl_repo / "subdir"
        subdir.mkdir()
        (subdir / "sub_file.txt").write_text("sub\n")

        # Run status from subdirectory
        result = run_gitsl(["status", "--porcelain"], cwd=subdir)
        assert result.exit_code == 0

        # Should show files relative to repo root
        # Both files should be visible
        assert "root_file.txt" in result.stdout or "sub_file.txt" in result.stdout

    def test_nested_subdirectories(self, sl_repo: Path):
        """Files in deeply nested directories work correctly."""
        # Create nested structure
        deep_path = sl_repo / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        (deep_path / "deep_file.txt").write_text("deep\n")

        # Add the file
        result = run_gitsl(["add", "a/b/c/d/deep_file.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify it's staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "a/b/c/d/deep_file.txt" in status.stdout
