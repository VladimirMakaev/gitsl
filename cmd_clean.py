"""Handler for 'git clean' command."""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clean' command.

    Translations:
    - git clean -f      -> sl purge (force required by gitsl)
    - git clean -fd     -> sl purge (dirs included by default)
    - git clean -n      -> sl purge --print (dry run)

    SAFETY: git requires -f or -n to run. We enforce this.
    """
    args = list(parsed.args)

    # Check for force or dry-run flags (git's safety requirement)
    has_force = '-f' in args or '--force' in args
    has_dry_run = '-n' in args or '--dry-run' in args

    if not has_force and not has_dry_run:
        print("fatal: clean.requireForce is true and -f not given: refusing to clean",
              file=sys.stderr)
        return 128

    sl_args = []

    # Handle dry-run: -n -> --print
    if has_dry_run:
        sl_args.append("--print")
        args = [a for a in args if a not in ('-n', '--dry-run')]

    # Filter out -f/--force (not needed by sl purge)
    args = [a for a in args if a not in ('-f', '--force')]

    # Filter out -d (sl purge includes untracked dirs by default)
    args = [a for a in args if a != '-d']

    return run_sl(["purge"] + sl_args + args)
