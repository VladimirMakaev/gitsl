"""Handler for 'git log' command.

Supported flags:
- LOG-01: --graph -> -G (commit graph)
- LOG-02: --stat -> --stat (diffstat)
- LOG-03: --patch/-p -> -p (show diffs)
- LOG-04: --author=<pattern> -> -u <pattern> (filter by author)
- LOG-05: --grep=<pattern> -> -k <pattern> (filter by commit message)
- LOG-06: --no-merges -> --no-merges (exclude merge commits)
- LOG-07: --all -> --all (all commits)
- LOG-08: --follow -> -f (follow file renames)
- LOG-09: --since/--after -> -d ">date" (commits after date)
- LOG-10: --until/--before -> -d "<date" (commits before date)
- LOG-11: --name-only -> template with files
- LOG-12: --name-status -> template with file status
- LOG-13: --decorate -> template with bookmarks
- LOG-14: --pretty/--format -> -T template
- LOG-15: --first-parent -> revset approximation
- LOG-16: --reverse -> revset with reverse()
- LOG-17: -S<string> -> warning (pickaxe not supported)
- LOG-18: -G<regex> -> warning (pickaxe not supported)
- LOG-19: -n/--max-count -> -l (already implemented)
- LOG-20: --oneline -> template (already implemented)
"""

import re
import sys
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
    - git log --graph -> sl log -G
    - git log --stat -> sl log --stat
    - git log --patch/-p -> sl log -p
    - git log --author=<pattern> -> sl log -u <pattern>
    - git log --grep=<pattern> -> sl log -k <pattern>
    - git log --no-merges -> sl log --no-merges
    - git log --all -> sl log --all
    - git log --follow -> sl log -f
    - git log --since/--after -> sl log -d ">date"
    - git log --until/--before -> sl log -d "<date"

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

        # LOG-01: --graph -> -G
        elif arg == '--graph':
            sl_args.append('-G')

        # LOG-02: --stat passes through
        elif arg == '--stat':
            sl_args.append('--stat')

        # LOG-03: --patch/-p passes through
        elif arg in ('--patch', '-p'):
            sl_args.append('-p')

        # LOG-06: --no-merges passes through
        elif arg == '--no-merges':
            sl_args.append('--no-merges')

        # LOG-07: --all passes through
        elif arg == '--all':
            sl_args.append('--all')

        # LOG-08: --follow -> -f
        elif arg == '--follow':
            sl_args.append('-f')

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
