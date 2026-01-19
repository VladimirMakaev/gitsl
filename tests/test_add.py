"""
E2E tests for git add command (CMD-02, CMD-08, FLAG-03).

Tests:
- git add <files> stages files via sl add
- git add -A stages all changes via sl addremove
- git add --all works same as -A
- git add -u stages only tracked files (ignores untracked)
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.add,
]


class TestAddBasic:
    """CMD-02: git add <files> translates to sl add <files>."""

    def test_add_new_file_succeeds(self, sl_repo: Path):
        """git add stages a new file."""
        new_file = sl_repo / "test.txt"
        new_file.write_text("test content\n")

        result = run_gitsl(["add", "test.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl status
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A test.txt" in status.stdout

    def test_add_multiple_files(self, sl_repo: Path):
        """git add can stage multiple files at once."""
        (sl_repo / "a.txt").write_text("a\n")
        (sl_repo / "b.txt").write_text("b\n")

        result = run_gitsl(["add", "a.txt", "b.txt"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A a.txt" in status.stdout
        assert "A b.txt" in status.stdout


class TestAddAll:
    """CMD-08: git add -A translates to sl addremove."""

    def test_add_all_short_flag(self, sl_repo: Path):
        """git add -A stages new files."""
        (sl_repo / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "-A"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A new.txt" in status.stdout

    def test_add_all_long_flag(self, sl_repo: Path):
        """git add --all works the same as -A."""
        (sl_repo / "new.txt").write_text("new\n")

        result = run_gitsl(["add", "--all"], cwd=sl_repo)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A new.txt" in status.stdout

    def test_add_all_with_deleted_file(self, sl_repo_with_commit: Path):
        """git add -A marks deleted files for removal."""
        # Delete an existing tracked file
        (sl_repo_with_commit / "README.md").unlink()

        result = run_gitsl(["add", "-A"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout or "! README.md" in status.stdout


class TestAddUpdate:
    """FLAG-03: git add -u stages only tracked files (ignores untracked)."""

    def test_add_u_ignores_untracked(self, sl_repo_with_commit: Path):
        """git add -u should NOT stage untracked files."""
        # Create an untracked file
        untracked = sl_repo_with_commit / "untracked.txt"
        untracked.write_text("untracked content\n")

        # Modify the tracked README.md
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("# Modified content\n")

        # Run git add -u
        result = run_gitsl(["add", "-u"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify untracked file is still untracked (? status)
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "? untracked.txt" in status.stdout
        # Modified file is auto-staged by Sapling, so M status
        assert "M README.md" in status.stdout

    def test_add_u_marks_deleted_for_removal(self, sl_repo_with_commit: Path):
        """git add -u marks deleted tracked files for removal."""
        # Delete the tracked README.md
        readme = sl_repo_with_commit / "README.md"
        readme.unlink()

        # Verify file shows as deleted (!) in sl status
        status_before = run_command(["sl", "status", "-d", "-n"], cwd=sl_repo_with_commit)
        assert "README.md" in status_before.stdout

        # Run git add -u
        result = run_gitsl(["add", "-u"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify file is now marked as R (removed)
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout

    def test_add_u_with_pathspec(self, sl_repo_with_commit: Path):
        """git add -u path/ respects pathspec, only affects files in path."""
        # Create subdirectory with a tracked file
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        subfile = subdir / "tracked.txt"
        subfile.write_text("subdir content\n")
        run_command(["sl", "add", "subdir/tracked.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add subdir file"], cwd=sl_repo_with_commit)

        # Delete both files
        (sl_repo_with_commit / "README.md").unlink()
        subfile.unlink()

        # Verify both show as deleted
        status_before = run_command(["sl", "status", "-d", "-n"], cwd=sl_repo_with_commit)
        assert "README.md" in status_before.stdout
        assert "subdir/tracked.txt" in status_before.stdout

        # Run git add -u only on subdir/
        result = run_gitsl(["add", "-u", "subdir/"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Check status
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        # subdir/tracked.txt should be marked R (removed)
        assert "R subdir/tracked.txt" in status.stdout
        # README.md should still be deleted (!) not removed
        assert "! README.md" in status.stdout

    def test_add_u_no_deleted_files(self, sl_repo_with_commit: Path):
        """git add -u succeeds when there are no deleted files."""
        # Modify the tracked README.md (no deletion)
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("# Modified content\n")

        # Run git add -u
        result = run_gitsl(["add", "-u"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify modified file is in expected state (Sapling auto-stages)
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "M README.md" in status.stdout

    def test_add_update_long_flag(self, sl_repo_with_commit: Path):
        """git add --update works the same as -u."""
        # Delete the tracked README.md
        readme = sl_repo_with_commit / "README.md"
        readme.unlink()

        # Run git add --update
        result = run_gitsl(["add", "--update"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify file is now marked as R (removed)
        status = run_command(["sl", "status"], cwd=sl_repo_with_commit)
        assert "R README.md" in status.stdout


class TestAddDot:
    """Test git add . (current directory)."""

    def test_add_dot_current_directory(self, sl_repo: Path):
        """git add . stages all files in current directory."""
        # Create multiple files
        (sl_repo / "file1.txt").write_text("content1\n")
        (sl_repo / "file2.txt").write_text("content2\n")

        # Add with .
        result = run_gitsl(["add", "."], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify both files are staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "A file1.txt" in status.stdout
        assert "A file2.txt" in status.stdout

    def test_add_dot_in_subdirectory(self, sl_repo: Path):
        """git add . from subdirectory adds files in that subdirectory."""
        # Create a subdirectory with files
        subdir = sl_repo / "subdir"
        subdir.mkdir()
        (subdir / "sub1.txt").write_text("sub content 1\n")
        (subdir / "sub2.txt").write_text("sub content 2\n")

        # Also create a file in root
        (sl_repo / "root.txt").write_text("root content\n")

        # Add with . from subdirectory
        result = run_gitsl(["add", "."], cwd=subdir)
        assert result.exit_code == 0

        # Verify subdir files are staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "sub1.txt" in status.stdout
        assert "sub2.txt" in status.stdout

    def test_add_subdirectory_path(self, sl_repo: Path):
        """git add subdir/ stages all files in subdirectory."""
        # Create a subdirectory with files
        subdir = sl_repo / "subdir"
        subdir.mkdir()
        (subdir / "a.txt").write_text("a\n")
        (subdir / "b.txt").write_text("b\n")

        # Also create file in root (should not be staged)
        (sl_repo / "root.txt").write_text("root\n")

        # Add with subdirectory path
        result = run_gitsl(["add", "subdir/"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify subdir files are staged
        status = run_command(["sl", "status"], cwd=sl_repo)
        assert "subdir/a.txt" in status.stdout
        assert "subdir/b.txt" in status.stdout
        # Root file should still be untracked
        assert "? root.txt" in status.stdout
