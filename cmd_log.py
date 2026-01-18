"""Handler for 'git log' command."""

import re
from common import ParsedCommand, run_sl


# Template for --oneline format
# Uses sl's {node|short} (12 chars) - semantic match per ROADMAP
ONELINE_TEMPLATE = "{node|short} {desc|firstline}\\n"


def handle(parsed: ParsedCommand) -> int:
    """
    Handle 'git log' command.

    Translations:
    - git log --oneline -> sl log -T '<template>'
    - git log -N -> sl log -l N
    - git log -n N -> sl log -l N
    - git log -nN -> sl log -l N
    - git log --max-count=N -> sl log -l N

    All other arguments pass through unchanged.
    """
    sl_args = ["log"]
    remaining_args = []
    use_oneline = False
    limit = None

    i = 0
    while i < len(parsed.args):
        arg = parsed.args[i]

        # --oneline flag
        if arg == "--oneline":
            use_oneline = True

        # -N format (e.g., -5, -10)
        elif re.match(r'^-(\d+)$', arg):
            limit = arg[1:]

        # -n N format (space between)
        elif arg == "-n":
            if i + 1 < len(parsed.args):
                limit = parsed.args[i + 1]
                i += 1

        # -nN format (attached number)
        elif arg.startswith("-n") and len(arg) > 2 and arg[2:].isdigit():
            limit = arg[2:]

        # --max-count=N format
        elif arg.startswith("--max-count="):
            limit = arg.split("=", 1)[1]

        # Everything else passes through
        else:
            remaining_args.append(arg)

        i += 1

    # Build sl command
    if use_oneline:
        sl_args.extend(["-T", ONELINE_TEMPLATE])

    if limit is not None:
        sl_args.extend(["-l", limit])

    sl_args.extend(remaining_args)

    return run_sl(sl_args)
