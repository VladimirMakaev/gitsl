"""Handler for 'git config' command.

Supported flags:
- CONF-01: --get -> no special handling (sl config key returns value)
- CONF-02: --unset -> --delete
- CONF-03: --list/-l -> sl config (no args)
- CONF-04: --global -> --user
- CONF-05: --local -> --local (pass through)
- CONF-06: --system -> --system (pass through)
- CONF-07: --show-origin -> --debug
- CONF-08: --all -> warning (multi-valued not supported)
"""

import sys
from common import ParsedCommand, run_sl


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git config' command.

    Translations:
    - git config <key>          -> sl config <key>
    - git config <key> <value>  -> sl config --local <key> <value>
    - git config --list         -> sl config (no args)
    - git config --global       -> sl config --user
    - git config --unset        -> sl config --delete
    - git config --show-origin  -> sl config --debug

    Pass-through:
    - git config --local -> sl config --local
    - git config --system -> sl config --system

    Warnings:
    - --all (multi-valued keys not supported)
    """
    sl_args = []
    remaining_args = []
    is_list = False

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # CONF-03: --list/-l: sl config with no args shows all
        if arg in ('--list', '-l'):
            is_list = True

        # CONF-01: --get: no special handling, just pass key through
        elif arg == '--get':
            pass  # Skip the flag, key will be in remaining_args

        # CONF-02: --unset -> --delete
        elif arg == '--unset':
            sl_args.append('--delete')

        # CONF-04: --global -> --user
        elif arg == '--global':
            sl_args.append('--user')

        # CONF-05: --local: pass through
        elif arg == '--local':
            sl_args.append('--local')

        # CONF-06: --system: pass through
        elif arg == '--system':
            sl_args.append('--system')

        # CONF-07: --show-origin -> --debug
        elif arg == '--show-origin':
            sl_args.append('--debug')

        # CONF-08: --all: warn (multi-valued not supported)
        elif arg == '--all':
            print("Warning: --all (multi-valued key retrieval) not supported by Sapling config",
                  file=sys.stderr)

        else:
            remaining_args.append(arg)

        i += 1

    # Handle list mode
    if is_list:
        return run_sl(["config"] + sl_args)

    # Count positional args (non-flag args)
    positional = [a for a in remaining_args if not a.startswith('-')]

    # If setting a value (key and value present) and no scope specified
    if len(positional) >= 2:
        has_scope = any(a in sl_args for a in ('--user', '--local', '--system'))
        if not has_scope:
            sl_args.append('--local')

    return run_sl(["config"] + sl_args + remaining_args)
