"""
Self-validation tests for the E2E test harness.

These tests verify that fixtures and helpers work correctly before
using them to test gitsl.
"""

import tempfile
from pathlib import Path

import pytest

from helpers.commands import CommandResult
from helpers.comparison import (
    assert_commands_equal,
    compare_exact,
    compare_semantic,
)
from conftest import run_git, run_gitsl


# ============================================================
# TestCommandResult - Test the dataclass
# ============================================================


class TestCommandResult:
    """Test CommandResult dataclass behavior."""

    def test_success_property_true(self):
        """CommandResult with exit_code=0 has success=True."""
        result = CommandResult(stdout="", stderr="", exit_code=0)
        assert result.success is True

    def test_success_property_false(self):
        """CommandResult with exit_code=1 has success=False."""
        result = CommandResult(stdout="", stderr="", exit_code=1)
        assert result.success is False

    def test_success_property_false_other_codes(self):
        """CommandResult with other non-zero exit codes has success=False."""
        result = CommandResult(stdout="", stderr="", exit_code=128)
        assert result.success is False

    def test_stores_stdout(self):
        """Verify stdout is captured."""
        result = CommandResult(stdout="hello world", stderr="", exit_code=0)
        assert result.stdout == "hello world"

    def test_stores_stderr(self):
        """Verify stderr is captured."""
        result = CommandResult(stdout="", stderr="error message", exit_code=1)
        assert result.stderr == "error message"


# ============================================================
# TestRunGit - Test run_git helper
# ============================================================


class TestRunGit:
    """Test run_git helper function."""

    def test_captures_stdout(self, git_repo):
        """run_git(["status"]) returns stdout with "On branch"."""
        result = run_git(["status"], cwd=git_repo)
        assert "On branch" in result.stdout

    def test_captures_exit_code_success(self, git_repo):
        """run_git(["status"]) returns exit_code=0."""
        result = run_git(["status"], cwd=git_repo)
        assert result.exit_code == 0
        assert result.success is True

    def test_captures_exit_code_failure(self, git_repo):
        """run_git with invalid path returns non-zero exit_code."""
        # Use a command that fails - checking status of nonexistent path
        result = run_git(["status", "nonexistent_path_12345"], cwd=git_repo)
        # Git doesn't necessarily fail on nonexistent path in status
        # Use a different command that reliably fails
        result = run_git(["checkout", "nonexistent_branch_12345"], cwd=git_repo)
        assert result.exit_code != 0
        assert result.success is False

    def test_captures_stderr_on_error(self, git_repo):
        """run_git with invalid args has non-empty stderr."""
        result = run_git(["checkout", "nonexistent_branch_12345"], cwd=git_repo)
        assert result.stderr != ""


# ============================================================
# TestRunGitsl - Test run_gitsl helper
# ============================================================


class TestRunGitsl:
    """Test run_gitsl helper function."""

    def test_runs_gitsl_script(self, git_repo):
        """run_gitsl(["--version"]) returns exit_code=0."""
        result = run_gitsl(["--version"], cwd=git_repo)
        assert result.exit_code == 0
        assert result.success is True

    def test_captures_gitsl_stdout(self, git_repo):
        """run_gitsl(["--version"]) stdout contains "gitsl"."""
        result = run_gitsl(["--version"], cwd=git_repo)
        assert "gitsl" in result.stdout


# ============================================================
# TestGitRepoFixture - Test git_repo fixture
# ============================================================


class TestGitRepoFixture:
    """Test git_repo fixture."""

    def test_creates_git_directory(self, git_repo):
        """(git_repo / ".git").is_dir() is True."""
        assert (git_repo / ".git").is_dir()

    def test_is_valid_repo(self, git_repo):
        """run_git(["status"]) succeeds."""
        result = run_git(["status"], cwd=git_repo)
        assert result.success is True

    def test_is_temporary(self, git_repo):
        """git_repo path is under system temp dir (or not in project)."""
        project_dir = Path(__file__).parent.parent.resolve()
        git_repo_resolved = git_repo.resolve()
        # The git_repo should not be under our project directory
        assert not str(git_repo_resolved).startswith(str(project_dir))
        # It should be under a temp directory (resolve symlinks for macOS /var -> /private/var)
        temp_dir = Path(tempfile.gettempdir()).resolve()
        assert str(git_repo_resolved).startswith(str(temp_dir))


# ============================================================
# TestGitRepoWithCommit - Test git_repo_with_commit fixture
# ============================================================


class TestGitRepoWithCommit:
    """Test git_repo_with_commit fixture."""

    def test_has_initial_commit(self, git_repo_with_commit):
        """git log --oneline contains 'Initial commit'."""
        result = run_git(["log", "--oneline"], cwd=git_repo_with_commit)
        assert "Initial commit" in result.stdout

    def test_has_readme(self, git_repo_with_commit):
        """README.md exists."""
        readme = git_repo_with_commit / "README.md"
        assert readme.exists()

    def test_clean_working_tree(self, git_repo_with_commit):
        """git status --porcelain is empty."""
        result = run_git(["status", "--porcelain"], cwd=git_repo_with_commit)
        assert result.stdout.strip() == ""


