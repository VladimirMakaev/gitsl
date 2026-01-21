"""Handler for 'git add' command.

Supported flags:
- ADD-01: -A/--all -> sl addremove (existing)
- ADD-02: -u/--update -> mark deleted for removal (existing)
- ADD-03: -n/--dry-run -> preview mode
- ADD-04: -f/--force -> warning (Sapling limitation)
- ADD-05: -v/--verbose -> show files being added
"""

import subprocess
import sys
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


def handle_update_with_flags(pathspec: List[str], dry_run: bool, verbose: bool) -> int:
    """
    Handle git add -u with optional dry-run and verbose.

    Stages only tracked files:
    - Modified files: No action (Sapling auto-stages)
    - Deleted files: Mark for removal with sl remove --mark

    Does NOT add untracked files.
    """
    deleted_files = get_deleted_files(pathspec if pathspec else None)

    if not deleted_files:
        if verbose:
            print("No deleted files to mark for removal.")
        return 0

    if dry_run:
        for f in deleted_files:
            print(f"remove '{f}'")
        return 0

    result = subprocess.run(
        ["sl", "remove", "--mark"] + deleted_files,
        capture_output=verbose,
        text=True
    )
    if verbose and result.returncode == 0:
        for f in deleted_files:
            print(f"remove '{f}'")
    return result.returncode


def handle_all_with_flags(remaining: List[str], dry_run: bool, verbose: bool) -> int:
    """Handle git add -A with optional dry-run and verbose."""
    cmd = ["addremove"] + remaining
    if dry_run:
        cmd.append("-n")

    if verbose or dry_run:
        result = subprocess.run(["sl"] + cmd, capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                if line:
                    # Format: adding/removing filename
                    print(line)
        return result.returncode

    return run_sl(cmd)


def handle_add_with_flags(remaining: List[str], dry_run: bool, verbose: bool) -> int:
    """Handle standard git add with optional dry-run and verbose."""
    cmd = ["add"] + remaining
    if dry_run:
        cmd.append("-n")

    if verbose or dry_run:
        result = subprocess.run(["sl"] + cmd, capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                if line:
                    print(f"add '{line}'")
        return result.returncode

    return run_sl(cmd)


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git add' command.

    Translations:
    - git add <files>  -> sl add <files>
    - git add -A       -> sl addremove
    - git add --all    -> sl addremove
    - git add -u       -> mark deleted for removal (modified auto-staged)
    - git add --update -> mark deleted for removal (modified auto-staged)
    - git add -n       -> sl add -n (dry-run preview)
    - git add -f       -> warning (Sapling limitation)
    - git add -v       -> show files being added
    """
    # Extract flags
    dry_run = '-n' in parsed.args or '--dry-run' in parsed.args
    force = '-f' in parsed.args or '--force' in parsed.args
    verbose = '-v' in parsed.args or '--verbose' in parsed.args
    use_update = '-u' in parsed.args or '--update' in parsed.args
    use_all = '-A' in parsed.args or '--all' in parsed.args

    # Filter out processed flags
    remaining = [a for a in parsed.args
                 if a not in ('-n', '--dry-run', '-f', '--force', '-v', '--verbose',
                              '-u', '--update', '-A', '--all')]

    # ADD-04: Warn about --force
    if force:
        print("Warning: -f/--force not directly supported. "
              "Sapling cannot force-add ignored files. "
              "Consider updating your .gitignore instead.",
              file=sys.stderr)

    # Handle -u/--update mode
    if use_update:
        return handle_update_with_flags(remaining, dry_run, verbose)

    # Handle -A/--all mode
    if use_all:
        return handle_all_with_flags(remaining, dry_run, verbose)

    # Standard add with new flags
    return handle_add_with_flags(remaining, dry_run, verbose)
