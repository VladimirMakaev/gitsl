"""E2E tests for git config command (CONFIG-01, CONFIG-02, CONFIG-03)."""

import shutil
from pathlib import Path

import pytest

from conftest import run_gitsl
from helpers.commands import run_command


sl_available = shutil.which("sl") is not None
pytestmark = [
    pytest.mark.skipif(not sl_available, reason="Sapling (sl) not installed"),
    pytest.mark.config,
]


class TestConfigRead:
    """CONFIG-01: git config <key> translates to sl config <key>."""

    def test_config_read_value(self, sl_repo: Path):
        """git config reads a config value."""
        # First set a value
        run_command(["sl", "config", "--local", "ui.username", "Test <test@test.com>"],
                    cwd=sl_repo)

        result = run_gitsl(["config", "ui.username"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "Test" in result.stdout


class TestConfigWrite:
    """CONFIG-02: git config <key> <value> translates to sl config."""

    def test_config_write_value(self, sl_repo: Path):
        """git config sets a config value."""
        result = run_gitsl(["config", "test.key", "test-value"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify value was set
        verify = run_command(["sl", "config", "test.key"], cwd=sl_repo)
        assert "test-value" in verify.stdout


class TestConfigList:
    """CONFIG-03: git config --list translates to sl config."""

    def test_config_list(self, sl_repo: Path):
        """git config --list shows all config."""
        result = run_gitsl(["config", "--list"], cwd=sl_repo)
        assert result.exit_code == 0
        # Should have some output (at least system config)
        assert len(result.stdout) > 0