# ============================================================
# TestGitRepoWithChanges - Test git_repo_with_changes fixture
# ============================================================


class TestGitRepoWithChanges:
    """Test git_repo_with_changes fixture."""

    def test_has_modified_file(self, git_repo_with_changes):
        """git status --porcelain contains ' M README.md'."""
        result = run_git(["status", "--porcelain"], cwd=git_repo_with_changes)
        assert " M README.md" in result.stdout

    def test_has_untracked_file(self, git_repo_with_changes):
        """git status --porcelain contains '?? new_file.txt'."""
        result = run_git(["status", "--porcelain"], cwd=git_repo_with_changes)
        assert "?? new_file.txt" in result.stdout


# ============================================================
# TestGitRepoWithBranch - Test git_repo_with_branch fixture
# ============================================================


class TestGitRepoWithBranch:
    """Test git_repo_with_branch fixture."""

    def test_has_feature_branch(self, git_repo_with_branch):
        """git branch --list contains 'feature'."""
        result = run_git(["branch", "--list"], cwd=git_repo_with_branch)
        assert "feature" in result.stdout


# ============================================================
# TestCompareExact - Test compare_exact function
# ============================================================


class TestCompareExact:
    """Test compare_exact function."""

    def test_identical_strings_match(self):
        """compare_exact("a", "a") is True."""
        assert compare_exact("a", "a") is True

    def test_different_strings_dont_match(self):
        """compare_exact("a", "b") is False."""
        assert compare_exact("a", "b") is False

    def test_whitespace_matters(self):
        """compare_exact("a ", "a") is False."""
        assert compare_exact("a ", "a") is False

    def test_newlines_matter(self):
        """compare_exact("a\\n", "a") is False."""
        assert compare_exact("a\n", "a") is False


# ============================================================
# TestCompareSemantic - Test compare_semantic function
# ============================================================


class TestCompareSemantic:
    """Test compare_semantic function."""

    def test_identical_strings_match(self):
        """compare_semantic("a", "a") is True."""
        assert compare_semantic("a", "a") is True

    def test_leading_trailing_whitespace_ignored(self):
        """compare_semantic(" a ", "a") is True."""
        assert compare_semantic(" a ", "a") is True

    def test_multiple_spaces_collapsed(self):
        """compare_semantic("a  b", "a b") is True."""
        assert compare_semantic("a  b", "a b") is True

    def test_empty_lines_ignored(self):
        """compare_semantic("a\\n\\nb", "a\\nb") is True."""
        assert compare_semantic("a\n\nb", "a\nb") is True

    def test_different_content_fails(self):
        """compare_semantic("a", "b") is False."""
        assert compare_semantic("a", "b") is False

    def test_tab_whitespace_collapsed(self):
        """compare_semantic("a\\tb", "a b") is True."""
        assert compare_semantic("a\tb", "a b") is True


# ============================================================
# TestAssertCommandsEqual - Test assert_commands_equal function
# ============================================================


class TestAssertCommandsEqual:
    """Test assert_commands_equal function."""

    def test_matching_commands_pass(self):
        """Same results don't raise."""
        git_result = CommandResult(stdout="output", stderr="", exit_code=0)
        gitsl_result = CommandResult(stdout="output", stderr="", exit_code=0)
        # Should not raise
        assert_commands_equal(git_result, gitsl_result)

    def test_exit_code_mismatch_fails(self):
        """Different exit codes raise AssertionError."""
        git_result = CommandResult(stdout="output", stderr="", exit_code=0)
        gitsl_result = CommandResult(stdout="output", stderr="", exit_code=1)
        with pytest.raises(AssertionError) as exc_info:
            assert_commands_equal(git_result, gitsl_result)
        assert "Exit code mismatch" in str(exc_info.value)

    def test_stdout_mismatch_fails(self):
        """Different stdout raises AssertionError."""
        git_result = CommandResult(stdout="expected", stderr="", exit_code=0)
        gitsl_result = CommandResult(stdout="actual", stderr="", exit_code=0)
        with pytest.raises(AssertionError) as exc_info:
            assert_commands_equal(git_result, gitsl_result)
        assert "stdout mismatch" in str(exc_info.value)

    def test_semantic_mode_ignores_whitespace(self):
        """Whitespace-only stdout difference passes in semantic mode."""
        git_result = CommandResult(stdout="a  b\n", stderr="", exit_code=0)
        gitsl_result = CommandResult(stdout=" a b ", stderr="", exit_code=0)
        # Should not raise in semantic mode
        assert_commands_equal(git_result, gitsl_result, mode="semantic")

    def test_semantic_mode_still_checks_content(self):
        """Semantic mode still fails on content difference."""
        git_result = CommandResult(stdout="expected", stderr="", exit_code=0)
        gitsl_result = CommandResult(stdout="different", stderr="", exit_code=0)
        with pytest.raises(AssertionError):
            assert_commands_equal(git_result, gitsl_result, mode="semantic")
