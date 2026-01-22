"""E2E tests for git clone flags (CLON-01 through CLON-09)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.clone,
]


class TestCloneTranslation:
    """Tests for clone flags that require translation."""

    def test_clone_branch_b(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-01: git clone -b translates to sl clone -u."""
        # Create a bookmark in source repo
        run_command(["sl", "bookmark", "feature"], cwd=sl_repo_with_commit)

        # Clone with -b
        target = tmp_path / "clone_target_b"
        result = run_gitsl(
            ["clone", "-b", "feature", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        # Verify target directory was created
        assert target.exists()
        # Verify files exist in the cloned repo
        assert (target / "README.md").exists()

    def test_clone_branch_long(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-01: git clone --branch=<bookmark> translates to sl clone -u."""
        # Create a bookmark in source repo
        run_command(["sl", "bookmark", "feature2"], cwd=sl_repo_with_commit)

        # Clone with --branch=
        target = tmp_path / "clone_target_branch"
        result = run_gitsl(
            ["clone", "--branch=feature2", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        assert target.exists()
        assert (target / "README.md").exists()

    def test_clone_no_checkout_n(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-05: git clone -n translates to sl clone -U (no update)."""
        target = tmp_path / "clone_no_checkout_n"
        result = run_gitsl(
            ["clone", "-n", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        # Directory should exist but working copy should be empty
        assert target.exists()
        # With -U, files are not checked out
        assert not (target / "README.md").exists()

    def test_clone_no_checkout_long(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-05: git clone --no-checkout translates to sl clone -U."""
        target = tmp_path / "clone_no_checkout_long"
        result = run_gitsl(
            ["clone", "--no-checkout", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        assert target.exists()
        # With --no-checkout, files are not checked out
        assert not (target / "README.md").exists()


class TestClonePassThrough:
    """Tests for clone flags that pass through directly."""

    def test_clone_quiet_q(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-08: git clone -q passes through for quiet output."""
        target = tmp_path / "clone_quiet"
        result = run_gitsl(
            ["clone", "-q", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        assert target.exists()
        # With quiet mode, minimal output expected
        assert (target / "README.md").exists()

    def test_clone_verbose_v(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-09: git clone -v passes through for verbose output."""
        target = tmp_path / "clone_verbose"
        result = run_gitsl(
            ["clone", "-v", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        assert result.exit_code == 0
        assert target.exists()
        assert (target / "README.md").exists()


class TestCloneUnsupported:
    """Tests for clone flags that are unsupported (warn and skip)."""

    def test_clone_depth_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-02: git clone --depth warns about no effect in Sapling."""
        target = tmp_path / "clone_depth"
        result = run_gitsl(
            ["clone", "--depth", "1", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "no effect" in result.stderr.lower()
        assert target.exists()

    def test_clone_depth_equals_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-02: git clone --depth=1 warns about no effect in Sapling."""
        target = tmp_path / "clone_depth_eq"
        result = run_gitsl(
            ["clone", "--depth=1", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "no effect" in result.stderr.lower()
        assert target.exists()

    def test_clone_single_branch_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-03: git clone --single-branch warns about not applicable."""
        target = tmp_path / "clone_single"
        result = run_gitsl(
            ["clone", "--single-branch", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "not applicable" in result.stderr.lower()
        assert target.exists()

    def test_clone_origin_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-04: git clone -o custom warns about unsupported remote name."""
        target = tmp_path / "clone_origin"
        result = run_gitsl(
            ["clone", "-o", "upstream", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()
        assert target.exists()

    def test_clone_origin_long_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-04: git clone --origin=custom warns about unsupported remote name."""
        target = tmp_path / "clone_origin_long"
        result = run_gitsl(
            ["clone", "--origin=upstream", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()
        assert target.exists()

    def test_clone_recursive_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-06: git clone --recursive warns about submodules not supported."""
        target = tmp_path / "clone_recursive"
        result = run_gitsl(
            ["clone", "--recursive", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "submodule" in result.stderr.lower()
        assert target.exists()

    def test_clone_recurse_submodules_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-06: git clone --recurse-submodules warns about submodules not supported."""
        target = tmp_path / "clone_recurse_sub"
        result = run_gitsl(
            ["clone", "--recurse-submodules", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "submodule" in result.stderr.lower()
        assert target.exists()

    def test_clone_no_tags_warning(self, sl_repo_with_commit: Path, tmp_path: Path):
        """CLON-07: git clone --no-tags warns about not applicable."""
        target = tmp_path / "clone_no_tags"
        result = run_gitsl(
            ["clone", "--no-tags", str(sl_repo_with_commit), str(target)],
            cwd=tmp_path,
        )
        # Should warn but still clone
        assert "warning" in result.stderr.lower() or "not applicable" in result.stderr.lower()
        assert target.exists()
