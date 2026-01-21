"""
E2E tests for git commit flags (COMM-01 through COMM-08).

Tests:
- COMM-01: --amend translates to sl amend
- COMM-02: --no-edit combined with amend uses existing message
- COMM-03: -F/--file translates to sl commit -l
- COMM-04: --author translates to sl commit -u
- COMM-05: --date translates to sl commit -d
- COMM-06: -v/--verbose shows warning
- COMM-07: -s/--signoff adds Signed-off-by trailer
- COMM-08: -n/--no-verify shows warning
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.commit_flags,
]


# ============================================================
# COMM-01: --amend translates to sl amend
# ============================================================


class TestCommitAmend:
    """COMM-01: --amend translates to sl amend."""

    def test_amend_modifies_last_commit(self, sl_repo_with_commit: Path):
        """git commit --amend modifies the last commit."""
        # Modify a file
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("modified content\n")
        run_command(["sl", "add", "README.md"], cwd=sl_repo_with_commit)

        # Amend the commit
        result = run_gitsl(["commit", "--amend", "-m", "Amended message"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify message was changed
        log = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                         cwd=sl_repo_with_commit)
        assert "Amended message" in log.stdout

    def test_amend_includes_new_changes(self, sl_repo_with_commit: Path):
        """git commit --amend includes newly staged changes."""
        # Add new file
        (sl_repo_with_commit / "new.txt").write_text("new content\n")
        run_command(["sl", "add", "new.txt"], cwd=sl_repo_with_commit)

        # Amend
        result = run_gitsl(["commit", "--amend", "-m", "Added new file"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify new file is in the commit
        show = run_command(["sl", "show", "--stat"], cwd=sl_repo_with_commit)
        assert "new.txt" in show.stdout


# ============================================================
# COMM-02: --no-edit with amend uses existing message
# ============================================================


class TestCommitNoEdit:
    """COMM-02: --no-edit with amend uses existing message."""

    def test_amend_no_edit_preserves_message(self, sl_repo_with_commit: Path):
        """git commit --amend --no-edit keeps original message."""
        # Get original message
        log_before = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                                cwd=sl_repo_with_commit)
        original_msg = log_before.stdout.strip()

        # Modify file and amend with --no-edit
        readme = sl_repo_with_commit / "README.md"
        readme.write_text("more content\n")
        run_command(["sl", "add", "README.md"], cwd=sl_repo_with_commit)

        result = run_gitsl(["commit", "--amend", "--no-edit"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Verify message unchanged
        log_after = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                               cwd=sl_repo_with_commit)
        assert log_after.stdout.strip() == original_msg


# ============================================================
# COMM-03: -F/--file translates to sl commit -l
# ============================================================


class TestCommitFile:
    """COMM-03: -F/--file translates to sl commit -l."""

    def test_commit_with_file_message(self, sl_repo: Path):
        """git commit -F <file> uses message from file."""
        # Create file and message file
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        msg_file = sl_repo / "commit_msg.txt"
        msg_file.write_text("Message from file\n")

        result = run_gitsl(["commit", "-F", str(msg_file)], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify message
        log = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                         cwd=sl_repo)
        assert "Message from file" in log.stdout

    def test_commit_with_file_long_form(self, sl_repo: Path):
        """git commit --file=<file> works with long form."""
        (sl_repo / "test2.txt").write_text("content\n")
        run_command(["sl", "add", "test2.txt"], cwd=sl_repo)

        msg_file = sl_repo / "msg2.txt"
        msg_file.write_text("Long form message\n")

        result = run_gitsl(["commit", f"--file={msg_file}"], cwd=sl_repo)
        assert result.exit_code == 0

        log = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                         cwd=sl_repo)
        assert "Long form message" in log.stdout


# ============================================================
# COMM-04: --author translates to sl commit -u
# ============================================================


class TestCommitAuthor:
    """COMM-04: --author translates to sl commit -u."""

    def test_commit_with_custom_author(self, sl_repo: Path):
        """git commit --author sets commit author."""
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-m", "Test",
                           "--author=Custom Author <custom@example.com>"],
                          cwd=sl_repo)
        assert result.exit_code == 0

        # Verify author
        log = run_command(["sl", "log", "-l", "1", "--template", "{author}"],
                         cwd=sl_repo)
        assert "Custom Author" in log.stdout
        assert "custom@example.com" in log.stdout


# ============================================================
# COMM-05: --date translates to sl commit -d
# ============================================================


class TestCommitDate:
    """COMM-05: --date translates to sl commit -d."""

    def test_commit_with_custom_date(self, sl_repo: Path):
        """git commit --date sets commit date."""
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-m", "Test",
                           "--date=2024-01-15 12:00:00"],
                          cwd=sl_repo)
        assert result.exit_code == 0

        # Verify date (sl stores as unix timestamp, check year)
        log = run_command(["sl", "log", "-l", "1", "--template", "{date|isodate}"],
                         cwd=sl_repo)
        assert "2024" in log.stdout


# ============================================================
# COMM-06: -v/--verbose shows warning
# ============================================================


class TestCommitVerbose:
    """COMM-06: -v/--verbose shows warning about different semantics."""

    def test_verbose_shows_note(self, sl_repo: Path):
        """git commit -v prints note about different semantics."""
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-v", "-m", "Test"], cwd=sl_repo)
        # Should succeed and show note
        assert result.exit_code == 0
        assert "note" in result.stderr.lower() or "verbose" in result.stderr.lower()

    def test_verbose_long_form_shows_note(self, sl_repo: Path):
        """git commit --verbose prints note."""
        (sl_repo / "test2.txt").write_text("content\n")
        run_command(["sl", "add", "test2.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "--verbose", "-m", "Test"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "note" in result.stderr.lower() or "verbose" in result.stderr.lower()


# ============================================================
# COMM-07: -s/--signoff adds Signed-off-by trailer
# ============================================================


class TestCommitSignoff:
    """COMM-07: -s/--signoff adds Signed-off-by trailer."""

    def test_signoff_adds_trailer(self, sl_repo: Path):
        """git commit -s adds Signed-off-by line."""
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-m", "Test commit", "-s"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify Signed-off-by trailer in message
        log = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                         cwd=sl_repo)
        assert "Signed-off-by:" in log.stdout

    def test_signoff_long_form(self, sl_repo: Path):
        """git commit --signoff also adds trailer."""
        (sl_repo / "test2.txt").write_text("content\n")
        run_command(["sl", "add", "test2.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-m", "Test", "--signoff"], cwd=sl_repo)
        assert result.exit_code == 0

        log = run_command(["sl", "log", "-l", "1", "--template", "{desc}"],
                         cwd=sl_repo)
        assert "Signed-off-by:" in log.stdout


# ============================================================
# COMM-08: -n/--no-verify shows warning
# ============================================================


class TestCommitNoVerify:
    """COMM-08: -n/--no-verify shows warning about hooks."""

    def test_no_verify_shows_warning(self, sl_repo: Path):
        """git commit --no-verify prints warning."""
        (sl_repo / "test.txt").write_text("content\n")
        run_command(["sl", "add", "test.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "--no-verify", "-m", "Test"], cwd=sl_repo)
        # Should succeed with warning
        assert result.exit_code == 0
        assert "warning" in result.stderr.lower() or "no-verify" in result.stderr.lower()

    def test_no_verify_short_form(self, sl_repo: Path):
        """git commit -n also shows warning."""
        (sl_repo / "test2.txt").write_text("content\n")
        run_command(["sl", "add", "test2.txt"], cwd=sl_repo)

        result = run_gitsl(["commit", "-n", "-m", "Test"], cwd=sl_repo)
        assert result.exit_code == 0
        # Either warning or note about no-verify
        assert "warning" in result.stderr.lower() or "no-verify" in result.stderr.lower() or "pre-commit" in result.stderr.lower()
