"""Handler for 'git clean' command.

Supported flags:
- CLEN-01: -x -> --ignored (remove ignored files too)
- CLEN-02: -X -> warning + --ignored (only ignored files not directly supported)
- CLEN-03: -e <pattern> -> -X <pattern> (exclude pattern)
- CLEN-04: -f, -d, -n -> existing handling (force, directories, dry-run)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clean' command.

    Translations:
    - git clean -f      -> sl purge (force required by gitsl)
    - git clean -fd     -> sl purge --files --dirs (remove files and empty dirs)
    - git clean -n      -> sl purge --print (dry run)
    - git clean -x      -> sl purge --ignored (remove ignored files too)
    - git clean -e pat  -> sl purge -X pat (exclude pattern)

    Warnings:
    - git clean -X      -> warning (only ignored files not directly supported)

    SAFETY: git requires -f or -n to run. We enforce this.
    """
    args = list(parsed.args)

    # Check for force or dry-run flags (git's safety requirement)
    # Handle both standalone flags and combined short flags (e.g., -fd, -fn)
    has_force = any('f' in a for a in args if a.startswith('-') and not a.startswith('--'))
    has_force = has_force or '--force' in args
    has_dry_run = any('n' in a for a in args if a.startswith('-') and not a.startswith('--'))
    has_dry_run = has_dry_run or '--dry-run' in args
    has_dirs = any('d' in a for a in args if a.startswith('-') and not a.startswith('--'))
    has_ignored = any('x' in a for a in args if a.startswith('-') and not a.startswith('--'))
    has_only_ignored = any('X' in a for a in args if a.startswith('-') and not a.startswith('--'))

    if not has_force and not has_dry_run:
        print("fatal: clean.requireForce is true and -f not given: refusing to clean",
              file=sys.stderr)
        return 128

    sl_args = []

    # Handle dry-run: -n -> --print
    if has_dry_run:
        sl_args.append("--print")

    # Handle directories: -d -> --files --dirs (to delete files AND empty dirs)
    if has_dirs:
        sl_args.extend(["--files", "--dirs"])

    # CLEN-01: -x -> --ignored (remove ignored files too)
    if has_ignored:
        sl_args.append("--ignored")

    # CLEN-02: -X -> warning (only ignored files not directly supported)
    if has_only_ignored:
        print("Warning: -X (only ignored files) not directly supported. "
              "Using --ignored which removes untracked and ignored files.", file=sys.stderr)
        if "--ignored" not in sl_args:
            sl_args.append("--ignored")

    # Process args: filter out git-specific flags, handle -e pattern
    filtered_args = []
    i = 0
    while i < len(args):
        arg = args[i]

        # CLEN-03: -e <pattern> -> -X <pattern> (exclude pattern)
        if arg == '-e':
            if i + 1 < len(args):
                i += 1
                sl_args.extend(['-X', args[i]])
        elif arg.startswith('-e') and len(arg) > 2:
            # Handle -epattern format
            sl_args.extend(['-X', arg[2:]])
        elif arg.startswith('-') and not arg.startswith('--'):
            # Short flag(s) - remove f, d, n, x, X from combined flags
            remaining = arg.replace('f', '').replace('d', '').replace('n', '').replace('x', '').replace('X', '')
            if remaining and remaining != '-':
                filtered_args.append(remaining)
        elif arg in ('--force', '--dry-run'):
            # Skip these long flags
            pass
        else:
            filtered_args.append(arg)

        i += 1

    return run_sl(["purge"] + sl_args + filtered_args)
