"""
Command execution helpers for E2E testing.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class CommandResult:
    """Result of running a command via subprocess."""

    stdout: str
    stderr: str
    exit_code: int

    @property
    def success(self) -> bool:
        """Return True if command exited with code 0."""
        return self.exit_code == 0


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> CommandResult:
    """
    Run a command and capture all output.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory (default: current)
        env: Environment variables to merge with current env (default: inherit)

    Returns:
        CommandResult with stdout, stderr, exit_code
    """
    # Merge with current environment if custom env provided
    full_env = None
    if env is not None:
        full_env = os.environ.copy()
        full_env.update(env)

    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=full_env,
        capture_output=True,
        text=True,
    )
    return CommandResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )
