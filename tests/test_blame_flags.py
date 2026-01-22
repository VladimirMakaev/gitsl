"""E2E tests for git blame flags (BLAM-01 through BLAM-07)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.blame,
]


class TestBlamePassThrough:
    """Tests for blame flags that pass through directly."""

    def test_blame_ignore_whitespace_w(self, sl_repo_with_commit: Path):
        """BLAM-01: git blame -w ignores all whitespace."""
        result = run_gitsl(["blame", "-w", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert len(result.stdout) > 0

    def test_blame_ignore_whitespace_long(self, sl_repo_with_commit: Path):
        """BLAM-01: git blame --ignore-all-space ignores whitespace."""
        result = run_gitsl(["blame", "--ignore-all-space", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert len(result.stdout) > 0

    def test_blame_show_number_n(self, sl_repo_with_commit: Path):
        """BLAM-07: git blame -n shows original line numbers."""
        result = run_gitsl(["blame", "-n", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_blame_show_number_long(self, sl_repo_with_commit: Path):
        """BLAM-07: git blame --show-number shows line numbers."""
        result = run_gitsl(["blame", "--show-number", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestBlameTranslation:
    """Tests for blame flags that require translation."""

    def test_blame_ignore_space_change_b(self, sl_repo_with_commit: Path):
        """BLAM-02: git blame -b translates to sl annotate --ignore-space-change."""
        # git -b means "ignore space changes" but sl -b means "blank SHA for boundary"
        # Our handler translates to --ignore-space-change
        result = run_gitsl(["blame", "-b", "README.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should not show blank hashes (which would happen if we passed -b directly)
        # Verify we get normal annotate output
        assert len(result.stdout) > 0


class TestBlameUnsupported:
    """Tests for blame flags that are unsupported (warn and skip)."""

    def test_blame_line_range_L_warning(self, sl_repo_with_commit: Path):
        """BLAM-03: git blame -L warns about unsupported line range."""
        result = run_gitsl(["blame", "-L", "1,5", "README.md"], cwd=sl_repo_with_commit)
        # Should warn but still run without the flag
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()
        # Should still produce output (full file annotation)
        assert len(result.stdout) > 0 or result.exit_code == 0

    def test_blame_line_range_L_attached(self, sl_repo_with_commit: Path):
        """BLAM-03: git blame -L1,5 with attached value."""
        result = run_gitsl(["blame", "-L1,5", "README.md"], cwd=sl_repo_with_commit)
        # Should warn
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_blame_show_email_e_warning(self, sl_repo_with_commit: Path):
        """BLAM-04: git blame -e warns about unsupported show email."""
        result = run_gitsl(["blame", "-e", "README.md"], cwd=sl_repo_with_commit)
        # Should warn
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_blame_show_email_long_warning(self, sl_repo_with_commit: Path):
        """BLAM-04: git blame --show-email warns."""
        result = run_gitsl(["blame", "--show-email", "README.md"], cwd=sl_repo_with_commit)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_blame_porcelain_p_warning(self, sl_repo_with_commit: Path):
        """BLAM-05: git blame -p warns about unsupported porcelain."""
        result = run_gitsl(["blame", "-p", "README.md"], cwd=sl_repo_with_commit)
        # Should warn
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_blame_porcelain_long_warning(self, sl_repo_with_commit: Path):
        """BLAM-05: git blame --porcelain warns."""
        result = run_gitsl(["blame", "--porcelain", "README.md"], cwd=sl_repo_with_commit)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_blame_long_hash_l_warning(self, sl_repo_with_commit: Path):
        """BLAM-06: git blame -l warns about semantic mismatch."""
        # CRITICAL: sl -l means "line number at first appearance" not "long hash"
        result = run_gitsl(["blame", "-l", "README.md"], cwd=sl_repo_with_commit)
        # Should warn - must not pass through (would change output meaning)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()
