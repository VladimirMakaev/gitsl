"""Handler for 'git clone' command.

Supported flags:
- CLON-01: -b/--branch <name> -> -u <name> (update to bookmark)
- CLON-02: --depth <n> -> warning (no effect, Sapling uses lazy fetching)
- CLON-03: --single-branch -> warning (not applicable to Sapling)
- CLON-04: -o/--origin <name> -> warning (Sapling uses 'default' remote)
- CLON-05: -n/--no-checkout -> -U (no update)
- CLON-06: --recursive/--recurse-submodules -> warning (submodules not supported)
- CLON-07: --no-tags -> warning (not applicable to Sapling)
- CLON-08: -q/--quiet -> -q (pass through)
- CLON-09: -v/--verbose -> -v (pass through)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git clone' command.

    Translations:
    - git clone -b <branch> -> sl clone -u <bookmark>
    - git clone -n/--no-checkout -> sl clone -U
    - git clone -q/--quiet -> sl clone -q
    - git clone -v/--verbose -> sl clone -v

    Warnings (unsupported):
    - --depth (no effect in Sapling, uses lazy fetching)
    - --single-branch (not applicable)
    - -o/--origin (Sapling uses 'default')
    - --recursive/--recurse-submodules (no submodules)
    - --no-tags (not applicable)
    """
    sl_args = []
    remaining_args = []

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # CLON-01: -b/--branch <value> -> -u <value>
        if arg in ('-b', '--branch'):
            if i + 1 < len(parsed.args):
                i += 1
                sl_args.extend(['-u', parsed.args[i]])
        elif arg.startswith('--branch='):
            sl_args.extend(['-u', arg.split('=', 1)[1]])

        # CLON-05: -n/--no-checkout -> -U
        elif arg in ('-n', '--no-checkout'):
            sl_args.append('-U')

        # CLON-08: -q/--quiet -> pass through
        elif arg in ('-q', '--quiet'):
            sl_args.append('-q')

        # CLON-09: -v/--verbose -> pass through
        elif arg in ('-v', '--verbose'):
            sl_args.append('-v')

        # CLON-02: --depth (unsupported - no effect in Sapling)
        elif arg == '--depth':
            if i + 1 < len(parsed.args):
                i += 1  # Skip the value
            print("Warning: --depth has no effect in Sapling (uses lazy fetching by default)",
                  file=sys.stderr)
        elif arg.startswith('--depth='):
            print("Warning: --depth has no effect in Sapling (uses lazy fetching by default)",
                  file=sys.stderr)

        # CLON-03: --single-branch (not applicable)
        elif arg == '--single-branch':
            print("Warning: --single-branch not applicable to Sapling", file=sys.stderr)

        # CLON-04: -o/--origin (unsupported - Sapling uses 'default')
        elif arg in ('-o', '--origin'):
            if i + 1 < len(parsed.args):
                i += 1  # Skip the value
            print("Warning: custom remote name not supported. Sapling uses 'default' remote.",
                  file=sys.stderr)
        elif arg.startswith('--origin='):
            print("Warning: custom remote name not supported. Sapling uses 'default' remote.",
                  file=sys.stderr)

        # CLON-06: --recursive/--recurse-submodules (no submodules)
        elif arg in ('--recursive', '--recurse-submodules'):
            print("Warning: submodules not supported by Sapling", file=sys.stderr)

        # CLON-07: --no-tags (not applicable)
        elif arg == '--no-tags':
            print("Warning: --no-tags not applicable to Sapling", file=sys.stderr)

        else:
            remaining_args.append(arg)

        i += 1

    return run_sl(["clone"] + sl_args + remaining_args)
