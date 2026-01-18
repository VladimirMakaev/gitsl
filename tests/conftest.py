"""
Shared test fixtures for gitsl E2E testing.
"""

from pathlib import Path
from typing import List, Optional

import pytest

from helpers.commands import CommandResult, run_command


# ============================================================
# GIT COMMAND HELPERS
# ============================================================


def run_git(args: List[str], cwd: Path, env: Optional[dict] = None) -> CommandResult:
    """
    Run git command in specified directory.

    Args:
        args: Git subcommand and arguments (without 'git')
        cwd: Working directory for the command
        env: Optional environment variables to merge

    Returns:
        CommandResult with captured output
    """
    return run_command(["git"] + args, cwd=cwd, env=env)


def run_gitsl(args: List[str], cwd: Path, env: Optional[dict] = None) -> CommandResult:
    """
    Run gitsl command in specified directory.

    This runs gitsl.py via subprocess, testing the actual CLI behavior.

    Args:
        args: gitsl subcommand and arguments (without 'gitsl')
        cwd: Working directory for the command
        env: Optional environment variables to merge

    Returns:
        CommandResult with captured output
    """
    # Get path to gitsl.py relative to tests directory
    gitsl_path = Path(__file__).parent.parent / "gitsl.py"
    return run_command(["python", str(gitsl_path)] + args, cwd=cwd, env=env)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """
    Create a temporary git repository.

    Configured with test user for commits.
    Automatically cleaned up after test.

    Returns:
        Path to the initialized git repository
    """
    # Initialize repo
    run_git(["init"], cwd=tmp_path)

    # Configure for CI environments
    run_git(["config", "user.email", "test@test.com"], cwd=tmp_path)
    run_git(["config", "user.name", "Test User"], cwd=tmp_path)

    return tmp_path


@pytest.fixture
def git_repo_with_commit(git_repo: Path) -> Path:
    """
    Git repo with initial commit.

    Creates README.md and commits it.

    Returns:
        Path to the git repository with one commit
    """
    readme = git_repo / "README.md"
    readme.write_text("# Test Repository\n")

    run_git(["add", "README.md"], cwd=git_repo)
    run_git(["commit", "-m", "Initial commit"], cwd=git_repo)

    return git_repo


@pytest.fixture
def git_repo_with_changes(git_repo_with_commit: Path) -> Path:
    """
    Git repo with uncommitted changes.

    Has:
    - Modified README.md (tracked, modified)
    - new_file.txt (untracked)

    Returns:
        Path to the git repository with changes
    """
    # Modify existing file
    readme = git_repo_with_commit / "README.md"
    readme.write_text("# Test Repository\n\nModified content.\n")

    # Add untracked file
    new_file = git_repo_with_commit / "new_file.txt"
    new_file.write_text("New untracked file\n")

    return git_repo_with_commit


@pytest.fixture
def git_repo_with_branch(git_repo_with_commit: Path) -> Path:
    """
    Git repo with a feature branch.

    Creates a branch named 'feature' (but stays on main/master).

    Returns:
        Path to the git repository with feature branch
    """
    run_git(["branch", "feature"], cwd=git_repo_with_commit)
    return git_repo_with_commit
