"""E2E tests for git grep flags (GREP-01 through GREP-14)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.grep,
]


class TestGrepPassThrough:
    """Tests for grep flags that pass through directly."""

    def test_grep_line_number_n(self, sl_repo_with_commit: Path):
        """GREP-01: git grep -n shows line numbers."""
        result = run_gitsl(["grep", "-n", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Output should contain filename:linenum:content format
        assert ":" in result.stdout

    def test_grep_line_number_long(self, sl_repo_with_commit: Path):
        """GREP-01: git grep --line-number shows line numbers."""
        result = run_gitsl(["grep", "--line-number", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_case_insensitive_i(self, sl_repo_with_commit: Path):
        """GREP-02: git grep -i performs case-insensitive search."""
        result = run_gitsl(["grep", "-i", "TEST"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "Test" in result.stdout or "test" in result.stdout.lower()

    def test_grep_case_insensitive_long(self, sl_repo_with_commit: Path):
        """GREP-02: git grep --ignore-case performs case-insensitive search."""
        result = run_gitsl(["grep", "--ignore-case", "TEST"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_files_only_l(self, sl_repo_with_commit: Path):
        """GREP-03: git grep -l shows only filenames."""
        result = run_gitsl(["grep", "-l", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "README" in result.stdout

    def test_grep_files_only_long(self, sl_repo_with_commit: Path):
        """GREP-03: git grep --files-with-matches shows only filenames."""
        result = run_gitsl(["grep", "--files-with-matches", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert "README" in result.stdout

    def test_grep_word_match_w(self, sl_repo_with_commit: Path):
        """GREP-05: git grep -w matches whole words only."""
        result = run_gitsl(["grep", "-w", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_word_match_long(self, sl_repo_with_commit: Path):
        """GREP-05: git grep --word-regexp matches whole words only."""
        result = run_gitsl(["grep", "--word-regexp", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_fixed_strings_F(self, sl_repo_with_commit: Path):
        """GREP-14: git grep -F treats pattern as literal string."""
        result = run_gitsl(["grep", "-F", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_fixed_strings_long(self, sl_repo_with_commit: Path):
        """GREP-14: git grep --fixed-strings treats pattern as literal."""
        result = run_gitsl(["grep", "--fixed-strings", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestGrepContextLines:
    """Tests for grep context line flags."""

    def test_grep_after_context_A(self, sl_repo_with_commit: Path):
        """GREP-07: git grep -A shows trailing context."""
        result = run_gitsl(["grep", "-A", "1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_after_context_attached(self, sl_repo_with_commit: Path):
        """GREP-07: git grep -A1 with attached value."""
        result = run_gitsl(["grep", "-A1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_before_context_B(self, sl_repo_with_commit: Path):
        """GREP-08: git grep -B shows leading context."""
        result = run_gitsl(["grep", "-B", "1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_before_context_attached(self, sl_repo_with_commit: Path):
        """GREP-08: git grep -B1 with attached value."""
        result = run_gitsl(["grep", "-B1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_both_context_C(self, sl_repo_with_commit: Path):
        """GREP-09: git grep -C shows both context."""
        result = run_gitsl(["grep", "-C", "1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0

    def test_grep_both_context_attached(self, sl_repo_with_commit: Path):
        """GREP-09: git grep -C1 with attached value."""
        result = run_gitsl(["grep", "-C1", "Test"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


class TestGrepTranslation:
    """Tests for grep flags that require translation."""

    def test_grep_invert_match_v(self, sl_repo_with_commit: Path):
        """GREP-06: git grep -v inverts match (translates to sl -V)."""
        # Search for pattern that exists
        result_match = run_gitsl(["grep", "Test"], cwd=sl_repo_with_commit)
        assert result_match.exit_code == 0

        # Invert should find lines NOT matching
        result_invert = run_gitsl(["grep", "-v", "Test"], cwd=sl_repo_with_commit)
        # Could be exit 0 if other lines exist, or exit 1 if all lines match
        # Key is that it doesn't error out (wrong flag would error)
        assert result_invert.exit_code in (0, 1)

    def test_grep_invert_match_long(self, sl_repo_with_commit: Path):
        """GREP-06: git grep --invert-match inverts match."""
        result = run_gitsl(["grep", "--invert-match", "NonExistent"], cwd=sl_repo_with_commit)
        # Should return matching (inverted from no-match) lines
        assert result.exit_code == 0


class TestGrepUnsupported:
    """Tests for grep flags that are unsupported (warn and skip)."""

    def test_grep_count_c_warning(self, sl_repo_with_commit: Path):
        """GREP-04: git grep -c warns about unsupported flag."""
        result = run_gitsl(["grep", "-c", "Test"], cwd=sl_repo_with_commit)
        # Should warn but still run (without the flag)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_count_long_warning(self, sl_repo_with_commit: Path):
        """GREP-04: git grep --count warns about unsupported flag."""
        result = run_gitsl(["grep", "--count", "Test"], cwd=sl_repo_with_commit)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_suppress_filename_h_warning(self, sl_repo_with_commit: Path):
        """GREP-10: git grep -h warns (sl -h shows help instead)."""
        result = run_gitsl(["grep", "-h", "Test"], cwd=sl_repo_with_commit)
        # Should warn but still run
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_force_filename_H_noop(self, sl_repo_with_commit: Path):
        """GREP-11: git grep -H is no-op (already default)."""
        result = run_gitsl(["grep", "-H", "Test"], cwd=sl_repo_with_commit)
        # Should work without error (flag silently ignored)
        assert result.exit_code == 0

    def test_grep_only_matching_o_warning(self, sl_repo_with_commit: Path):
        """GREP-12: git grep -o warns about unsupported flag."""
        result = run_gitsl(["grep", "-o", "Test"], cwd=sl_repo_with_commit)
        # Should warn
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_only_matching_long_warning(self, sl_repo_with_commit: Path):
        """GREP-12: git grep --only-matching warns about unsupported flag."""
        result = run_gitsl(["grep", "--only-matching", "Test"], cwd=sl_repo_with_commit)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_quiet_q_warning(self, sl_repo_with_commit: Path):
        """GREP-13: git grep -q warns about unsupported quiet mode."""
        result = run_gitsl(["grep", "-q", "Test"], cwd=sl_repo_with_commit)
        # Should warn - sl grep doesn't support quiet mode
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_grep_quiet_long_warning(self, sl_repo_with_commit: Path):
        """GREP-13: git grep --quiet warns about unsupported quiet mode."""
        result = run_gitsl(["grep", "--quiet", "Test"], cwd=sl_repo_with_commit)
        assert "not supported" in result.stderr.lower() or "warning" in result.stderr.lower()
