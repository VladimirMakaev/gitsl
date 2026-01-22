"""Handler for 'git switch' command."""

import subprocess
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git switch' command with full flag support.

    Translations:
    - git switch <branch>              -> sl goto <bookmark>
    - git switch -c/--create <name>    -> sl bookmark <name> + sl goto <name>
    - git switch -C/--force-create     -> sl bookmark -f <name> + sl goto <name>
    - git switch -d/--detach           -> sl goto --inactive
    - git switch -f/--force/--discard-changes -> sl goto -C
    - git switch -m/--merge            -> sl goto -m
    """
    args = list(parsed.args)

    # Extract flags
    create = False
    force_create = False
    detach = False
    force = False
    merge = False
    branch_name = None
    remaining = []

    i = 0
    while i < len(args):
        arg = args[i]

        # CHKT-01: -c/--create
        if arg in ('-c', '--create'):
            create = True
            if i + 1 < len(args):
                branch_name = args[i + 1]
                i += 2
                continue
            i += 1
            continue

        # CHKT-02: -C/--force-create
        if arg in ('-C', '--force-create'):
            force_create = True
            if i + 1 < len(args):
                branch_name = args[i + 1]
                i += 2
                continue
            i += 1
            continue

        # CHKT-07: -d/--detach
        if arg in ('-d', '--detach'):
            detach = True
            i += 1
            continue

        # CHKT-08: -f/--force/--discard-changes
        if arg in ('-f', '--force', '--discard-changes'):
            force = True
            i += 1
            continue

        # CHKT-09: -m/--merge
        if arg in ('-m', '--merge'):
            merge = True
            i += 1
            continue

        remaining.append(arg)
        i += 1

    # Handle create modes
    if create and branch_name:
        result = run_sl(['bookmark', branch_name])
        if result != 0:
            return result
        return run_sl(['goto', branch_name])

    if force_create and branch_name:
        # Use -f to force update if bookmark exists
        result = run_sl(['bookmark', '-f', branch_name])
        if result != 0:
            return result
        return run_sl(['goto', branch_name])

    # Build goto command for regular switch
    goto_args = ['goto']

    if force:
        goto_args.append('-C')  # Clean/discard changes
    if merge:
        goto_args.append('-m')
    if detach:
        goto_args.append('--inactive')

    goto_args.extend(remaining)
    return run_sl(goto_args)
