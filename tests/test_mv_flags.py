"""E2E tests for git mv flags (MV-01 through MV-04)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.mv,
]


class TestMvPassThrough:
    """Tests for mv flags that pass through directly."""

    def test_mv_force_f(self, sl_repo_with_commit: Path):
        """MV-01: git mv -f passes through to sl rename -f."""
        # Create source and target files
        src = sl_repo_with_commit / "source.txt"
        dst = sl_repo_with_commit / "dest.txt"
        src.write_text("Source content\n")
        dst.write_text("Dest content\n")
        run_command(["sl", "add", "source.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add source"], cwd=sl_repo_with_commit)

        # Move with force should overwrite dest
        result = run_gitsl(["mv", "-f", "source.txt", "dest.txt"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Source should be gone, dest should have source content
        assert not src.exists()
        assert dst.exists()
        assert dst.read_text() == "Source content\n"

    def test_mv_force_long(self, sl_repo_with_commit: Path):
        """MV-01: git mv --force passes through to sl rename -f."""
        # Create source and target files
        src = sl_repo_with_commit / "source2.txt"
        dst = sl_repo_with_commit / "dest2.txt"
        src.write_text("Source content 2\n")
        dst.write_text("Dest content 2\n")
        run_command(["sl", "add", "source2.txt"], cwd=sl_repo_with_commit)
        run_command(["sl", "commit", "-m", "Add source2"], cwd=sl_repo_with_commit)

        result = run_gitsl(["mv", "--force", "source2.txt", "dest2.txt"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not src.exists()
        assert dst.exists()

    def test_mv_verbose_v(self, sl_repo_with_commit: Path):
        """MV-03: git mv -v passes through for verbose output."""
        result = run_gitsl(["mv", "-v", "README.md", "README_moved.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not (sl_repo_with_commit / "README.md").exists()
        assert (sl_repo_with_commit / "README_moved.md").exists()

    def test_mv_verbose_long(self, sl_repo_with_commit: Path):
        """MV-03: git mv --verbose passes through for verbose output."""
        result = run_gitsl(["mv", "--verbose", "README.md", "README_v.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        assert not (sl_repo_with_commit / "README.md").exists()
        assert (sl_repo_with_commit / "README_v.md").exists()

    def test_mv_dry_run_n(self, sl_repo_with_commit: Path):
        """MV-04: git mv -n passes through for dry-run."""
        result = run_gitsl(["mv", "-n", "README.md", "README_dry.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # With dry-run, file should not be moved
        assert (sl_repo_with_commit / "README.md").exists()
        assert not (sl_repo_with_commit / "README_dry.md").exists()

    def test_mv_dry_run_long(self, sl_repo_with_commit: Path):
        """MV-04: git mv --dry-run passes through for dry-run."""
        result = run_gitsl(["mv", "--dry-run", "README.md", "README_drylong.md"], cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # With dry-run, file should not be moved
        assert (sl_repo_with_commit / "README.md").exists()
        assert not (sl_repo_with_commit / "README_drylong.md").exists()


class TestMvUnsupported:
    """Tests for mv flags that are unsupported (warn)."""

    def test_mv_k_warning(self, sl_repo_with_commit: Path):
        """MV-02: git mv -k warns about skip errors not supported."""
        result = run_gitsl(["mv", "-k", "README.md", "README_k.md"], cwd=sl_repo_with_commit)
        # Should warn about -k not supported
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()
        # Move should still succeed (flag is ignored after warning)
        assert not (sl_repo_with_commit / "README.md").exists()
        assert (sl_repo_with_commit / "README_k.md").exists()
