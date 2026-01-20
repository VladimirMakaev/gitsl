#!/usr/bin/env python3
"""
gitsl - Git to Sapling CLI shim.

Translates git commands to their Sapling (sl) equivalents.
Set GITSL_DEBUG=1 to see what would be executed without running.
"""

import shlex
import sys
from typing import List

from common import parse_argv, is_debug_mode, print_debug_info, VERSION
import cmd_status
import cmd_log
import cmd_diff
import cmd_init
import cmd_rev_parse
import cmd_add
import cmd_commit
import cmd_show
import cmd_blame
import cmd_rm
import cmd_mv
import cmd_clone
import cmd_grep
import cmd_clean
import cmd_config
import cmd_switch
import cmd_branch
import cmd_restore


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

    # Dispatch to command handlers
    if parsed.command == "status":
        return cmd_status.handle(parsed)

    if parsed.command == "log":
        return cmd_log.handle(parsed)

    if parsed.command == "diff":
        return cmd_diff.handle(parsed)

    if parsed.command == "init":
        return cmd_init.handle(parsed)

    if parsed.command == "rev-parse":
        return cmd_rev_parse.handle(parsed)

    if parsed.command == "add":
        return cmd_add.handle(parsed)

    if parsed.command == "commit":
        return cmd_commit.handle(parsed)

    if parsed.command == "show":
        return cmd_show.handle(parsed)

    if parsed.command == "blame":
        return cmd_blame.handle(parsed)

    if parsed.command == "rm":
        return cmd_rm.handle(parsed)

    if parsed.command == "mv":
        return cmd_mv.handle(parsed)

    if parsed.command == "clone":
        return cmd_clone.handle(parsed)

    if parsed.command == "grep":
        return cmd_grep.handle(parsed)

    if parsed.command == "clean":
        return cmd_clean.handle(parsed)

    if parsed.command == "config":
        return cmd_config.handle(parsed)

    if parsed.command == "switch":
        return cmd_switch.handle(parsed)

    if parsed.command == "branch":
        return cmd_branch.handle(parsed)

    if parsed.command == "restore":
        return cmd_restore.handle(parsed)

    # Unsupported command handling (UNSUP-01, UNSUP-02)
    if parsed.args:
        original_command = f"git {parsed.command} {shlex.join(parsed.args)}"
    else:
        original_command = f"git {parsed.command}"

    print(f"gitsl: unsupported command: {original_command}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
