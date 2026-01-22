"""Handler for 'git mv' command.

Supported flags:
- MV-01: -f/--force -> -f (pass through)
- MV-02: -k -> warning (skip errors not supported)
- MV-03: -v/--verbose -> -v (pass through)
- MV-04: -n/--dry-run -> -n (pass through)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git mv' command.

    Translations:
    - git mv <src> <dst> -> sl rename <src> <dst>
    - git mv -f          -> sl rename -f
    - git mv -n          -> sl rename -n
    - git mv -v          -> sl rename -v

    Warnings:
    - -k (skip errors not supported)
    """
    sl_args = []
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # MV-01: -f/--force -> pass through
        if arg in ('-f', '--force'):
            sl_args.append('-f')

        # MV-04: -n/--dry-run -> pass through
        elif arg in ('-n', '--dry-run'):
            sl_args.append('-n')

        # MV-03: -v/--verbose -> pass through
        elif arg in ('-v', '--verbose'):
            sl_args.append('-v')

        # MV-02: -k -> warning (skip errors not supported)
        elif arg == '-k':
            print("Warning: -k (skip errors) not supported by Sapling rename", file=sys.stderr)

        else:
            remaining_args.append(arg)

        i += 1

    return run_sl(["rename"] + sl_args + remaining_args)
