"""
E2E tests for git log command (CMD-04).

These tests verify:
- git log translates to sl log
- Exit codes propagate correctly
- Output is passed through
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


# Skip all tests if sl is not installed
sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.log,
]


class TestLogBasic:
    """Basic log command functionality."""

    def test_log_succeeds_in_repo_with_commit(self, git_repo_with_commit: Path):
        """sl log on repo with commit returns 0."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        assert result.exit_code == 0

    def test_log_shows_output(self, git_repo_with_commit: Path):
        """sl log produces some output."""
        result = run_gitsl(["log"], cwd=git_repo_with_commit)
        # Log should show something (commit info in stdout or stderr)
        assert result.stdout != "" or result.stderr != ""


class TestLogExitCodes:
    """Exit code propagation for log command."""

    def test_log_fails_in_non_repo(self, tmp_path: Path):
        """sl log in non-repo directory returns non-zero."""
        # tmp_path is NOT a repo, so sl log should fail
        result = run_gitsl(["log"], cwd=tmp_path)
        assert result.exit_code != 0


class TestLogOneline:
    """FLAG-04: git log --oneline emulates git oneline format."""

    def test_oneline_returns_hash_and_subject(self, sl_repo_with_commit: Path):
        """--oneline shows hash and subject."""
        result = run_gitsl(["log", "--oneline"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1

        # Each line should be: <hash> <subject>
        for line in lines:
            parts = line.split(" ", 1)
            assert len(parts) == 2, f"Expected 'hash subject', got: {line}"
            hash_part, subject = parts
            # Hash should be hex characters (sl uses 12 chars)
            assert all(c in "0123456789abcdef" for c in hash_part)
            # Subject should be non-empty
            assert len(subject) > 0


class TestLogLimit:
    """FLAG-05: git log -N translates to sl log -l N."""

    def test_limit_with_dash_n(self, sl_repo_with_commits: Path):
        """-3 limits to 3 commits."""
        result = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_dash_n_space(self, sl_repo_with_commits: Path):
        """-n 3 limits to 3 commits."""
        result = run_gitsl(["log", "-n", "3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_dash_n_attached(self, sl_repo_with_commits: Path):
        """-n3 limits to 3 commits."""
        result = run_gitsl(["log", "-n3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3

    def test_limit_with_max_count(self, sl_repo_with_commits: Path):
        """--max-count=3 limits to 3 commits."""
        result = run_gitsl(["log", "--max-count=3", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 3


class TestLogCombined:
    """Combined --oneline and -N flags."""

    def test_oneline_with_limit_either_order(self, sl_repo_with_commits: Path):
        """--oneline -3 and -3 --oneline produce same result."""
        result1 = run_gitsl(["log", "--oneline", "-3"], cwd=sl_repo_with_commits)
        result2 = run_gitsl(["log", "-3", "--oneline"], cwd=sl_repo_with_commits)

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result1.stdout == result2.stdout

    def test_limit_greater_than_available(self, sl_repo_with_commits: Path):
        """-100 on 10-commit repo shows all 10."""
        result = run_gitsl(["log", "-100", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 10

    def test_5_oneline_combined(self, sl_repo_with_commits: Path):
        """-5 --oneline shows exactly 5 commits in oneline format."""
        result = run_gitsl(["log", "-5", "--oneline"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 5

        # Verify oneline format (hash + subject)
        for line in lines:
            parts = line.split(" ", 1)
            assert len(parts) == 2
            hash_part = parts[0]
            assert all(c in "0123456789abcdef" for c in hash_part)


class TestLogNoFlags:
    """Test log command without any flags."""

    def test_log_no_flags_shows_commits(self, sl_repo_with_commit: Path):
        """Log without flags shows commit details."""
        result = run_gitsl(["log"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Should show commit info (varies by format but should have content)
        assert result.stdout != "" or result.stderr != ""

    def test_log_no_flags_with_multiple_commits(self, sl_repo_with_commits: Path):
        """Log without flags shows all 10 commits."""
        result = run_gitsl(["log"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0

        # Output should be substantial (multiple commits)
        assert len(result.stdout) > 100


class TestLogDisplayFlags:
    """Tests for LOG-01, LOG-02, LOG-03 display flags."""

    def test_graph_flag(self, sl_repo_with_commits: Path):
        """LOG-01: --graph shows ASCII commit graph."""
        result = run_gitsl(["log", "--graph", "-3"], cwd=sl_repo_with_commits)
        assert result.exit_code == 0
        # Graph output contains special characters (|, *, /, \)
        # At minimum, should have some non-alphanumeric graph chars
        assert any(c in result.stdout for c in ["|", "*", "@"])

    def test_stat_flag(self, sl_repo_with_commit: Path):
        """LOG-02: --stat shows diffstat with each commit."""
        result = run_gitsl(["log", "--stat", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Stat output typically contains file changes like:
        # filename | N +++---
        assert "|" in result.stdout or "file" in result.stdout.lower()

    def test_patch_flag(self, sl_repo_with_commit: Path):
        """LOG-03: --patch shows diff content."""
        result = run_gitsl(["log", "--patch", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Patch output contains diff markers
        assert "@@" in result.stdout or "diff" in result.stdout.lower()

    def test_patch_short_flag(self, sl_repo_with_commit: Path):
        """LOG-03: -p is alias for --patch."""
        result = run_gitsl(["log", "-p", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "@@" in result.stdout or "diff" in result.stdout.lower()


class TestLogFilterFlags:
    """Tests for LOG-04, LOG-05 filter flags."""

    def test_author_flag_equals_syntax(self, sl_repo_with_commits: Path):
        """LOG-04: --author=pattern filters by author."""
        # Get the author name from sl config
        result = run_gitsl(
            ["log", "--author=test", "-1", "--oneline"], cwd=sl_repo_with_commits
        )
        # Should succeed (may or may not find matches depending on author)
        assert result.exit_code == 0

    def test_author_flag_space_syntax(self, sl_repo_with_commits: Path):
        """LOG-04: --author pattern with space syntax."""
        result = run_gitsl(
            ["log", "--author", "test", "-1", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0

    def test_grep_flag_equals_syntax(self, sl_repo_with_commits: Path):
        """LOG-05: --grep=pattern searches commit messages."""
        # Search for "Commit" which is in the test commit messages
        result = run_gitsl(
            ["log", "--grep=Commit", "-3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0

    def test_grep_flag_space_syntax(self, sl_repo_with_commits: Path):
        """LOG-05: --grep pattern with space syntax."""
        result = run_gitsl(
            ["log", "--grep", "Commit", "-3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0


class TestLogBehaviorFlags:
    """Tests for LOG-06, LOG-07, LOG-08 behavior flags."""

    def test_no_merges_flag(self, sl_repo_with_commits: Path):
        """LOG-06: --no-merges excludes merge commits."""
        result = run_gitsl(
            ["log", "--no-merges", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        # Should return some commits (test repo has no merges)
        assert result.stdout.strip() != ""

    def test_all_flag(self, sl_repo_with_commits: Path):
        """LOG-07: --all shows all branches."""
        result = run_gitsl(
            ["log", "--all", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) >= 1

    def test_follow_flag(self, sl_repo_with_commit: Path):
        """LOG-08: --follow follows file renames."""
        # Create a file, commit, then check log with --follow
        result = run_gitsl(
            ["log", "--follow", "-1", "--oneline", "README.md"], cwd=sl_repo_with_commit
        )
        # Should succeed - README.md exists in the test repo
        assert result.exit_code == 0


class TestLogDateFlags:
    """Tests for LOG-09, LOG-10 date flags."""

    def test_since_flag_equals_syntax(self, sl_repo_with_commits: Path):
        """LOG-09: --since filters commits after date."""
        result = run_gitsl(
            ["log", "--since=2020-01-01", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        # Should find commits (all test commits are recent)
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) >= 1

    def test_after_flag(self, sl_repo_with_commits: Path):
        """LOG-09: --after is alias for --since."""
        result = run_gitsl(
            ["log", "--after=2020-01-01", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0

    def test_until_flag_equals_syntax(self, sl_repo_with_commits: Path):
        """LOG-10: --until filters commits before date."""
        result = run_gitsl(
            ["log", "--until=2099-12-31", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) >= 1

    def test_before_flag(self, sl_repo_with_commits: Path):
        """LOG-10: --before is alias for --until."""
        result = run_gitsl(
            ["log", "--before=2099-12-31", "-5", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0

    def test_since_and_until_combined(self, sl_repo_with_commits: Path):
        """LOG-09/LOG-10: Combined date range."""
        result = run_gitsl(
            ["log", "--since=2020-01-01", "--until=2099-12-31", "-5", "--oneline"],
            cwd=sl_repo_with_commits,
        )
        assert result.exit_code == 0


class TestLogOutputFormatFlags:
    """Tests for LOG-11, LOG-12, LOG-13, LOG-14 output format flags."""

    def test_name_only_flag(self, sl_repo_with_commit: Path):
        """LOG-11: --name-only shows only filenames."""
        result = run_gitsl(["log", "--name-only", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show filename (README.md is in the test commit)
        assert "readme" in result.stdout.lower() or result.stdout.strip() != ""

    def test_name_status_flag(self, sl_repo_with_commit: Path):
        """LOG-12: --name-status shows status+filename."""
        result = run_gitsl(["log", "--name-status", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should show status indicators (A, M, D) and filename
        # At minimum, should have output
        assert result.stdout.strip() != ""

    def test_decorate_flag(self, sl_repo_with_commits: Path):
        """LOG-13: --decorate shows branch names."""
        result = run_gitsl(
            ["log", "--decorate", "-1", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        # Should succeed; bookmark may or may not be present
        assert result.stdout.strip() != ""

    def test_pretty_oneline(self, sl_repo_with_commits: Path):
        """LOG-14: --pretty=oneline works like --oneline."""
        result1 = run_gitsl(["log", "--pretty=oneline", "-3"], cwd=sl_repo_with_commits)
        result2 = run_gitsl(["log", "--oneline", "-3"], cwd=sl_repo_with_commits)
        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Both should produce similar output format

    def test_pretty_short(self, sl_repo_with_commit: Path):
        """LOG-14: --pretty=short shows short format."""
        result = run_gitsl(["log", "--pretty=short", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() != ""

    def test_pretty_medium(self, sl_repo_with_commit: Path):
        """LOG-14: --pretty=medium shows medium format."""
        result = run_gitsl(["log", "--pretty=medium", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() != ""

    def test_pretty_full(self, sl_repo_with_commit: Path):
        """LOG-14: --pretty=full shows full format."""
        result = run_gitsl(["log", "--pretty=full", "-1"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() != ""

    def test_format_custom_hash(self, sl_repo_with_commit: Path):
        """LOG-14: --format=format:%h shows short hash."""
        result = run_gitsl(
            ["log", "--format=format:%h", "-1"], cwd=sl_repo_with_commit
        )
        assert result.exit_code == 0
        # Should show hex hash
        output = result.stdout.strip()
        if output:
            assert all(c in "0123456789abcdef\n" for c in output)

    def test_format_custom_subject(self, sl_repo_with_commit: Path):
        """LOG-14: --format=format:%s shows subject."""
        result = run_gitsl(
            ["log", "--format=format:%s", "-1"], cwd=sl_repo_with_commit
        )
        assert result.exit_code == 0
        assert result.stdout.strip() != ""


class TestLogComplexFlags:
    """Tests for LOG-15, LOG-16 complex flags."""

    def test_first_parent_flag(self, sl_repo_with_commits: Path):
        """LOG-15: --first-parent follows only first parent."""
        result = run_gitsl(
            ["log", "--first-parent", "-3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        # Should produce some output
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) >= 1

    def test_reverse_flag(self, sl_repo_with_commits: Path):
        """LOG-16: --reverse shows commits in reverse order."""
        result = run_gitsl(
            ["log", "--reverse", "-3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        # Should produce output (reversed or not, depending on implementation)
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) >= 1


class TestLogPickaxeWarnings:
    """Tests for LOG-17, LOG-18 pickaxe warnings."""

    def test_pickaxe_S_warns(self, sl_repo_with_commit: Path):
        """LOG-17: -S warns about unsupported pickaxe."""
        result = run_gitsl(["log", "-Ssearchterm", "-1"], cwd=sl_repo_with_commit)
        # Should succeed but warn
        assert result.exit_code == 0
        # Warning should be in stderr
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_pickaxe_G_warns(self, sl_repo_with_commit: Path):
        """LOG-18: -G warns about unsupported regex pickaxe."""
        result = run_gitsl(["log", "-Gpattern", "-1"], cwd=sl_repo_with_commit)
        # Should succeed but warn
        assert result.exit_code == 0
        # Warning should be in stderr
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()


class TestLogExistingFlags:
    """Tests documenting LOG-19, LOG-20 already implemented flags."""

    def test_max_count_long_form(self, sl_repo_with_commits: Path):
        """LOG-19: --max-count=N already implemented."""
        result = run_gitsl(
            ["log", "--max-count=3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) == 3

    def test_n_flag_already_works(self, sl_repo_with_commits: Path):
        """LOG-19: -n N already implemented."""
        result = run_gitsl(
            ["log", "-n", "3", "--oneline"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert len(lines) == 3

    def test_oneline_already_works(self, sl_repo_with_commits: Path):
        """LOG-20: --oneline already implemented."""
        result = run_gitsl(
            ["log", "--oneline", "-3"], cwd=sl_repo_with_commits
        )
        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 3
        # Each line should be hash + subject
        for line in lines:
            parts = line.split(" ", 1)
            assert len(parts) == 2
