"""E2E tests for git rev-parse command."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.rev_parse,
]


class TestRevParseShortHead:
    """CMD-07: git rev-parse --short HEAD translates to sl whereami."""

    def test_rev_parse_returns_7_chars(self, sl_repo_with_commit: Path):
        """Output is exactly 7 characters (short hash)."""
        result = run_gitsl(["rev-parse", "--short", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        assert len(output) == 7, f"Expected 7 chars, got {len(output)}: '{output}'"

    def test_rev_parse_returns_hex_chars(self, sl_repo_with_commit: Path):
        """Output is valid hex characters."""
        result = run_gitsl(["rev-parse", "--short", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        assert all(c in "0123456789abcdef" for c in output), f"Invalid hex: '{output}'"

    def test_rev_parse_head_first_order(self, sl_repo_with_commit: Path):
        """Handles 'HEAD --short' order (alternative to '--short HEAD')."""
        result = run_gitsl(["rev-parse", "HEAD", "--short"], cwd=sl_repo_with_commit)
        # Should also work - both args present
        assert result.exit_code == 0


class TestRevParseExitCodes:
    """Exit code handling for rev-parse."""

    def test_rev_parse_fails_in_non_repo(self, tmp_path: Path):
        """Returns non-zero in non-repo directory."""
        result = run_gitsl(["rev-parse", "--short", "HEAD"], cwd=tmp_path)
        assert result.exit_code != 0

    def test_unsupported_variant_returns_error(self, sl_repo_with_commit: Path):
        """Unsupported rev-parse variants return error."""
        # Use a truly unsupported flag
        result = run_gitsl(["rev-parse", "--some-unknown-flag"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0
        assert "not supported" in result.stderr.lower() or result.exit_code != 0


class TestRevParseShowToplevel:
    """REVP-01: git rev-parse --show-toplevel returns repo root."""

    def test_show_toplevel_returns_absolute_path(self, sl_repo_with_commit: Path):
        """--show-toplevel returns absolute repository root path."""
        result = run_gitsl(["rev-parse", "--show-toplevel"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        assert output == str(sl_repo_with_commit)

    def test_show_toplevel_from_subdirectory(self, sl_repo_with_commit: Path):
        """--show-toplevel works from subdirectory."""
        subdir = sl_repo_with_commit / "subdir"
        subdir.mkdir()
        result = run_gitsl(["rev-parse", "--show-toplevel"], cwd=subdir)
        assert result.exit_code == 0
        assert result.stdout.strip() == str(sl_repo_with_commit)

    def test_show_toplevel_fails_outside_repo(self, tmp_path: Path):
        """--show-toplevel fails outside repository."""
        result = run_gitsl(["rev-parse", "--show-toplevel"], cwd=tmp_path)
        assert result.exit_code != 0


class TestRevParseGitDir:
    """REVP-02: git rev-parse --git-dir returns .sl/.hg directory."""

    def test_git_dir_returns_vcs_directory(self, sl_repo_with_commit: Path):
        """--git-dir returns .sl or .hg directory path."""
        result = run_gitsl(["rev-parse", "--git-dir"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        # Should end with .sl or .hg
        assert output.endswith(".sl") or output.endswith(".hg")
        # Should be inside repo root
        assert output.startswith(str(sl_repo_with_commit))

    def test_git_dir_fails_outside_repo(self, tmp_path: Path):
        """--git-dir fails outside repository."""
        result = run_gitsl(["rev-parse", "--git-dir"], cwd=tmp_path)
        assert result.exit_code != 0


class TestRevParseIsInsideWorkTree:
    """REVP-03: git rev-parse --is-inside-work-tree returns true/false."""

    def test_is_inside_work_tree_returns_true(self, sl_repo_with_commit: Path):
        """--is-inside-work-tree returns 'true' inside repository."""
        result = run_gitsl(["rev-parse", "--is-inside-work-tree"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == "true"

    def test_is_inside_work_tree_returns_false_outside(self, tmp_path: Path):
        """--is-inside-work-tree returns 'false' outside repository."""
        result = run_gitsl(["rev-parse", "--is-inside-work-tree"], cwd=tmp_path)
        # Note: git returns exit code 0 even outside repo
        assert result.exit_code == 0
        assert result.stdout.strip() == "false"


class TestRevParseAbbrevRef:
    """REVP-04: git rev-parse --abbrev-ref HEAD returns bookmark name."""

    def test_abbrev_ref_returns_bookmark_name(self, sl_repo_with_commit: Path):
        """--abbrev-ref HEAD returns current bookmark name."""
        # Create and activate a bookmark
        run_command(["sl", "bookmark", "my-feature"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rev-parse", "--abbrev-ref", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == "my-feature"

    def test_abbrev_ref_returns_head_when_detached(self, sl_repo_with_commit: Path):
        """--abbrev-ref HEAD returns 'HEAD' when no bookmark active."""
        # Deactivate any bookmark by going to a commit without bookmark
        run_command(["sl", "bookmark", "-d", "master"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rev-parse", "--abbrev-ref", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should return "HEAD" or empty bookmark name when detached
        output = result.stdout.strip()
        assert output in ("HEAD", "")


class TestRevParseVerify:
    """REVP-05: git rev-parse --verify validates object reference."""

    def test_verify_valid_ref_returns_hash(self, sl_repo_with_commit: Path):
        """--verify with valid ref returns full hash."""
        result = run_gitsl(["rev-parse", "--verify", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        output = result.stdout.strip()
        # Should be 40-character hex hash
        assert len(output) == 40
        assert all(c in "0123456789abcdef" for c in output)

    def test_verify_invalid_ref_fails(self, sl_repo_with_commit: Path):
        """--verify with invalid ref returns error."""
        result = run_gitsl(["rev-parse", "--verify", "nonexistent-ref-xyz"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0
        assert "fatal" in result.stderr.lower() or result.exit_code == 128

    def test_verify_bookmark_returns_hash(self, sl_repo_with_commit: Path):
        """--verify with bookmark name returns commit hash."""
        run_command(["sl", "bookmark", "test-bookmark"], cwd=sl_repo_with_commit)

        result = run_gitsl(["rev-parse", "--verify", "test-bookmark"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert len(result.stdout.strip()) == 40


class TestRevParseSymbolic:
    """REVP-06: git rev-parse --symbolic outputs in symbolic form."""

    def test_symbolic_head_returns_head(self, sl_repo_with_commit: Path):
        """--symbolic HEAD returns 'HEAD'."""
        result = run_gitsl(["rev-parse", "--symbolic", "HEAD"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == "HEAD"

    def test_symbolic_ref_returns_ref(self, sl_repo_with_commit: Path):
        """--symbolic with ref name returns that ref name."""
        result = run_gitsl(["rev-parse", "--symbolic", "master"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert result.stdout.strip() == "master"
