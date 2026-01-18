"""
Common utilities for gitsl.

This module contains shared data structures and functions used across
the gitsl codebase, including argument parsing, debug utilities,
and subprocess execution.
"""

import os
import shlex
import sys
from dataclasses import dataclass
from typing import List, Optional


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "0.1.0"


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class ParsedCommand:
    """Parsed representation of a git command."""
    command: Optional[str]    # e.g., "commit", "status", None if empty
    args: List[str]           # remaining arguments after command
    raw_argv: List[str]       # original argv for debugging


# ============================================================
# PARSING
# ============================================================

def parse_argv(argv: List[str]) -> ParsedCommand:
    """
    Parse git-style arguments.

    Args:
        argv: Command line arguments (without script name, i.e., sys.argv[1:])

    Returns:
        ParsedCommand with extracted command and remaining args
    """
    if not argv:
        return ParsedCommand(command=None, args=[], raw_argv=[])

    command = argv[0]
    args = argv[1:]
    return ParsedCommand(command=command, args=args, raw_argv=argv)


# ============================================================
# DEBUG MODE
# ============================================================

def is_debug_mode() -> bool:
    """Check if debug mode is enabled via GITSL_DEBUG environment variable."""
    debug_val = os.environ.get("GITSL_DEBUG", "").lower()
    return debug_val in ("1", "true", "yes", "on")


def print_debug_info(parsed: ParsedCommand) -> None:
    """Print debug information about the parsed command."""
    print(f"[DEBUG] Command: {parsed.command}", file=sys.stderr)
    print(f"[DEBUG] Args: {parsed.args}", file=sys.stderr)

    # Show what would be executed
    if parsed.command:
        would_execute = ["sl", parsed.command] + parsed.args
        print(f"[DEBUG] Would execute: {shlex.join(would_execute)}", file=sys.stderr)


# ============================================================
# SUBPROCESS EXECUTION
# ============================================================

def run_sl(args: List[str]) -> int:
    """Execute sl command with I/O passthrough. Stub for Plan 02."""
    print(f"[STUB] Would run: sl {shlex.join(args)}", file=sys.stderr)
    return 0
