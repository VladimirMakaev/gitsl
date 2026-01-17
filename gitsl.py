#!/usr/bin/env python3
"""
gitsl - Git to Sapling CLI shim.

Translates git commands to their Sapling (sl) equivalents.
Set GITSL_DEBUG=1 to see what would be executed without running.
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

    # Show what would be executed (placeholder for Phase 1)
    if parsed.command:
        would_execute = ["sl", parsed.command] + parsed.args
        print(f"[DEBUG] Would execute: {shlex.join(would_execute)}", file=sys.stderr)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main(argv: List[str] = None) -> int:
    """
    Main entry point for gitsl.

    Args:
        argv: Command line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if argv is None:
        argv = sys.argv[1:]

    parsed = parse_argv(argv)

    # Handle empty command
    if parsed.command is None:
        print("usage: git <command> [<args>]", file=sys.stderr)
        return 1

    # Handle special flags
    if parsed.command in ("--version", "-v"):
        print(f"gitsl version {VERSION}")
        return 0

    if parsed.command in ("--help", "-h", "help"):
        print("usage: git <command> [<args>]")
        print("\nThis is gitsl, a git-to-Sapling translation shim.")
        print("Set GITSL_DEBUG=1 to see commands without executing.")
        return 0

    # Debug mode: show what would run, don't execute
    if is_debug_mode():
        print_debug_info(parsed)
        return 0

    # Future phases: translate and execute command
    # For Phase 1, just acknowledge the command
    print(f"[STUB] Would process: git {parsed.command}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
