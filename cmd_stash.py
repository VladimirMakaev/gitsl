"""Handler for 'git stash' command."""

import subprocess
import sys
from typing import Optional
from common import ParsedCommand, run_sl


def _get_most_recent_shelve() -> Optional[str]:
    """Get the name of the most recent shelve, or None if no shelves exist."""
    result = subprocess.run(
        ["sl", "shelve", "--list"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    # Output format: "name    (age)    message"
    first_line = result.stdout.strip().split('\n')[0]
    # Name is first whitespace-separated token
    shelve_name = first_line.split()[0]
    return shelve_name


def _handle_push(args: list) -> int:
    """Handle git stash push -> sl shelve."""
    return run_sl(["shelve"] + args)


def _handle_pop(args: list) -> int:
    """Handle git stash pop -> sl unshelve."""
    return run_sl(["unshelve"] + args)


def _handle_apply(args: list) -> int:
    """Handle git stash apply -> sl unshelve --keep."""
    return run_sl(["unshelve", "--keep"] + args)


def _handle_list(args: list) -> int:
    """Handle git stash list -> sl shelve --list."""
    return run_sl(["shelve", "--list"] + args)


def _handle_drop(args: list) -> int:
    """
    Handle git stash drop -> sl shelve --delete.

    git stash drop without args deletes most recent.
    sl shelve --delete requires a name.
    """
    if args:
        # Specific stash reference provided
        # For v1.2, pass through - sl may error if format wrong
        return run_sl(["shelve", "--delete"] + args)

    # No args: delete most recent
    shelve_name = _get_most_recent_shelve()
    if shelve_name is None:
        print("No stash entries found.", file=sys.stderr)
        return 1

    return run_sl(["shelve", "--delete", shelve_name])


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git stash' command.

    Translations:
    - git stash           -> sl shelve
    - git stash push      -> sl shelve
    - git stash -m "msg"  -> sl shelve -m "msg"
    - git stash pop       -> sl unshelve
    - git stash apply     -> sl unshelve --keep
    - git stash list      -> sl shelve --list
    - git stash drop      -> sl shelve --delete <most-recent>
    """
    args = list(parsed.args)

    # No subcommand = stash (same as push)
    if not args:
        return run_sl(["shelve"])

    subcommand = args[0]
    subargs = args[1:]

    if subcommand == "push":
        return _handle_push(subargs)

    if subcommand == "pop":
        return _handle_pop(subargs)

    if subcommand == "apply":
        return _handle_apply(subargs)

    if subcommand == "list":
        return _handle_list(subargs)

    if subcommand == "drop":
        return _handle_drop(subargs)

    # Check if first arg is a flag (e.g., -m) - treat as push
    if subcommand.startswith("-"):
        return _handle_push(args)

    # Unknown subcommand - pass through to shelve
    return run_sl(["shelve"] + args)
