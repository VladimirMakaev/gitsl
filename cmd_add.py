"""Handler for 'git add' command."""

import subprocess
from typing import List

from common import ParsedCommand, run_sl


def get_deleted_files(pathspec: List[str] = None) -> List[str]:
    """
    Get list of deleted tracked files.

    Args:
        pathspec: Optional list of paths to filter

    Returns:
        List of filenames that are deleted (missing from disk but tracked)
    """
    cmd = ["sl", "status", "-d", "-n"]  # -d=deleted, -n=no-status-prefix
    if pathspec:
        cmd.extend(pathspec)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    return [f for f in result.stdout.splitlines() if f.strip()]


def handle_update(parsed: ParsedCommand) -> int:
    """
    Handle 'git add -u' (update) command.

    Stages only tracked files:
    - Modified files: No action (Sapling auto-stages)
    - Deleted files: Mark for removal with sl remove --mark

    Does NOT add untracked files.
    """
    # Extract pathspec (remaining args after -u/--update)
    pathspec = [a for a in parsed.args if a not in ("-u", "--update")]

    # Find deleted tracked files
    deleted_files = get_deleted_files(pathspec if pathspec else None)

    # Mark deleted files for removal
    if deleted_files:
        result = subprocess.run(["sl", "remove", "--mark"] + deleted_files)
        return result.returncode

    return 0


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git add' command.

    Translations:
    - git add <files>  -> sl add <files>
    - git add -A       -> sl addremove
    - git add --all    -> sl addremove
    - git add -u       -> mark deleted for removal (modified auto-staged)
    - git add --update -> mark deleted for removal (modified auto-staged)
    """
    # Check for -u or --update flag -> handle update mode
    if "-u" in parsed.args or "--update" in parsed.args:
        return handle_update(parsed)

    # Check for -A or --all flag -> translate to addremove
    if "-A" in parsed.args or "--all" in parsed.args:
        # Filter out the -A/--all flag
        filtered_args = [a for a in parsed.args if a not in ("-A", "--all")]
        return run_sl(["addremove"] + filtered_args)

    # Standard add passthrough
    return run_sl(["add"] + parsed.args)
