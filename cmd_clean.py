"""Handler for 'git clean' command."""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clean' command.

    Translations:
    - git clean -f      -> sl purge (force required by gitsl)
    - git clean -fd     -> sl purge --files --dirs (remove files and empty dirs)
    - git clean -n      -> sl purge --print (dry run)

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

    # Process args: filter out git-specific flags, handle combined flags
    filtered_args = []
    for arg in args:
        if arg.startswith('-') and not arg.startswith('--'):
            # Short flag(s) - remove f, d, n from combined flags
            remaining = arg.replace('f', '').replace('d', '').replace('n', '')
            if remaining and remaining != '-':
                filtered_args.append(remaining)
        elif arg in ('--force', '--dry-run'):
            # Skip these long flags
            continue
        else:
            filtered_args.append(arg)

    return run_sl(["purge"] + sl_args + filtered_args)
