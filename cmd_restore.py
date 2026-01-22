"""Handler for 'git restore' command."""

import subprocess
import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git restore' command with full flag support.

    Translations:
    - git restore <file>           -> sl revert <file>
    - git restore -s/--source=REV  -> sl revert -r REV
    - git restore --staged/-S      -> warning (no staging area)
    - git restore -q/--quiet       -> suppress output
    - git restore -W/--worktree    -> default behavior (skip flag)
    """
    args = list(parsed.args)

    # Extract flags
    source = None
    staged = False
    quiet = False
    remaining = []

    i = 0
    while i < len(args):
        arg = args[i]

        # CHKT-03: -s/--source
        if arg in ('-s', '--source'):
            if i + 1 < len(args):
                source = args[i + 1]
                i += 2
                continue
        elif arg.startswith('--source='):
            source = arg.split('=', 1)[1]
            i += 1
            continue

        # CHKT-04: --staged/-S (warning)
        if arg in ('-S', '--staged'):
            staged = True
            i += 1
            continue

        # CHKT-10: -q/--quiet
        if arg in ('-q', '--quiet'):
            quiet = True
            i += 1
            continue

        # CHKT-11: -W/--worktree (default, skip)
        if arg in ('-W', '--worktree'):
            i += 1
            continue

        remaining.append(arg)
        i += 1

    # Warn about staged
    if staged:
        print("Warning: --staged/-S has no effect. "
              "Sapling has no staging area.",
              file=sys.stderr)

    # Build revert command
    revert_args = ['revert']

    if source:
        revert_args.extend(['-r', source])

    revert_args.extend(remaining)

    if quiet:
        # Capture and discard output
        result = subprocess.run(
            ['sl'] + revert_args,
            capture_output=True
        )
        return result.returncode

    return run_sl(revert_args)
