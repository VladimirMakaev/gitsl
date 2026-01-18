"""E2E tests for git rev-parse command."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed")


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
        # Without --short or HEAD, should fail
        result = run_gitsl(["rev-parse", "--verify", "master"], cwd=sl_repo_with_commit)
        assert result.exit_code != 0
        assert "only supports" in result.stderr.lower() or result.exit_code != 0
