"""Handler for 'git rm' command.

Supported flags:
- RM-01: -f/--force -> -f (pass through)
- RM-02: --cached -> warning (no staging area in Sapling)
- RM-03: -n/--dry-run -> warning (not supported)
- RM-04: -q/--quiet -> -q (pass through)
- RM-05: -r/--recursive -> filtered (sl remove is recursive by default)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git rm' command.

    Translations:
    - git rm <files>   -> sl remove <files>
    - git rm -f        -> sl remove -f
    - git rm -q        -> sl remove -q
    - git rm -r        -> sl remove (recursive by default)

    Warnings:
    - --cached (no staging area, use 'sl forget')
    - -n/--dry-run (not supported)
    """
    sl_args = []
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # RM-01: -f/--force -> pass through
        if arg in ('-f', '--force'):
            sl_args.append('-f')

        # RM-04: -q/--quiet -> pass through
        elif arg in ('-q', '--quiet'):
            sl_args.append('-q')

        # RM-05: -r/--recursive -> filtered (sl remove is recursive by default)
        elif arg in ('-r', '--recursive'):
            pass  # Skip - sl remove is recursive by default

        # RM-02: --cached -> warning (no staging area)
        elif arg == '--cached':
            print("Warning: --cached not supported. Sapling has no staging area. "
                  "Use 'sl forget' to untrack files.", file=sys.stderr)

        # RM-03: -n/--dry-run -> warning (not supported)
        elif arg in ('-n', '--dry-run'):
            print("Warning: -n/--dry-run not supported by Sapling remove. "
                  "Use 'sl status' to see tracked files.", file=sys.stderr)

        else:
            remaining_args.append(arg)

        i += 1

    return run_sl(["remove"] + sl_args + remaining_args)
