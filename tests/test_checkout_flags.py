"""
E2E tests for git checkout flags (CHKT-05, CHKT-06).

Tests:
- CHKT-05: --detach passes through
- CHKT-06: -t/--track is accepted with note
"""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.checkout_flags,
]


# ============================================================
# CHKT-05: --detach
# ============================================================


class TestCheckoutDetach:
    """CHKT-05: checkout --detach switches to commit without branch."""

    def test_checkout_detach(self, sl_repo_with_commit: Path):
        """git checkout --detach <commit> switches without active bookmark."""
        # Get commit hash
        log = run_command(["sl", "log", "-l", "1", "--template", "{node|short}"],
                         cwd=sl_repo_with_commit)
        commit = log.stdout.strip()

        result = run_gitsl(["checkout", "--detach", commit], cwd=sl_repo_with_commit)
        assert result.exit_code == 0


# ============================================================
# CHKT-06: -t/--track
# ============================================================


class TestCheckoutTrack:
    """CHKT-06: checkout -t/--track is accepted with note."""

    def test_checkout_track_accepted(self, sl_repo_with_commit: Path):
        """git checkout -t -b <name> is accepted."""
        result = run_gitsl(["checkout", "-t", "-b", "tracked-branch"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0

        # Branch should be created
        bookmarks = run_command(["sl", "bookmark"], cwd=sl_repo_with_commit)
        assert "tracked-branch" in bookmarks.stdout

    def test_checkout_track_note(self, sl_repo_with_commit: Path):
        """git checkout --track prints note about limited emulation."""
        result = run_gitsl(["checkout", "--track", "-b", "another-tracked"],
                          cwd=sl_repo_with_commit)
        assert result.exit_code == 0
        # Should print note about tracking
        assert "track" in result.stderr.lower()
