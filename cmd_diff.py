"""Handler for 'git diff' command.

Supported flags:
- DIFF-01: --stat -> --stat (diffstat summary)
- DIFF-02: -w/--ignore-all-space -> -w (ignore all whitespace)
- DIFF-03: -b/--ignore-space-change -> -b (ignore space changes)
- DIFF-04: -U<n>/--unified=<n> -> -U <n> (context lines)
- DIFF-05: --name-only -> sl status -mard (file names only)
- DIFF-06: --name-status -> sl status -mard (file names with status)
- DIFF-07: --staged/--cached -> warning (no staging area)
- DIFF-08: --raw -> warning (format not supported)
- DIFF-09: -M/--find-renames -> warning (not supported)
- DIFF-10: -C/--find-copies -> warning (not supported)
- DIFF-11: --word-diff -> warning (not supported)
- DIFF-12: --color-moved -> warning (not supported)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git diff' command.

    Translations:
    - git diff --stat -> sl diff --stat
    - git diff -w -> sl diff -w
    - git diff -b -> sl diff -b
    - git diff -U<n> -> sl diff -U <n>
    - git diff --name-only -> sl status -mard (working dir) or pass-through (commits)
    - git diff --name-status -> sl status -mard (working dir) or pass-through (commits)
    - git diff --staged/--cached -> warning + sl diff
    - git diff --raw -> warning
    - git diff -M/-C -> warning
    - git diff --word-diff -> warning
    - git diff --color-moved -> warning

    All other arguments pass through unchanged.
    """
    sl_args = ["diff"]
    remaining_args = []
    name_only = False
    name_status = False
    has_commits = False

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # DIFF-01: --stat passes through
        if arg == '--stat':
            sl_args.append('--stat')

        # DIFF-02: -w/--ignore-all-space passes through
        elif arg in ('-w', '--ignore-all-space'):
            sl_args.append('-w')

        # DIFF-03: -b/--ignore-space-change passes through
        elif arg in ('-b', '--ignore-space-change'):
            sl_args.append('-b')

        # DIFF-04: -U<n>/--unified=<n> with value parsing
        elif arg.startswith('-U') and len(arg) > 2 and arg[2:].isdigit():
            # Attached value: -U5
            sl_args.extend(['-U', arg[2:]])
        elif arg == '-U':
            # Separate value: -U 5
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-U', parsed.args[i]])
        elif arg.startswith('--unified='):
            # Equals format: --unified=5
            sl_args.extend(['-U', arg.split('=', 1)[1]])

        # DIFF-05: --name-only - use sl status for working directory
        elif arg == '--name-only':
            name_only = True

        # DIFF-06: --name-status - use sl status for working directory
        elif arg == '--name-status':
            name_status = True

        # DIFF-07: --staged/--cached - warn about no staging area
        elif arg in ('--staged', '--cached'):
            print("Warning: Sapling has no staging area. "
                  "Use 'sl diff' to see all uncommitted changes.",
                  file=sys.stderr)
            # Skip this flag - don't add to sl_args

        # DIFF-08: --raw - warn about unsupported format
        elif arg == '--raw':
            print("Warning: --raw format not supported. "
                  "Use 'sl status' for file status information.",
                  file=sys.stderr)
            # Skip this flag

        # DIFF-09: -M/--find-renames - warn about unsupported feature
        elif arg == '--find-renames' or arg == '-M' or (
                arg.startswith('-M') and len(arg) > 2 and arg[2:].isdigit()):
            print("Warning: Sapling doesn't support automatic rename detection (-M). "
                  "Use 'sl mv' to track renames before committing.",
                  file=sys.stderr)
            # Skip this flag

        # DIFF-10: -C/--find-copies - warn about unsupported feature
        elif arg == '--find-copies' or arg == '-C' or (
                arg.startswith('-C') and len(arg) > 2 and arg[2:].isdigit()):
            print("Warning: Sapling doesn't support automatic copy detection (-C). "
                  "Use 'sl copy' to track copies before committing.",
                  file=sys.stderr)
            # Skip this flag

        # DIFF-11: --word-diff - warn about unsupported feature
        elif arg.startswith('--word-diff'):
            print("Warning: Sapling doesn't support word-level diff (--word-diff). "
                  "Consider using external tools like 'diff-so-fancy' or 'delta'.",
                  file=sys.stderr)
            # Skip this flag

        # DIFF-12: --color-moved - warn about unsupported feature
        elif arg.startswith('--color-moved'):
            print("Warning: Sapling doesn't support --color-moved highlighting.",
                  file=sys.stderr)
            # Skip this flag

        # Everything else passes through
        else:
            remaining_args.append(arg)
            # Check if this looks like a commit ref (for name-only/name-status)
            # Commit refs don't start with - and aren't file paths
            if not arg.startswith('-') and not arg.startswith('.'):
                has_commits = True

        i += 1

    # Handle --name-only and --name-status
    # For working directory diff, use sl status
    # For commit diff, note limitation and pass through
    if name_only or name_status:
        if has_commits:
            # For commit diff, sl diff doesn't support --name-only directly
            # Pass through and accept different output format
            print("Note: --name-only/--name-status for commit diff may differ from git.",
                  file=sys.stderr)
            sl_args.extend(remaining_args)
            return run_sl(sl_args)
        else:
            # For working directory diff, use sl status -mard
            # This shows modified, added, removed, deleted files
            status_args = ["status", "-mard"]
            if name_only:
                # --name-only: just show file names
                status_args.append("--no-status")
            # For --name-status, sl status already shows status codes (M, A, R, !)
            # The output format is close enough to git's
            return run_sl(status_args)

    sl_args.extend(remaining_args)
    return run_sl(sl_args)
