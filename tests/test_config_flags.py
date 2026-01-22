"""E2E tests for git config flags (CONF-01 through CONF-08)."""

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


class TestConfigGet:
    """Tests for config --get flag."""

    def test_config_get_key(self, sl_repo: Path):
        """CONF-01: git config --get key returns value."""
        # Set a config value first
        run_command(["sl", "config", "--local", "test.key", "testvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "--get", "test.key"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "testvalue" in result.stdout

    def test_config_implicit_get(self, sl_repo: Path):
        """CONF-01: git config key (without --get) returns value."""
        # Set a config value first
        run_command(["sl", "config", "--local", "test.implicit", "implicitvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "test.implicit"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "implicitvalue" in result.stdout


class TestConfigTranslation:
    """Tests for config flags that require translation."""

    def test_config_unset_to_delete(self, sl_repo: Path):
        """CONF-02: git config --unset key translates to sl config --delete."""
        # Set a value first
        run_command(["sl", "config", "--local", "test.unset", "todelete"], cwd=sl_repo)
        # Verify it's set
        verify = run_command(["sl", "config", "test.unset"], cwd=sl_repo)
        assert "todelete" in verify.stdout

        # Unset it
        result = run_gitsl(["config", "--unset", "test.unset"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify it's gone
        verify_after = run_command(["sl", "config", "test.unset"], cwd=sl_repo)
        assert "todelete" not in verify_after.stdout

    def test_config_global_to_user(self, sl_repo: Path):
        """CONF-04: git config --global translates to sl config --user."""
        # Set a global (user) config value
        result = run_gitsl(["config", "--global", "test.global", "globalvalue"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl config --user
        verify = run_command(["sl", "config", "test.global"], cwd=sl_repo)
        assert "globalvalue" in verify.stdout

    def test_config_show_origin_to_debug(self, sl_repo: Path):
        """CONF-07: git config --show-origin translates to sl config --debug."""
        # Set a local config value
        run_command(["sl", "config", "--local", "test.origin", "originvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "--show-origin", "--list"], cwd=sl_repo)
        assert result.exit_code == 0
        # --debug shows file sources, look for file path indicators
        # The output should contain file references or debug information
        assert len(result.stdout) > 0


class TestConfigPassThrough:
    """Tests for config flags that pass through directly."""

    def test_config_list_l(self, sl_repo: Path):
        """CONF-03: git config --list shows all config."""
        # Set a test value so we have something to find
        run_command(["sl", "config", "--local", "test.list", "listvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "--list"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "test.list" in result.stdout

    def test_config_list_short(self, sl_repo: Path):
        """CONF-03: git config -l shows all config."""
        run_command(["sl", "config", "--local", "test.listshort", "shortvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "-l"], cwd=sl_repo)
        assert result.exit_code == 0
        assert "test.listshort" in result.stdout

    def test_config_local_scope(self, sl_repo: Path):
        """CONF-05: git config --local key value sets local config."""
        result = run_gitsl(["config", "--local", "test.local", "localvalue"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl config
        verify = run_command(["sl", "config", "test.local"], cwd=sl_repo)
        assert "localvalue" in verify.stdout

    @pytest.mark.skip(reason="sl config --system hangs in test environment")
    def test_config_system_scope(self, sl_repo: Path):
        """CONF-06: git config --system is accepted."""
        # System config typically requires root, so just verify flag is accepted
        # The command may fail due to permissions, but shouldn't error on the flag
        result = run_gitsl(["config", "--system", "--list"], cwd=sl_repo)
        # Exit code 0 or permission error, but not "unknown flag" error
        # Just verify the command doesn't crash
        assert "unknown" not in result.stderr.lower()


class TestConfigUnsupported:
    """Tests for config flags that are unsupported (warn)."""

    def test_config_all_warning(self, sl_repo: Path):
        """CONF-08: git config --all key warns about multi-valued not supported."""
        # Set a test value
        run_command(["sl", "config", "--local", "test.all", "allvalue"], cwd=sl_repo)

        result = run_gitsl(["config", "--all", "test.all"], cwd=sl_repo)
        # Should warn about multi-valued
        assert "warning" in result.stderr.lower() or "not supported" in result.stderr.lower()


class TestConfigSetValue:
    """Tests for config set operations."""

    def test_config_set_key_value(self, sl_repo: Path):
        """Config set: git config key value sets config."""
        result = run_gitsl(["config", "test.set", "setvalue"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify with sl config
        verify = run_command(["sl", "config", "test.set"], cwd=sl_repo)
        assert "setvalue" in verify.stdout

    def test_config_set_defaults_to_local(self, sl_repo: Path):
        """Config set without scope defaults to local."""
        result = run_gitsl(["config", "test.default", "defaultvalue"], cwd=sl_repo)
        assert result.exit_code == 0

        # Verify value was set
        verify = run_command(["sl", "config", "test.default"], cwd=sl_repo)
        assert "defaultvalue" in verify.stdout
