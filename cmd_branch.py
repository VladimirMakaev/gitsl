"""Handler for 'git branch' command.

Supported flags:
- SAFE-04: -D -> -d (prevent destructive strip)
- BRAN-01: -m/--move -> -m (rename bookmark)
- BRAN-02: -a/--all -> --all (show all including remote)
- BRAN-03: -r/--remotes -> --remote (show remote only)
- BRAN-04: -v/--verbose -> template with commit info
- BRAN-05: -l/--list -> filter bookmarks by pattern
- BRAN-06: --show-current -> template query for active bookmark
- BRAN-07: -t/--track -> -t (pass through)
- BRAN-08: -f/--force -> -f (pass through)
- BRAN-09: -c/--copy -> custom two-step implementation
"""

import fnmatch
import subprocess
import sys
from common import ParsedCommand, run_sl


def show_current_branch() -> int:
    """BRAN-06: Show current branch name only."""
    result = subprocess.run(
        ['sl', 'log', '-r', '.', '--template', '{activebookmark}'],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    # No output if detached (matches git behavior)
    return 0


def copy_branch(source: str, dest: str) -> int:
    """BRAN-09: Copy a branch (create new bookmark at same commit)."""
    # Get commit where source bookmark points
    result = subprocess.run(
        ['sl', 'log', '-r', f'bookmark({source})', '--template', '{node}'],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        sys.stderr.write(f"error: branch '{source}' not found\n")
        return 1

    commit = result.stdout.strip()

    # Create new bookmark at that commit
    return run_sl(['bookmark', dest, '-r', commit])


def list_bookmarks_verbose() -> int:
    """BRAN-04: Show bookmarks with commit info."""
    result = subprocess.run(
        ['sl', 'bookmark', '--template', '{bookmark}: {node|short} {desc|firstline}\n'],
        capture_output=True, text=True
    )
    sys.stdout.write(result.stdout)
    return result.returncode


def list_bookmarks_with_pattern(pattern: str) -> int:
    """BRAN-05: List bookmarks matching a glob pattern."""
    result = subprocess.run(
        ['sl', 'bookmark', '--template', '{bookmark}\n'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return result.returncode

    for line in result.stdout.strip().split('\n'):
        bookmark = line.strip()
        if bookmark and fnmatch.fnmatch(bookmark, pattern):
            print(bookmark)
    return 0


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git branch' command.

    Translations:
    - git branch              -> sl bookmark (list)
    - git branch <name>       -> sl bookmark <name> (create)
    - git branch -d <name>    -> sl bookmark -d <name> (delete)
    - git branch -D <name>    -> sl bookmark -d <name> (safe delete)
    - git branch -m old new   -> sl bookmark -m old new (rename)
    - git branch -a           -> sl bookmark --all (list all)
    - git branch -r           -> sl bookmark --remote (list remote)
    - git branch -v           -> sl bookmark with template (verbose)
    - git branch -l pattern   -> filter bookmarks by pattern
    - git branch --show-current -> show active bookmark
    - git branch -c old new   -> copy bookmark (two-step)

    SAFETY: git branch -D just removes the label. sl bookmark -D strips
    commits. We ALWAYS use -d to preserve commits.
    """
    args = list(parsed.args)
    sl_args = ['bookmark']
    remaining_args = []

    # Flags to track
    show_current = False
    verbose = False
    list_pattern = None
    copy_mode = False
    copy_args = []
    rename_mode = False
    rename_args = []
    show_all = False
    show_remote = False

    i = 0
    while i < len(args):
        arg = args[i]

        # BRAN-06: --show-current
        if arg == '--show-current':
            show_current = True
            i += 1
            continue

        # BRAN-04: -v/--verbose
        if arg in ('-v', '--verbose', '-vv'):
            verbose = True
            i += 1
            continue

        # BRAN-02: -a/--all
        if arg in ('-a', '--all'):
            show_all = True
            i += 1
            continue

        # BRAN-03: -r/--remotes
        if arg in ('-r', '--remotes'):
            show_remote = True
            i += 1
            continue

        # BRAN-05: -l/--list with optional pattern
        if arg in ('-l', '--list'):
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                list_pattern = args[i + 1]
                i += 2
            else:
                # Just list all (default behavior)
                i += 1
            continue

        # BRAN-09: -c/--copy
        if arg in ('-c', '--copy'):
            copy_mode = True
            # Collect next two args as source and dest
            if i + 2 < len(args):
                copy_args = [args[i + 1], args[i + 2]]
                i += 3
            else:
                sys.stderr.write("error: -c requires source and destination\n")
                return 1
            continue

        # BRAN-01: -m/--move (rename)
        if arg in ('-m', '--move'):
            rename_mode = True
            # Collect next two args as old and new
            if i + 2 < len(args):
                rename_args = [args[i + 1], args[i + 2]]
                i += 3
            else:
                sys.stderr.write("error: -m requires old and new name\n")
                return 1
            continue

        # SAFE-04: Translate -D to -d to avoid destroying commits
        if arg == '-D':
            remaining_args.append('-d')
            i += 1
            continue

        # BRAN-07: -t/--track (pass through)
        if arg in ('-t', '--track'):
            remaining_args.append('-t')
            i += 1
            continue

        # BRAN-08: -f/--force (pass through)
        if arg in ('-f', '--force'):
            remaining_args.append('-f')
            i += 1
            continue

        # Pass through other args
        remaining_args.append(arg)
        i += 1

    # Handle special modes
    if show_current:
        return show_current_branch()

    if verbose:
        return list_bookmarks_verbose()

    if list_pattern:
        return list_bookmarks_with_pattern(list_pattern)

    if copy_mode and len(copy_args) == 2:
        return copy_branch(copy_args[0], copy_args[1])

    if rename_mode and len(rename_args) == 2:
        return run_sl(['bookmark', '-m', rename_args[0], rename_args[1]])

    # Build sl command for remaining cases
    if show_all:
        sl_args.append('--all')
    if show_remote:
        sl_args.append('--remote')

    sl_args.extend(remaining_args)

    return run_sl(sl_args)
